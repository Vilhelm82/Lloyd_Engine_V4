class LloydV4Error(Exception):
    """Base error for Lloyd V4 substrate failures."""


class ProtocolViolationError(LloydV4Error):
    """Raised when a consumer receives an unhandled status."""


class ScalarizationError(LloydV4Error):
    """Raised when scalarization is requested where no honest scalar exists."""


class HiddenGuardRailError(LloydV4Error):
    """Raised when a primitive attempts undeclared numerical correction."""


class UnhandledStratumError(LloydV4Error):
    """Raised when a stratum has no explicit handling rule."""
