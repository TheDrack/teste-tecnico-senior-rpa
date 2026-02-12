"""
Application configuration using Pydantic Settings.

Este módulo centraliza todas as configurações da aplicação,
incluindo conexões com banco de dados, RabbitMQ e configurações gerais.

As configurações são carregadas de variáveis de ambiente (.env)
usando Pydantic Settings para validação e type hints.
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn


class Settings(BaseSettings):
    """
    Configurações principais da aplicação.
    
    Todas as configurações são carregadas de variáveis de ambiente.
    Valores com 'PREENCHER' devem ser substituídos no arquivo .env
    
    Attributes:
        app_name: Nome da aplicação
        debug: Modo debug (development/production)
        api_prefix: Prefixo das rotas da API
        
        database_url: URL de conexão com PostgreSQL
        database_pool_size: Tamanho do pool de conexões
        database_max_overflow: Máximo de conexões extras
        
        rabbitmq_host: Host do RabbitMQ
        rabbitmq_port: Porta do RabbitMQ
        rabbitmq_user: Usuário do RabbitMQ
        rabbitmq_password: Senha do RabbitMQ
        rabbitmq_queue_hockey: Nome da fila para jobs de Hockey
        rabbitmq_queue_oscar: Nome da fila para jobs de Oscar
        
        selenium_headless: Executar Selenium em modo headless
        selenium_timeout: Timeout padrão para operações Selenium
        scraper_user_agent: User agent para requests HTTP
        scraper_delay: Delay entre requests (segundos)
    """
    
    # Configurações da Aplicação
    app_name: str = Field(
        default="RPA Scraping System",
        description="Nome da aplicação"
    )
    debug: bool = Field(
        default=False,
        description="Modo debug (True para development)"
    )
    api_prefix: str = Field(
        default="/api/v1",
        description="Prefixo das rotas da API"
    )
    
    # Configurações do Banco de Dados PostgreSQL
    # PREENCHER: Configurar URL do banco de dados no .env
    database_url: str = Field(
        default="postgresql://PREENCHER_USER:PREENCHER_PASSWORD@PREENCHER_HOST:5432/PREENCHER_DB",
        description="URL de conexão com PostgreSQL"
    )
    database_pool_size: int = Field(
        default=5,
        description="Tamanho do pool de conexões"
    )
    database_max_overflow: int = Field(
        default=10,
        description="Número máximo de conexões extras"
    )
    
    # Configurações do RabbitMQ
    # PREENCHER: Configurar credenciais do RabbitMQ no .env
    rabbitmq_host: str = Field(
        default="PREENCHER_HOST",
        description="Host do servidor RabbitMQ"
    )
    rabbitmq_port: int = Field(
        default=5672,
        description="Porta do RabbitMQ"
    )
    rabbitmq_user: str = Field(
        default="PREENCHER_USER",
        description="Usuário do RabbitMQ"
    )
    rabbitmq_password: str = Field(
        default="PREENCHER_PASSWORD",
        description="Senha do RabbitMQ"
    )
    rabbitmq_queue_hockey: str = Field(
        default="scraper_hockey_queue",
        description="Nome da fila para jobs de Hockey"
    )
    rabbitmq_queue_oscar: str = Field(
        default="scraper_oscar_queue",
        description="Nome da fila para jobs de Oscar"
    )
    
    # Configurações dos Scrapers
    selenium_headless: bool = Field(
        default=True,
        description="Executar Selenium sem interface gráfica"
    )
    selenium_timeout: int = Field(
        default=30,
        description="Timeout padrão para operações Selenium (segundos)"
    )
    scraper_user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        description="User agent para requests HTTP"
    )
    scraper_delay: float = Field(
        default=1.0,
        description="Delay entre requests (segundos) para evitar sobrecarga"
    )
    
    # PREENCHER: URLs dos sites a fazer scraping (valores exemplo)
    hockey_url: str = Field(
        default="https://PREENCHER_URL_HOCKEY",
        description="URL do site de dados de Hockey"
    )
    oscar_url: str = Field(
        default="https://PREENCHER_URL_OSCAR",
        description="URL do site de dados de Oscar"
    )
    
    class Config:
        """Configuração do Pydantic Settings."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instância global de configurações
# Será carregada automaticamente do arquivo .env
settings = Settings()
