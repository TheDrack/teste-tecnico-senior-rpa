"""
Database connection and session management.

Este módulo gerencia a conexão com PostgreSQL usando SQLAlchemy,
incluindo criação de engine, sessões e gerenciamento de transações.

A configuração é obtida do módulo config.py que carrega do .env
"""

from typing import Generator
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.core.config import settings


# Base class para todos os modelos SQLAlchemy
# Todos os models devem herdar desta classe
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def create_db_engine() -> Engine:
    """
    Cria e retorna o engine do SQLAlchemy.

    O engine é configurado com:
    - Pool de conexões para melhor performance
    - Echo SQL quando em modo debug

    Returns:
        Engine: Engine do SQLAlchemy configurado

    Example:
        >>> engine = create_db_engine()
        >>> # Use o engine para criar sessões ou operações diretas
    """
    engine = create_engine(
        settings.database_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        echo=settings.debug,  # Log SQL queries em modo debug
        pool_pre_ping=True,  # Verifica conexão antes de usar
    )
    return engine


# Engine global da aplicação
engine = create_db_engine()


# Session factory - cria novas sessões de banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency que fornece uma sessão de banco de dados.

    Esta função é usada como dependency do FastAPI para injetar
    uma sessão de banco em cada request. A sessão é automaticamente
    fechada após o uso.

    Yields:
        Session: Sessão do SQLAlchemy

    Example:
        >>> from fastapi import Depends
        >>> @app.get("/items/")
        >>> def get_items(db: Session = Depends(get_db)):
        >>>     return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa o banco de dados criando todas as tabelas.

    Esta função deve ser chamada na inicialização da aplicação
    para garantir que todas as tabelas existam.

    NOTA: Em produção, use Alembic para migrations ao invés desta função.

    Example:
        >>> init_db()
        >>> # Todas as tabelas foram criadas
    """
    # Importar todos os models aqui para que sejam registrados no Base
    from app import models  # noqa: F401

    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    Remove todas as tabelas do banco de dados.

    ATENÇÃO: Esta função é destrutiva e deve ser usada apenas
    em ambientes de desenvolvimento/testes.

    Example:
        >>> drop_db()
        >>> # Todas as tabelas foram removidas
    """
    Base.metadata.drop_all(bind=engine)
