class QSTError(Exception):
    """Base exception for all QST errors."""

    code: str = "QST-000"


class ValidationError(QSTError):
    """Raised when invalid parameters are passed."""

    code: str = "QST-VAL-001"


class SimulationError(QSTError):
    """Raised when the underlying simulator fails."""

    code: str = "QST-SIM-001"


class ExportError(QSTError):
    """Raised when output export fails."""

    code: str = "QST-EXP-001"
