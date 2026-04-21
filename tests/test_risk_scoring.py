"""Unit test for the risk-scoring aggregator."""
from src.agents import RiskScoringAgent
from src.domain import Clause, ClauseType, Contract, RiskLevel


def test_aggregate_no_clauses():
    contract = Contract(source_blob="x")
    score, level = RiskScoringAgent._aggregate(contract)
    assert score == 0.0
    assert level == RiskLevel.LOW


def test_aggregate_high_risk():
    contract = Contract(source_blob="x")
    contract.clauses = [
        Clause(
            clause_type=ClauseType.LIABILITY,
            text="...",
            risk_level=RiskLevel.CRITICAL,
            risk_score=0.95,
        ),
        Clause(
            clause_type=ClauseType.INDEMNITY,
            text="...",
            risk_level=RiskLevel.HIGH,
            risk_score=0.8,
        ),
    ]
    score, level = RiskScoringAgent._aggregate(contract)
    assert score > 0.5
    assert level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
