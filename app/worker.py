"""
RabbitMQ consumer worker.

Este módulo implementa o worker que consome mensagens de RabbitMQ
e executa os scrapers apropriados, salvando os resultados no banco de dados.

O worker:
1. Conecta ao RabbitMQ e escuta as filas
2. Recebe mensagens com job_id e tipo de scraping
3. Executa o scraper correspondente
4. Salva os dados no PostgreSQL
5. Atualiza o status do job
"""
from typing import Dict, Any
import json
import traceback
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from sqlalchemy.orm import Session

from app.core.rabbitmq import RabbitMQConnection
from app.core.database import SessionLocal
from app.core.config import settings
from app.models import Job, JobStatus, JobType, HockeyData, OscarData
from app.static_scraper.hockey import scrape_hockey_data
from app.dynamic_scraper.oscar import scrape_oscar_data


class ScraperWorker:
    """
    Worker que processa jobs de scraping.
    
    Consome mensagens de RabbitMQ e executa scrapers,
    salvando resultados no banco de dados.
    
    Attributes:
        rabbitmq: Conexão com RabbitMQ
        db_session: Sessão do banco de dados
        
    Example:
        >>> worker = ScraperWorker()
        >>> worker.start()  # Inicia consumo (bloqueia execução)
    """
    
    def __init__(self) -> None:
        """Inicializa o worker (sem conexões ativas)."""
        self.rabbitmq: RabbitMQConnection = RabbitMQConnection()
    
    def start(self) -> None:
        """
        Inicia o worker e começa a consumir mensagens.
        
        Esta função bloqueia a execução e processa mensagens
        conforme elas chegam nas filas configuradas.
        
        Example:
            >>> worker = ScraperWorker()
            >>> worker.start()  # Bloqueia aqui
        """
        print("[Worker] Iniciando worker de scraping...")
        
        # Conectar ao RabbitMQ
        self.rabbitmq.connect()
        
        # Declarar filas (idempotente)
        self.rabbitmq.declare_queue(settings.rabbitmq_queue_hockey)
        self.rabbitmq.declare_queue(settings.rabbitmq_queue_oscar)
        
        print(f"[Worker] Escutando filas:")
        print(f"  - {settings.rabbitmq_queue_hockey}")
        print(f"  - {settings.rabbitmq_queue_oscar}")
        
        # PREENCHER: Se precisar consumir de múltiplas filas simultaneamente,
        # pode ser necessário usar threads ou multiprocessing
        
        # Por simplicidade, consumir de uma fila por vez
        # Ou implementar lógica para consumir de ambas
        
        # Exemplo: consumir apenas de hockey (ADAPTAR conforme necessário)
        self._consume_from_queues()
    
    def _consume_from_queues(self) -> None:
        """
        Configura consumo de múltiplas filas.
        
        Para processar múltiplas filas, registra callbacks para cada uma.
        """
        # Configurar callback para fila de Hockey
        self.rabbitmq.channel.basic_consume(
            queue=settings.rabbitmq_queue_hockey,
            on_message_callback=self._process_hockey_message,
            auto_ack=False
        )
        
        # Configurar callback para fila de Oscar
        self.rabbitmq.channel.basic_consume(
            queue=settings.rabbitmq_queue_oscar,
            on_message_callback=self._process_oscar_message,
            auto_ack=False
        )
        
        # Iniciar consumo
        print("[Worker] Aguardando mensagens...")
        self.rabbitmq.channel.start_consuming()
    
    def _process_hockey_message(
        self,
        channel: BlockingChannel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes
    ) -> None:
        """
        Processa mensagem de scraping de Hockey.
        
        Args:
            channel: Canal RabbitMQ
            method: Metadados da entrega
            properties: Propriedades da mensagem
            body: Corpo da mensagem (JSON)
        """
        print(f"[Worker] Recebida mensagem de Hockey: {body}")
        
        try:
            # Parsear mensagem JSON
            message = json.loads(body)
            job_id = message.get("job_id")
            
            if not job_id:
                print("[Worker] Mensagem sem job_id, ignorando")
                channel.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            # Processar job
            self._process_hockey_job(job_id)
            
            # Confirmar processamento
            channel.basic_ack(delivery_tag=method.delivery_tag)
            print(f"[Worker] Job {job_id} (Hockey) processado com sucesso")
            
        except Exception as e:
            print(f"[Worker] Erro ao processar mensagem de Hockey: {e}")
            traceback.print_exc()
            # PREENCHER: Decidir estratégia de retry ou dead-letter queue
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def _process_oscar_message(
        self,
        channel: BlockingChannel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes
    ) -> None:
        """
        Processa mensagem de scraping de Oscar.
        
        Args:
            channel: Canal RabbitMQ
            method: Metadados da entrega
            properties: Propriedades da mensagem
            body: Corpo da mensagem (JSON)
        """
        print(f"[Worker] Recebida mensagem de Oscar: {body}")
        
        try:
            # Parsear mensagem JSON
            message = json.loads(body)
            job_id = message.get("job_id")
            
            if not job_id:
                print("[Worker] Mensagem sem job_id, ignorando")
                channel.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            # Processar job
            self._process_oscar_job(job_id)
            
            # Confirmar processamento
            channel.basic_ack(delivery_tag=method.delivery_tag)
            print(f"[Worker] Job {job_id} (Oscar) processado com sucesso")
            
        except Exception as e:
            print(f"[Worker] Erro ao processar mensagem de Oscar: {e}")
            traceback.print_exc()
            # PREENCHER: Decidir estratégia de retry ou dead-letter queue
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def _process_hockey_job(self, job_id: int) -> None:
        """
        Executa scraping de Hockey e salva no banco.
        
        Args:
            job_id: ID do job a processar
        """
        db: Session = SessionLocal()
        
        try:
            # Buscar job no banco
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                print(f"[Worker] Job {job_id} não encontrado no banco")
                return
            
            # Atualizar status para RUNNING
            job.status = JobStatus.RUNNING
            db.commit()
            
            # Executar scraping
            print(f"[Worker] Executando scraping de Hockey para job {job_id}...")
            hockey_data_list = scrape_hockey_data()
            
            # Salvar dados no banco
            for data_dict in hockey_data_list:
                hockey_data = HockeyData(
                    job_id=job_id,
                    **data_dict
                )
                db.add(hockey_data)
            
            # Atualizar status para COMPLETED
            job.status = JobStatus.COMPLETED
            db.commit()
            
            print(f"[Worker] Job {job_id} concluído. Salvos {len(hockey_data_list)} registros.")
            
        except Exception as e:
            # Atualizar status para FAILED
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            db.commit()
            print(f"[Worker] Job {job_id} falhou: {e}")
            raise
        finally:
            db.close()
    
    def _process_oscar_job(self, job_id: int) -> None:
        """
        Executa scraping de Oscar e salva no banco.
        
        Args:
            job_id: ID do job a processar
        """
        db: Session = SessionLocal()
        
        try:
            # Buscar job no banco
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                print(f"[Worker] Job {job_id} não encontrado no banco")
                return
            
            # Atualizar status para RUNNING
            job.status = JobStatus.RUNNING
            db.commit()
            
            # Executar scraping
            print(f"[Worker] Executando scraping de Oscar para job {job_id}...")
            oscar_data_list = scrape_oscar_data()
            
            # Salvar dados no banco
            for data_dict in oscar_data_list:
                oscar_data = OscarData(
                    job_id=job_id,
                    **data_dict
                )
                db.add(oscar_data)
            
            # Atualizar status para COMPLETED
            job.status = JobStatus.COMPLETED
            db.commit()
            
            print(f"[Worker] Job {job_id} concluído. Salvos {len(oscar_data_list)} registros.")
            
        except Exception as e:
            # Atualizar status para FAILED
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            db.commit()
            print(f"[Worker] Job {job_id} falhou: {e}")
            raise
        finally:
            db.close()
    
    def stop(self) -> None:
        """
        Para o worker e fecha conexões.
        
        Example:
            >>> worker = ScraperWorker()
            >>> # ... em outro thread/signal handler ...
            >>> worker.stop()
        """
        print("[Worker] Parando worker...")
        if self.rabbitmq.channel:
            self.rabbitmq.channel.stop_consuming()
        self.rabbitmq.close()


def main() -> None:
    """
    Função principal para executar o worker.
    
    Cria e inicia um worker de scraping.
    
    Example:
        >>> python -m app.worker
    """
    worker = ScraperWorker()
    try:
        worker.start()
    except KeyboardInterrupt:
        print("\n[Worker] Recebido sinal de interrupção")
        worker.stop()
    except Exception as e:
        print(f"[Worker] Erro fatal: {e}")
        traceback.print_exc()
        worker.stop()


if __name__ == "__main__":
    main()
