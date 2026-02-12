"""
Pydantic schemas for request/response validation.

Este módulo define os schemas Pydantic para validação de dados
de entrada e saída da API, garantindo type safety e validação automática.

Schemas incluem:
- Job: Criação e resposta de jobs
- HockeyData: Resposta de dados de Hockey
- OscarData: Resposta de dados de Oscar
- Crawl: Request e Response para endpoints de scraping
"""
from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ==================== Job Schemas ====================

class JobCreate(BaseModel):
    """
    Schema para criação de um novo Job.
    
    Attributes:
        type: Tipo do job (hockey, oscar, all)
        
    Example:
        >>> job = JobCreate(type="hockey")
    """
    type: Literal["hockey", "oscar", "all"] = Field(
        ...,
        description="Tipo do job de scraping"
    )


class JobResponse(BaseModel):
    """
    Schema de resposta com informações de um Job.
    
    Attributes:
        id: ID único do job
        type: Tipo do job
        status: Status atual (pending, running, completed, failed)
        created_at: Data/hora de criação
        updated_at: Data/hora da última atualização
        error_message: Mensagem de erro (se houver)
        
    Example:
        >>> job = JobResponse(
        >>>     id=1,
        >>>     type="hockey",
        >>>     status="completed",
        >>>     created_at=datetime.now(),
        >>>     updated_at=datetime.now()
        >>> )
    """
    id: int
    type: str
    status: Literal["pending", "running", "completed", "failed"]
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class JobListResponse(BaseModel):
    """
    Schema de resposta para lista de Jobs.
    
    Attributes:
        total: Total de jobs
        jobs: Lista de jobs
        
    Example:
        >>> response = JobListResponse(total=10, jobs=[...])
    """
    total: int
    jobs: List[JobResponse]


# ==================== HockeyData Schemas ====================

class HockeyDataResponse(BaseModel):
    """
    Schema de resposta para dados de Hockey.
    
    Attributes:
        id: ID único do registro
        job_id: ID do job que coletou este dado
        team_name: Nome do time
        year: Ano da temporada
        wins: Vitórias
        losses: Derrotas
        ot_losses: Derrotas na prorrogação
        win_pct: Percentual de vitórias (0.0 a 1.0)
        gf: Goals For (gols marcados)
        ga: Goals Against (gols sofridos)
        diff: Diferença de gols
        
    Example:
        >>> data = HockeyDataResponse(
        >>>     id=1, job_id=1,
        >>>     team_name="Boston Bruins",
        >>>     year=1990, wins=44, losses=24, ot_losses=0,
        >>>     win_pct=0.550, gf=299, ga=264, diff=35
        >>> )
    """
    id: int
    job_id: int
    team_name: str = Field(..., min_length=1, max_length=200)
    year: int = Field(..., ge=1900, le=2100)
    wins: int = Field(..., ge=0)
    losses: int = Field(..., ge=0)
    ot_losses: int = Field(..., ge=0)
    win_pct: Optional[float] = Field(None, ge=0.0, le=1.0)
    gf: Optional[int] = Field(None, ge=0)  # Goals For
    ga: Optional[int] = Field(None, ge=0)  # Goals Against
    diff: Optional[int] = None  # Goal Difference (pode ser negativo)
    
    model_config = ConfigDict(from_attributes=True)


class HockeyDataListResponse(BaseModel):
    """
    Schema de resposta para lista de dados de Hockey.
    
    Attributes:
        total: Total de registros
        data: Lista de dados
    """
    total: int
    data: List[HockeyDataResponse]


# ==================== OscarData Schemas ====================

class OscarDataResponse(BaseModel):
    """
    Schema de resposta para dados de Oscar.
    
    Attributes:
        id: ID único do registro
        job_id: ID do job que coletou este dado
        year: Ano da premiação
        title: Título do filme
        nominations: Número de indicações
        awards: Número de prêmios ganhos
        best_picture: Se ganhou Melhor Filme
        
    Example:
        >>> data = OscarDataResponse(
        >>>     id=1, job_id=1,
        >>>     year=2010, title="The Hurt Locker",
        >>>     nominations=9, awards=6, best_picture=True
        >>> )
    """
    id: int
    job_id: int
    year: int = Field(..., ge=1927, le=2100, description="Ano da premiação (Oscar começou em 1927)")
    title: str = Field(..., min_length=1, max_length=500)
    nominations: int = Field(..., ge=0, description="Número de indicações")
    awards: int = Field(..., ge=0, description="Número de prêmios ganhos")
    best_picture: bool = Field(..., description="Se ganhou Melhor Filme")
    
    @field_validator("awards")
    @classmethod
    def validate_awards_not_exceed_nominations(cls, awards: int, info) -> int:
        """
        Valida que o número de prêmios não excede o número de indicações.
        
        Args:
            awards: Número de prêmios ganhos
            info: Informações de validação (contém nominations)
            
        Returns:
            int: Número de prêmios validado
            
        Raises:
            ValueError: Se prêmios > indicações
        """
        # Durante a criação, info.data pode ter nominations
        nominations = info.data.get("nominations")
        if nominations is not None and awards > nominations:
            raise ValueError(
                f"Número de prêmios ({awards}) não pode exceder "
                f"número de indicações ({nominations})"
            )
        return awards
    
    model_config = ConfigDict(from_attributes=True)


class OscarDataListResponse(BaseModel):
    """
    Schema de resposta para lista de dados de Oscar.
    
    Attributes:
        total: Total de registros
        data: Lista de dados
    """
    total: int
    data: List[OscarDataResponse]


# ==================== Crawl Schemas ====================

class CrawlResponse(BaseModel):
    """
    Schema de resposta para requisições de scraping.
    
    Retornado quando um job de scraping é agendado.
    
    Attributes:
        job_id: ID do job criado
        message: Mensagem descritiva
        status: Status inicial do job
        
    Example:
        >>> response = CrawlResponse(
        >>>     job_id=1,
        >>>     message="Job de scraping agendado com sucesso",
        >>>     status="pending"
        >>> )
    """
    job_id: int
    message: str
    status: Literal["pending", "running", "completed", "failed"]


# ==================== Results Schemas ====================

class JobResultsResponse(BaseModel):
    """
    Schema de resposta para resultados de um Job.
    
    Retorna os dados coletados por um job específico.
    
    Attributes:
        job: Informações do job
        hockey_data: Dados de hockey (se aplicável)
        oscar_data: Dados de oscar (se aplicável)
        
    Example:
        >>> response = JobResultsResponse(
        >>>     job=job_info,
        >>>     hockey_data=[...],
        >>>     oscar_data=[]
        >>> )
    """
    job: JobResponse
    hockey_data: List[HockeyDataResponse] = []
    oscar_data: List[OscarDataResponse] = []


# ==================== Error Schemas ====================

class ErrorResponse(BaseModel):
    """
    Schema padrão para respostas de erro.
    
    Attributes:
        detail: Descrição do erro
        error_code: Código do erro (opcional)
        
    Example:
        >>> error = ErrorResponse(
        >>>     detail="Job não encontrado",
        >>>     error_code="JOB_NOT_FOUND"
        >>> )
    """
    detail: str
    error_code: Optional[str] = None
