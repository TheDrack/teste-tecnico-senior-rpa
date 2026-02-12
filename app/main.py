"""
FastAPI main application.

Este módulo define a API REST para gerenciamento de jobs de scraping.
Endpoints disponíveis:
- POST /crawl/hockey - Agendar scraping de Hockey
- POST /crawl/oscar - Agendar scraping de Oscar  
- POST /crawl/all - Agendar ambos scrapers
- GET /jobs - Listar todos os jobs
- GET /jobs/{job_id} - Detalhes de um job
- GET /jobs/{job_id}/results - Resultados de um job
- GET /results/hockey - Todos os dados de Hockey
- GET /results/oscar - Todos os dados de Oscar

A API é assíncrona e usa RabbitMQ para processamento em background.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db, init_db
from app.core.rabbitmq import get_rabbitmq_connection
from app.core.config import settings
from app.models import Job, JobStatus, JobType, HockeyData, OscarData
from app.schemas import (
    JobResponse,
    JobListResponse,
    CrawlResponse,
    JobResultsResponse,
    HockeyDataResponse,
    HockeyDataListResponse,
    OscarDataResponse,
    OscarDataListResponse,
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gerencia o ciclo de vida da aplicação.
    
    Executa setup na inicialização e cleanup no encerramento.
    """
    # Startup
    logger.info("Inicializando aplicação...")
    try:
        init_db()
        logger.info("Banco de dados inicializado")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
    
    logger.info("Aplicação inicializada com sucesso")
    
    yield
    
    # Shutdown
    logger.info("Encerrando aplicação...")


