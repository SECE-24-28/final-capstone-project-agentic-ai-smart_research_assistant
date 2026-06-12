from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base

class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512), nullable=False)
    authors = Column(String(1024), nullable=True)
    abstract = Column(Text, nullable=True)
    year = Column(String(32), nullable=True)
    doi = Column(String(256), nullable=True)
    journal = Column(String(256), nullable=True)
    source = Column(String(128), nullable=True)
    file_path = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    summaries = relationship("Summary", back_populates="paper")
    citations = relationship("Citation", back_populates="paper")
    chat_history = relationship("ChatHistory", back_populates="paper")

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    objective = Column(Text, nullable=True)
    methodology = Column(Text, nullable=True)
    findings = Column(Text, nullable=True)
    limitations = Column(Text, nullable=True)
    contributions = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    paper = relationship("Paper", back_populates="summaries")

class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False, index=True)
    paper_ids = Column(String(256), nullable=False, index=True)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class FinalReport(Base):
    __tablename__ = "final_reports"

    id              = Column(Integer, primary_key=True, index=True)
    title           = Column(String(512), nullable=True)
    topic           = Column(String(256), nullable=False, index=True)
    paper_ids       = Column(String(512), nullable=False, index=True)
    summary_ids     = Column(String(256), nullable=True)
    comparison_id   = Column(Integer, nullable=True)
    # legacy column kept as-is so existing rows are not lost
    content         = Column(Text, nullable=True)
    # primary storage – new reports write here
    report_markdown = Column(Text, nullable=True)
    template_type   = Column(String(64), nullable=True, default="Research Report")
    created_at      = Column(DateTime, default=datetime.utcnow)

class Citation(Base):
    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    citation_type = Column(String(64), nullable=False, default="journal")
    citation_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    paper = relationship("Paper", back_populates="citations")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=True)
    session_id = Column(String(128), nullable=True)
    user_question = Column(Text, nullable=False)
    assistant_answer = Column(Text, nullable=False)
    source_references = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    paper = relationship("Paper", back_populates="chat_history")


class CoordinatorRun(Base):
    """Records every Auto Mode coordinator execution for audit and analytics."""
    __tablename__ = "coordinator_runs"

    id         = Column(Integer, primary_key=True, index=True)
    workflow   = Column(String(128), nullable=False)
    intent     = Column(String(64),  nullable=False)
    query      = Column(Text,        nullable=False)
    topic      = Column(String(256), nullable=True)
    task_id    = Column(String(128), nullable=True, index=True)
    status     = Column(String(32),  nullable=False, default="pending")
    result_type= Column(String(32),  nullable=True)
    created_at = Column(DateTime,    default=datetime.utcnow)
    completed_at = Column(DateTime,  nullable=True)
