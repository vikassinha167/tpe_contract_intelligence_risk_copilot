"""Azure SQL adapter implementing `IContractRepository`.

We persist the contract as a single JSON column for simplicity; in production
you'd normalise into multiple tables. The interface stays the same — that's
the OCP win.
"""
from __future__ import annotations

import json
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import Column, DateTime, MetaData, String, Table, Text, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from src.domain import Contract
from src.interfaces import IContractRepository
from src.utils import PersistenceError, with_retry

_metadata = MetaData()

contracts_table = Table(
    "contracts",
    _metadata,
    Column("contract_id", String(64), primary_key=True),
    Column("source_blob", String(512), nullable=False),
    Column("stage", String(32), nullable=False),
    Column("overall_risk_level", String(16)),
    Column("overall_risk_score", String(16)),
    Column("payload_json", Text, nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
)


class AzureSqlContractRepository(IContractRepository):
    def __init__(self, connection_string: str) -> None:
        # SQLAlchemy URL for pyodbc
        url = (
            "mssql+pyodbc:///?odbc_connect="
            + connection_string.replace(" ", "+")
        )
        self._engine: Engine = create_engine(url, pool_pre_ping=True, future=True)
        _metadata.create_all(self._engine)

    @contextmanager
    def _conn(self) -> Iterator:
        try:
            with self._engine.begin() as conn:
                yield conn
        except SQLAlchemyError as exc:
            raise PersistenceError(str(exc)) from exc

    @with_retry(SQLAlchemyError)
    def save(self, contract: Contract) -> None:
        payload = contract.model_dump_json()
        row = {
            "contract_id": contract.contract_id,
            "source_blob": contract.source_blob,
            "stage": contract.stage.value,
            "overall_risk_level": contract.overall_risk_level.value
            if contract.overall_risk_level
            else None,
            "overall_risk_score": str(contract.overall_risk_score)
            if contract.overall_risk_score is not None
            else None,
            "payload_json": payload,
            "created_at": contract.created_at,
            "updated_at": contract.updated_at,
        }
        with self._conn() as conn:
            # MERGE-style upsert via dialect-agnostic delete+insert
            conn.execute(
                contracts_table.delete().where(
                    contracts_table.c.contract_id == contract.contract_id
                )
            )
            conn.execute(contracts_table.insert().values(**row))

    @with_retry(SQLAlchemyError)
    def get(self, contract_id: str) -> Contract | None:
        with self._conn() as conn:
            row = conn.execute(
                contracts_table.select().where(
                    contracts_table.c.contract_id == contract_id
                )
            ).first()
        if not row:
            return None
        return Contract.model_validate(json.loads(row.payload_json))