# Inicializar aplicação FastAPI
app = FastAPI(
    title="RPA Scraping System",
    description="Sistema de coleta de dados de múltiplas fontes web com gerenciamento de jobs através de filas de mensagens",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.get("/", tags=["Health"])
async def root() -> dict:
    """
    Endpoint raiz - Health check.

    Returns:
        dict: Informações básicas da API

    Example:
        >>> GET /
        >>> {"message": "RPA Scraping System API", "version": "1.0.0"}
    """
    return {
        "message": "RPA Scraping System API",
        "version": "1.0.0",
        "status": "running",
    }


# ==================== Crawl Endpoints ====================


def _publish_to_rabbitmq(queue_name: str, job_id: int, job_type: str) -> None:
    """
    Helper para publicar mensagens no RabbitMQ.
    
    Args:
        queue_name: Nome da fila
        job_id: ID do job
        job_type: Tipo do job (hockey, oscar)
        
    Raises:
        Exception: Se falhar ao publicar mensagem
    """
    rabbitmq = get_rabbitmq_connection()
    try:
        rabbitmq.connect()
        rabbitmq.declare_queue(queue_name)
        rabbitmq.publish_message(queue_name, {"job_id": job_id, "type": job_type})
    finally:
        rabbitmq.close()


def _schedule_crawl_job(
    db: Session, job_type: JobType, queue_name: str, type_name: str, message_suffix: str
) -> CrawlResponse:
    """
    Helper genérico para agendar jobs de scraping.
    
    Args:
        db: Sessão do banco de dados
        job_type: Tipo do job (JobType enum)
        queue_name: Nome da fila RabbitMQ
        type_name: Nome do tipo para a mensagem
        message_suffix: Sufixo para mensagem de sucesso
        
    Returns:
        CrawlResponse: Informações do job criado
        
    Raises:
        HTTPException: Se falhar ao criar job ou publicar mensagem
    """
    # Criar job no banco
    job = Job(type=job_type, status=JobStatus.PENDING)
    db.add(job)
    db.commit()
    db.refresh(job)

    # Publicar mensagem no RabbitMQ
    try:
        _publish_to_rabbitmq(queue_name, job.id, type_name)
    except Exception as e:
        # Se falhar ao publicar, marcar job como failed
        job.status = JobStatus.FAILED
        job.error_message = f"Falha ao publicar mensagem: {str(e)}"
        db.commit()
        logger.error(f"Erro ao agendar job {job.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao agendar job: {str(e)}",
        )

    logger.info(f"Job {job.id} ({job_type}) agendado com sucesso")
    return CrawlResponse(
        job_id=job.id,
        message=f"Job de scraping {message_suffix} agendado com sucesso",
        status=job.status,
    )


@app.post(
    "/crawl/hockey",
    response_model=CrawlResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Scraping"],
    summary="Agendar scraping de Hockey",
)
async def crawl_hockey(db: Session = Depends(get_db)) -> CrawlResponse:
    """
    Agenda um job de scraping de dados de Hockey.

    O job é criado no banco e uma mensagem é publicada no RabbitMQ
    para processamento assíncrono por um worker.

    Args:
        db: Sessão do banco de dados (injetada)

    Returns:
        CrawlResponse: Informações do job criado

    Raises:
        HTTPException: Se falhar ao criar job ou publicar mensagem

    Example:
        >>> POST /crawl/hockey
        >>> {
        >>>   "job_id": 1,
        >>>   "message": "Job de scraping de Hockey agendado com sucesso",
        >>>   "status": "pending"
        >>> }
    """
    return _schedule_crawl_job(
        db, JobType.HOCKEY, settings.rabbitmq_queue_hockey, "hockey", "de Hockey"
    )


@app.post(
    "/crawl/oscar",
    response_model=CrawlResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Scraping"],
    summary="Agendar scraping de Oscar",
)
async def crawl_oscar(db: Session = Depends(get_db)) -> CrawlResponse:
    """
    Agenda um job de scraping de dados de Oscar.

    O job é criado no banco e uma mensagem é publicada no RabbitMQ
    para processamento assíncrono por um worker.

    Args:
        db: Sessão do banco de dados (injetada)

    Returns:
        CrawlResponse: Informações do job criado

    Example:
        >>> POST /crawl/oscar
        >>> {
        >>>   "job_id": 2,
        >>>   "message": "Job de scraping de Oscar agendado com sucesso",
        >>>   "status": "pending"
        >>> }
    """
    return _schedule_crawl_job(
        db, JobType.OSCAR, settings.rabbitmq_queue_oscar, "oscar", "de Oscar"
    )

@app.post(
    "/crawl/all",
    response_model=CrawlResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Scraping"],
    summary="Agendar scraping de Hockey e Oscar",
)
async def crawl_all(db: Session = Depends(get_db)) -> CrawlResponse:
    """
    Agenda jobs de scraping para Hockey E Oscar.

    Cria um job do tipo "all" e publica mensagens em ambas as filas.

    Args:
        db: Sessão do banco de dados (injetada)

    Returns:
        CrawlResponse: Informações do job criado

    Example:
        >>> POST /crawl/all
        >>> {
        >>>   "job_id": 3,
        >>>   "message": "Jobs de scraping agendados com sucesso",
        >>>   "status": "pending"
        >>> }
    """
    # Criar job no banco
    job = Job(type=JobType.ALL, status=JobStatus.PENDING)
    db.add(job)
    db.commit()
    db.refresh(job)

    # Publicar mensagens em ambas as filas
    try:
        _publish_to_rabbitmq(settings.rabbitmq_queue_hockey, job.id, "hockey")
        _publish_to_rabbitmq(settings.rabbitmq_queue_oscar, job.id, "oscar")
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = f"Falha ao publicar mensagens: {str(e)}"
        db.commit()
        logger.error(f"Erro ao agendar jobs {job.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao agendar jobs: {str(e)}",
        )

    logger.info(f"Job {job.id} (all) agendado com sucesso")
    return CrawlResponse(
        job_id=job.id,
        message="Jobs de scraping agendados com sucesso",
        status=job.status,
    )


# ==================== Job Management Endpoints ====================


@app.get(
    "/jobs",
    response_model=JobListResponse,
    tags=["Jobs"],
    summary="Listar todos os jobs",
)
async def list_jobs(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> JobListResponse:
    """
    Lista todos os jobs de scraping.

    Args:
        skip: Número de registros a pular (paginação)
        limit: Número máximo de registros a retornar
        db: Sessão do banco de dados (injetada)

    Returns:
        JobListResponse: Lista de jobs com total

    Example:
        >>> GET /jobs?skip=0&limit=10
        >>> {
        >>>   "total": 5,
        >>>   "jobs": [...]
        >>> }
    """
    total = db.query(Job).count()
    jobs = db.query(Job).order_by(Job.created_at.desc()).offset(skip).limit(limit).all()

    return JobListResponse(
        total=total, jobs=[JobResponse.model_validate(job) for job in jobs]
    )


@app.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
    tags=["Jobs"],
    summary="Obter detalhes de um job",
)
async def get_job(job_id: int, db: Session = Depends(get_db)) -> JobResponse:
    """
    Obtém detalhes de um job específico.

    Args:
        job_id: ID do job
        db: Sessão do banco de dados (injetada)

    Returns:
        JobResponse: Informações do job

    Raises:
        HTTPException: Se job não encontrado

    Example:
        >>> GET /jobs/1
        >>> {
        >>>   "id": 1,
        >>>   "type": "hockey",
        >>>   "status": "completed",
        >>>   ...
        >>> }
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} não encontrado"
        )

    return JobResponse.model_validate(job)


@app.get(
    "/jobs/{job_id}/results",
    response_model=JobResultsResponse,
    tags=["Jobs"],
    summary="Obter resultados de um job",
)
async def get_job_results(
    job_id: int, db: Session = Depends(get_db)
) -> JobResultsResponse:
    """
    Obtém os resultados coletados por um job.

    Args:
        job_id: ID do job
        db: Sessão do banco de dados (injetada)

    Returns:
        JobResultsResponse: Job e dados coletados

    Raises:
        HTTPException: Se job não encontrado

    Example:
        >>> GET /jobs/1/results
        >>> {
        >>>   "job": {...},
        >>>   "hockey_data": [...],
        >>>   "oscar_data": []
        >>> }
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} não encontrado"
        )

    # Buscar dados de hockey e oscar relacionados
    hockey_data = db.query(HockeyData).filter(HockeyData.job_id == job_id).all()
    oscar_data = db.query(OscarData).filter(OscarData.job_id == job_id).all()

    return JobResultsResponse(
        job=JobResponse.model_validate(job),
        hockey_data=[HockeyDataResponse.model_validate(d) for d in hockey_data],
        oscar_data=[OscarDataResponse.model_validate(d) for d in oscar_data],
    )


