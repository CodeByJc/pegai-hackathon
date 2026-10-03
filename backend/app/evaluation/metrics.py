"""Evaluation metrics helpers."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AccuracyMetrics:
    total: int
    correct: int
    accuracy: float

    @classmethod
    def from_results(cls, results: list, key: str) -> "AccuracyMetrics":
        total = len(results)
        correct = sum(1 for r in results if getattr(r, key, False))
        return cls(
            total=total,
            correct=correct,
            accuracy=correct / total if total else 0.0,
        )

    def __str__(self) -> str:
        return (
            f"Total: {self.total}  "
            f"Correct: {self.correct}  "
            f"Accuracy: {self.accuracy:.1%}"
        )
