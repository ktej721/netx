class NetXError(Exception):
    """Base exception for all NetX errors."""
    pass


class PhaseError(NetXError):
    """Base exception for errors occurring during a specific phase."""
    def __init__(self, message: str, phase_name: str, original_error: Exception = None):
        super().__init__(f"[{phase_name}] {message}")
        self.phase_name = phase_name
        self.original_error = original_error


class URLParseError(PhaseError):
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message, "URL Parsing", original_error)


class DNSResolutionError(PhaseError):
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message, "DNS Resolution", original_error)


class TCPConnectionError(PhaseError):
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message, "TCP Connection", original_error)


class TLSHandshakeError(PhaseError):
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message, "TLS Handshake", original_error)


class HTTPRequestError(PhaseError):
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message, "HTTP Request", original_error)