# ==================== Results Endpoints ====================


@app.get(
    "/results/hockey",
    response_model=HockeyDataListResponse,
    tags=["Results"],
    summary="Listar todos os dados de Hockey",
)
async def get_all_hockey_data(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> HockeyDataListResponse:
    """
    Lista todos os dados de Hockey coletados.

    Args:
        skip: Número de registros a pular
        limit: Número máximo de registros
        db: Sessão do banco de dados (injetada)

    Returns:
        HockeyDataListResponse: Lista de dados com total
    """
    total = db.query(HockeyData).count()
    data = (
        db.query(HockeyData)
        .order_by(HockeyData.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return HockeyDataListResponse(
        total=total, data=[HockeyDataResponse.model_validate(d) for d in data]
    )


@app.get(
    "/results/oscar",
    response_model=OscarDataListResponse,
    tags=["Results"],
    summary="Listar todos os dados de Oscar",
)
async def get_all_oscar_data(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> OscarDataListResponse:
    """
    Lista todos os dados de Oscar coletados.

    Args:
        skip: Número de registros a pular
        limit: Número máximo de registros
        db: Sessão do banco de dados (injetada)

    Returns:
        OscarDataListResponse: Lista de dados com total
    """
    total = db.query(OscarData).count()
    data = (
        db.query(OscarData)
        .order_by(OscarData.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return OscarDataListResponse(
        total=total, data=[OscarDataResponse.model_validate(d) for d in data]
    )
