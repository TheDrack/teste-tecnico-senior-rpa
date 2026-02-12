"""
RabbitMQ connection and queue management.

Este módulo gerencia a comunicação com RabbitMQ, incluindo:
- Conexão com o servidor
- Declaração de filas
- Publicação de mensagens
- Consumo de mensagens

Usa a biblioteca pika para interagir com RabbitMQ.
"""

from typing import Optional, Callable, Any
import json
import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from app.core.config import settings


class RabbitMQConnection:
    """
    Gerenciador de conexão com RabbitMQ.

    Encapsula a lógica de conexão, publicação e consumo de mensagens.

    Attributes:
        connection: Conexão ativa com RabbitMQ
        channel: Canal de comunicação

    Example:
        >>> rabbitmq = RabbitMQConnection()
        >>> rabbitmq.connect()
        >>> rabbitmq.publish_message("queue_name", {"job_id": 1})
        >>> rabbitmq.close()
    """

    def __init__(self) -> None:
        """Inicializa o gerenciador sem conexão ativa."""
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[BlockingChannel] = None

    def connect(self) -> None:
        """
        Estabelece conexão com RabbitMQ.

        Cria conexão e canal, configurando credenciais e host
        a partir das configurações da aplicação.

        Raises:
            pika.exceptions.AMQPConnectionError: Se falhar ao conectar

        Example:
            >>> rabbitmq = RabbitMQConnection()
            >>> rabbitmq.connect()
        """
        # Configurar credenciais
        credentials = pika.PlainCredentials(
            username=settings.rabbitmq_user, password=settings.rabbitmq_password
        )

        # Configurar parâmetros de conexão
        parameters = pika.ConnectionParameters(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            credentials=credentials,
            heartbeat=600,  # Heartbeat a cada 10 minutos
            blocked_connection_timeout=300,  # Timeout de 5 minutos
        )

        # Estabelecer conexão
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def declare_queue(self, queue_name: str, durable: bool = True) -> None:
        """
        Declara uma fila no RabbitMQ.

        Se a fila já existir, esta operação é idempotente.

        Args:
            queue_name: Nome da fila a ser criada
            durable: Se True, a fila sobrevive a reinicializações do broker

        Raises:
            ValueError: Se não houver conexão ativa

        Example:
            >>> rabbitmq = RabbitMQConnection()
            >>> rabbitmq.connect()
            >>> rabbitmq.declare_queue("my_queue")
        """
        if not self.channel:
            raise ValueError("Não há conexão ativa. Execute connect() primeiro.")

        self.channel.queue_declare(queue=queue_name, durable=durable)

    def publish_message(
        self, queue_name: str, message: dict[str, Any], persistent: bool = True
    ) -> None:
        """
        Publica uma mensagem em uma fila.

        A mensagem é serializada para JSON antes de ser enviada.

        Args:
            queue_name: Nome da fila de destino
            message: Dicionário com os dados da mensagem
            persistent: Se True, mensagem sobrevive a reinicializações

        Raises:
            ValueError: Se não houver conexão ativa

        Example:
            >>> rabbitmq = RabbitMQConnection()
            >>> rabbitmq.connect()
            >>> rabbitmq.publish_message("jobs", {"job_id": 1, "type": "hockey"})
        """
        if not self.channel:
            raise ValueError("Não há conexão ativa. Execute connect() primeiro.")

        # Serializar mensagem para JSON
        message_body = json.dumps(message)

        # Configurar propriedades da mensagem
        properties = BasicProperties(
            delivery_mode=2 if persistent else 1,  # 2 = persistent
            content_type="application/json",
        )

        # Publicar mensagem
        self.channel.basic_publish(
            exchange="",  # Exchange padrão
            routing_key=queue_name,
            body=message_body,
            properties=properties,
        )

    def consume_messages(
        self,
        queue_name: str,
        callback: Callable[
            [BlockingChannel, Basic.Deliver, BasicProperties, bytes], None
        ],
        auto_ack: bool = False,
    ) -> None:
        """
        Inicia consumo de mensagens de uma fila.

        Esta função bloqueia a execução e processa mensagens
        conforme elas chegam na fila.

        Args:
            queue_name: Nome da fila para consumir
            callback: Função a ser chamada para cada mensagem
            auto_ack: Se True, reconhece mensagens automaticamente

        Raises:
            ValueError: Se não houver conexão ativa

        Example:
            >>> def process_message(ch, method, properties, body):
            >>>     print(f"Recebido: {body}")
            >>>     ch.basic_ack(delivery_tag=method.delivery_tag)
            >>>
            >>> rabbitmq = RabbitMQConnection()
            >>> rabbitmq.connect()
            >>> rabbitmq.consume_messages("jobs", process_message)
        """
        if not self.channel:
            raise ValueError("Não há conexão ativa. Execute connect() primeiro.")

        # Configurar consumo
        self.channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=auto_ack
        )

        # Iniciar consumo (bloqueia execução)
        print(f"[*] Aguardando mensagens na fila '{queue_name}'. CTRL+C para sair.")
        self.channel.start_consuming()

    def close(self) -> None:
        """
        Fecha a conexão com RabbitMQ.

        Deve ser chamado ao finalizar o uso da conexão
        para liberar recursos.

        Example:
            >>> rabbitmq = RabbitMQConnection()
            >>> rabbitmq.connect()
            >>> # ... usar conexão ...
            >>> rabbitmq.close()
        """
        if self.connection and not self.connection.is_closed:
            self.connection.close()


def get_rabbitmq_connection() -> RabbitMQConnection:
    """
    Factory function para criar uma nova conexão RabbitMQ.

    Returns:
        RabbitMQConnection: Nova instância de conexão

    Example:
        >>> rabbitmq = get_rabbitmq_connection()
        >>> rabbitmq.connect()
    """
    return RabbitMQConnection()
