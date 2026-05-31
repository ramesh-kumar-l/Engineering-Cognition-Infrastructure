"""Domain errors for the reflection package."""

from __future__ import annotations


class ReflectionError(Exception):
    """Base class for all reflection-domain errors."""


class LessonNotFoundError(ReflectionError):
    """Raised when a lesson ID resolves to no row."""


class RetrospectiveNotFoundError(ReflectionError):
    """Raised when a retrospective ID resolves to no row."""


class InvalidCadenceError(ReflectionError):
    """Raised when an unknown cadence value is provided."""


class InvalidConfidenceError(ReflectionError):
    """Raised when an unknown confidence value is provided."""


class SupersessionError(ReflectionError):
    """Raised when a lesson supersession violates invariants."""
