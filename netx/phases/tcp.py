import socket
import errno
from typing import List, Dict

from netx.phases.base import Phase
from netx.core.models import RequestContext, HostAddress, TCPConnectResult # Added TCPConnectResult
from netx.core.exceptions import TCPConnectionError


class TCPConnectPhase(Phase):
    name = "TCP Connection"

    def run(self, context: RequestContext) -> TCPConnectResult: # Changed return type
        if not context.resolved_addresses:
            raise TCPConnectionError("No DNS results available to connect.")

        last_error = None
        
        # Fallback logic: Try addresses in order (IPv6 -> IPv4 due to DNS sort)
        for host_addr in context.resolved_addresses:
            try:
                sock = socket.socket(host_addr.family, socket.SOCK_STREAM)
                sock.settimeout(context.timeout)
                
                # Update context so we can clean up if this phase fails partway (though we handle it here)
                # But better to assign to context ONLY on success or if we want the pipeline cleanup to handle it.
                # Here we handle close on fail.
                
                sock.connect((host_addr.ip, context.port))
                
                # Success!
                context.sock = sock
                context.selected_address = host_addr
                
                return TCPConnectResult( # Changed to return TCPConnectResult
                    ip=host_addr.ip,
                    port=context.port,
                    family=host_addr.family_str
                )

            except socket.timeout:
                sock.close()
                last_error = f"Timeout connecting to {host_addr.ip}"
            except ConnectionRefusedError:
                sock.close()
                last_error = f"Connection refused by {host_addr.ip}"
            except OSError as e:
                sock.close()
                # Handle specific error codes if needed
                if e.errno == errno.ENETUNREACH:
                    last_error = f"Network unreachable for {host_addr.ip}"
                else:
                    last_error = str(e)
            
        # If we exit the loop, all attempts failed
        raise TCPConnectionError(f"Failed to connect to any resolved address. Last error: {last_error}")
