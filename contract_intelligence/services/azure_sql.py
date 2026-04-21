"""
Azure SQL service implementation.

Provides database operations for storing contract metadata.
"""

from typing import Any, Dict, Optional

import pyodbc
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, MetaData, Table
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func

from contract_intelligence.config.settings import settings
from contract_intelligence.services.base import SQLService
from contract_intelligence.utils.exceptions import AzureServiceError
from contract_intelligence.utils.logging import get_logger

logger = get_logger(__name__)

Base = declarative_base()


class Contract(Base):
    """Contract database model."""
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(255), unique=True, nullable=False)
    blob_url = Column(String(500))
    document_type = Column(String(100))
    content_summary = Column(Text)
    risk_score = Column(Float)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class AzureSQLService(SQLService):
    """Azure SQL service implementation."""

    def __init__(self) -> None:
        """Initialize the SQL database connection."""
        try:
            # Create connection string
            connection_string = (
                f"Driver={{ODBC Driver 18 for SQL Server}};"
                f"Server=tcp:{settings.sql.server}.database.windows.net,1433;"
                f"Database={settings.sql.database};"
                f"Uid={settings.sql.user};"
                f"Pwd={settings.sql.password.get_secret_value()};"
                "Encrypt=yes;"
                "TrustServerCertificate=no;"
                "Connection Timeout=30;"
            )

            # Create SQLAlchemy engine
            self.engine = create_engine(
                f"mssql+pyodbc:///?odbc_connect={connection_string}",
                echo=False,  # Set to True for debugging
            )

            # Create tables
            Base.metadata.create_all(self.engine)

            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

            logger.info("Azure SQL service initialized", database=settings.sql.database)
        except Exception as e:
            logger.error("Failed to initialize SQL service", error=str(e))
            raise AzureServiceError(f"Failed to initialize SQL service: {e}") from e

    def insert_contract(self, contract_data: Dict[str, Any]) -> int:
        """
        Insert contract data into the database.

        Args:
            contract_data: Contract data to insert.

        Returns:
            ID of the inserted record.

        Raises:
            AzureServiceError: If insertion fails.
        """
        session = None
        try:
            logger.info("Inserting contract data", document_id=contract_data.get("document_id"))

            session = self.SessionLocal()

            contract = Contract(
                document_id=contract_data["document_id"],
                blob_url=contract_data.get("blob_url"),
                document_type=contract_data.get("document_type"),
                content_summary=contract_data.get("content_summary"),
                risk_score=contract_data.get("risk_score"),
            )

            session.add(contract)
            session.commit()
            session.refresh(contract)

            contract_id = contract.id
            logger.info("Contract data inserted", contract_id=contract_id)
            return contract_id

        except Exception as e:
            if session:
                session.rollback()
            logger.error("Contract insertion failed", document_id=contract_data.get("document_id"), error=str(e))
            raise AzureServiceError(f"Contract insertion failed: {e}") from e
        finally:
            if session:
                session.close()

    def get_contract(self, contract_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve contract data by ID.

        Args:
            contract_id: Contract ID.

        Returns:
            Contract data if found, None otherwise.

        Raises:
            AzureServiceError: If retrieval fails.
        """
        session = None
        try:
            logger.info("Retrieving contract data", contract_id=contract_id)

            session = self.SessionLocal()
            contract = session.query(Contract).filter(Contract.id == contract_id).first()

            if contract:
                contract_data = {
                    "id": contract.id,
                    "document_id": contract.document_id,
                    "blob_url": contract.blob_url,
                    "document_type": contract.document_type,
                    "content_summary": contract.content_summary,
                    "risk_score": contract.risk_score,
                    "created_at": contract.created_at.isoformat() if contract.created_at else None,
                    "updated_at": contract.updated_at.isoformat() if contract.updated_at else None,
                }
                logger.info("Contract data retrieved", contract_id=contract_id)
                return contract_data
            else:
                logger.info("Contract not found", contract_id=contract_id)
                return None

        except Exception as e:
            logger.error("Contract retrieval failed", contract_id=contract_id, error=str(e))
            raise AzureServiceError(f"Contract retrieval failed: {e}") from e
        finally:
            if session:
                session.close()