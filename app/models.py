"""
Database models using SQLAlchemy.

Este módulo define os modelos de dados da aplicação:
- Job: Representa um job de scraping
- HockeyData: Dados coletados de Hockey
- OscarData: Dados coletados de Oscar

Todos os modelos herdam de Base (definido em database.py)
e usam Type Hints para melhor validação.
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class JobStatus(str, enum.Enum):
    """
    Enum para os possíveis status de um Job.
    
    Attributes:
        PENDING: Job criado, aguardando processamento
        RUNNING: Job em execução
        COMPLETED: Job concluído com sucesso
        FAILED: Job falhou durante execução
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobType(str, enum.Enum):
    """
    Enum para os tipos de Job disponíveis.
    
    Attributes:
        HOCKEY: Job de scraping de dados de Hockey
        OSCAR: Job de scraping de dados de Oscar
        ALL: Job que executa ambos scrapers
    """
    HOCKEY = "hockey"
    OSCAR = "oscar"
    ALL = "all"


class Job(Base):
    """
    Modelo para Jobs de scraping.
    
    Representa um job de coleta de dados, contendo informações
    sobre tipo, status, timestamps e mensagens de erro.
    
    Attributes:
        id: Identificador único do job
        type: Tipo do job (hockey, oscar, all)
        status: Status atual do job
        created_at: Data/hora de criação
        updated_at: Data/hora da última atualização
        error_message: Mensagem de erro (se falhou)
        hockey_data: Relação com dados de hockey coletados
        oscar_data: Relação com dados de oscar coletados
        
    Example:
        >>> job = Job(type=JobType.HOCKEY, status=JobStatus.PENDING)
        >>> db.add(job)
        >>> db.commit()
    """
    __tablename__ = "jobs"
    
    # Campos principais
    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type: str = Column(SQLEnum(JobType), nullable=False, index=True)
    status: str = Column(SQLEnum(JobStatus), nullable=False, default=JobStatus.PENDING, index=True)
    
    # Timestamps
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Informações adicionais
    error_message: Optional[str] = Column(String, nullable=True)
    
    # Relacionamentos (um job pode ter múltiplos resultados)
    hockey_data: List["HockeyData"] = relationship("HockeyData", back_populates="job", cascade="all, delete-orphan")
    oscar_data: List["OscarData"] = relationship("OscarData", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """Representação string do Job."""
        return f"<Job(id={self.id}, type={self.type}, status={self.status})>"


class HockeyData(Base):
    """
    Modelo para dados de Hockey coletados.
    
    Armazena estatísticas de times de Hockey coletadas via scraping.
    Cada registro está associado a um Job específico.
    
    Attributes:
        id: Identificador único do registro
        job_id: ID do job que coletou este dado
        team_name: Nome do time
        year: Ano da temporada
        wins: Número de vitórias
        losses: Número de derrotas
        ot_losses: Número de derrotas na prorrogação
        win_pct: Percentual de vitórias (0.0 a 1.0)
        gf: Goals For - gols marcados
        ga: Goals Against - gols sofridos
        diff: Diferença de gols (GF - GA)
        job: Relação com o Job que coletou este dado
        
    Example:
        >>> data = HockeyData(
        >>>     job_id=1,
        >>>     team_name="Boston Bruins",
        >>>     year=1990,
        >>>     wins=44,
        >>>     losses=24
        >>> )
        >>> db.add(data)
    """
    __tablename__ = "hockey_data"
    
    # Campos principais
    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id: int = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    
    # Dados do time
    team_name: str = Column(String(200), nullable=False, index=True)
    year: int = Column(Integer, nullable=False, index=True)
    
    # Estatísticas de jogos
    wins: int = Column(Integer, nullable=False, default=0)
    losses: int = Column(Integer, nullable=False, default=0)
    ot_losses: int = Column(Integer, nullable=False, default=0)
    
    # Estatísticas calculadas
    win_pct: float = Column(Float, nullable=True)  # Percentual de vitórias
    gf: int = Column(Integer, nullable=True)  # Goals For
    ga: int = Column(Integer, nullable=True)  # Goals Against
    diff: int = Column(Integer, nullable=True)  # Goal Difference
    
    # Relacionamento com Job
    job: Job = relationship("Job", back_populates="hockey_data")
    
    def __repr__(self) -> str:
        """Representação string do HockeyData."""
        return f"<HockeyData(id={self.id}, team={self.team_name}, year={self.year})>"


class OscarData(Base):
    """
    Modelo para dados de Oscar coletados.
    
    Armazena informações sobre filmes e premiações do Oscar.
    Cada registro está associado a um Job específico.
    
    Attributes:
        id: Identificador único do registro
        job_id: ID do job que coletou este dado
        year: Ano da premiação
        title: Título do filme
        nominations: Número de indicações
        awards: Número de prêmios ganhos
        best_picture: Se ganhou Melhor Filme
        job: Relação com o Job que coletou este dado
        
    Example:
        >>> data = OscarData(
        >>>     job_id=1,
        >>>     year=2010,
        >>>     title="The Hurt Locker",
        >>>     nominations=9,
        >>>     awards=6,
        >>>     best_picture=True
        >>> )
        >>> db.add(data)
    """
    __tablename__ = "oscar_data"
    
    # Campos principais
    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id: int = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    
    # Dados do filme
    year: int = Column(Integer, nullable=False, index=True)
    title: str = Column(String(500), nullable=False, index=True)
    
    # Estatísticas de premiação
    nominations: int = Column(Integer, nullable=False, default=0)
    awards: int = Column(Integer, nullable=False, default=0)
    best_picture: bool = Column(Boolean, nullable=False, default=False, index=True)
    
    # Relacionamento com Job
    job: Job = relationship("Job", back_populates="oscar_data")
    
    def __repr__(self) -> str:
        """Representação string do OscarData."""
        return f"<OscarData(id={self.id}, title={self.title}, year={self.year})>"
