"""Verification model — kept in its own module for explicit import."""
from app.models.diagnosis import VerificationResult  # re-export

__all__ = ["VerificationResult"]
