import socket

from netx.phases.base import Phase
from netx.core.models import RequestContext, HTTPRequestResult # Added HTTPRequestResult
from netx.core.exceptions import HTTPRequestError


class HTTPRequestPhase(Phase):
    name = "HTTP Request"

    def run(self, context: RequestContext) -> HTTPRequestResult: # Changed return type
        if not context.sock:
            raise HTTPRequestError("No active connection for HTTP request.")

        try:
            # Construct raw HTTP request
            # We use HTTP/1.1 and 'Connection: close' to ensure simple cleanup
            # unless we want to demo reuse (which is out of scope for single CLI run usually, but good practice)
            # 'Connection: close' is safer for this one-shot tool.
            
            path = context.path
            if context.query:
                path += f"?{context.query}"

            request_lines = [
                f"GET {path} HTTP/1.1",
                f"Host: {context.host}",
                f"User-Agent: {context.user_agent}",
                "Connection: close",
                "Accept: */*",
                "", ""  # End of headers
            ]
            
            request_data = "\r\n".join(request_lines).encode("ascii")
            
            # Send Request
            context.sock.sendall(request_data)
            
            # Read Response (Simple implementation reading until end of headers + measure TTFB)
            # We want to measure Time To First Byte (TTFB) carefully.
            
            # We'll read 1 byte to trigger the TTFB measurement
            first_byte = context.sock.recv(1)
            
            if not first_byte:
                 raise HTTPRequestError("Connection closed by server before response.")

            # TTFB is implicitly measured by the Phase wrapper around this run() function 
            # because we spent time constructing and sending. 
            # Wait, the Phase wrapper measures the WHOLE run() time.
            # Ideally, we should measure TTFB *inside* here and return it.
            # But the phase duration will include send time + wait time.
            # To get strict TTFB, we'd need manual timing here. 
            # However, for the purpose of the tool "HTTP Request" phase duration usually implies 
            # "Send + Wait + Receive Headers".
            
            # Let's read the rest of the headers to parse status.
            response_buffer = first_byte
            
            # Simple header parser loop
            headers_done = False
            while not headers_done:
                chunk = context.sock.recv(4096)
                if not chunk:
                    break
                response_buffer += chunk
                if b"\r\n\r\n" in response_buffer:
                    headers_done = True
            
            # Parse Status Line
            try:
                header_part = response_buffer.split(b"\r\n\r\n")[0]
                status_line = header_part.split(b"\r\n")[0].decode("iso-8859-1")
                proto, status_code, *reason_parts = status_line.split(" ")
                reason = " ".join(reason_parts)
                
                # Calculate size (rough approximation including headers for what we read so far)
                # If we want full body, we'd loop until close or Content-Length.
                # For this tool, maybe we just want to prove it works.
                # Let's read until close since we sent "Connection: close"
                
                total_bytes = len(response_buffer)
                while True:
                    chunk = context.sock.recv(4096)
                    if not chunk:
                        break
                    total_bytes += len(chunk)
                
                return HTTPRequestResult( # Changed to return HTTPRequestResult
                    status_code=int(status_code),
                    reason=reason,
                    proto=proto,
                    bytes_received=total_bytes
                )
                
            except Exception as e:
                raise HTTPRequestError(f"Failed to parse HTTP response: {e}")

        except socket.timeout:
             raise HTTPRequestError("HTTP request timed out.")
        except OSError as e:
             raise HTTPRequestError(f"Socket error during HTTP: {e}", original_error=e)
