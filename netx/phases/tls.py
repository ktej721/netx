import ssl
import socket

from netx.phases.base import Phase
from netx.core.models import RequestContext, TLSHandshakeResult # Added TLSHandshakeResult
from netx.core.exceptions import TLSHandshakeError


class TLSHandshakePhase(Phase):
    name = "TLS Handshake"

    def run(self, context: RequestContext) -> TLSHandshakeResult: # Changed return type
        # Check if we need TLS
        if context.scheme != "https":
            return TLSHandshakeResult(skipped=True, reason="Scheme is not HTTPS") # Changed to return TLSHandshakeResult

        if not context.sock:
            raise TLSHandshakeError("No active TCP connection found.")

        try:
            # Create SSL Context with secure defaults
            ssl_context = ssl.create_default_context()
            
            # Optional: Add flags for specific TLS versions if needed, or trust env vars
            # ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
            
            # Wrap the socket
            # server_hostname is critical for SNI
            tls_sock = ssl_context.wrap_socket(
                context.sock,
                server_hostname=context.host
            )
            
            # Replace the raw socket in context with the TLS socket
            context.sock = tls_sock
            
            # Extract info
            context.tls_version = tls_sock.version()
            cipher_info = tls_sock.cipher()
            context.cipher = cipher_info[0] if cipher_info else "Unknown"
            
            cert = tls_sock.getpeercert()
            
            return TLSHandshakeResult( # Changed to return TLSHandshakeResult
                tls_version=context.tls_version,
                cipher=context.cipher,
                sni=context.host,
                # "cert_subject": ... (Could parse cert for more info)
            )

        except ssl.SSLError as e:
            raise TLSHandshakeError(f"TLS/SSL Error: {e}", original_error=e)
        except Exception as e:
            raise TLSHandshakeError(f"Unexpected error during handshake: {e}", original_error=e)
