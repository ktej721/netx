import unittest
from unittest.mock import patch, MagicMock
import socket

from netx.core.models import RequestContext
from netx.phases.http import HTTPRequestPhase
from netx.core.exceptions import HTTPRequestError


class TestHTTPRequestPhase(unittest.TestCase):

    @patch('socket.socket')
    def test_http_request_success(self, mock_socket_class):
        mock_sock_instance = MagicMock()
        mock_socket_class.return_value = mock_sock_instance
        
        # Mocking recv to simulate a successful HTTP response
        mock_sock_instance.recv.side_effect = [
            b"HTTP/1.1 200 OK\r\n",
            b"Content-Length: 12\r\n",
            b"Connection: close\r\n",
            b"\r\n",
            b"Hello World!",
            b"" # End of stream
        ]

        context = RequestContext(url="http://example.com", scheme="http", host="example.com", port=80, path="/")
        context.sock = mock_sock_instance # Assign the mock socket to context

        phase = HTTPRequestPhase()
        result = phase.run(context)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.reason, "OK")
        self.assertEqual(result.proto, "HTTP/1.1")
        self.assertEqual(result.bytes_received, 70) # Headers + body length

        mock_sock_instance.sendall.assert_called_once()
        expected_request = (
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"User-Agent: netx/1.0\r\n"
            b"Connection: close\r\n"
            b"Accept: */*\r\n\r\n"
        )
        mock_sock_instance.sendall.assert_called_with(expected_request)

    @patch('socket.socket')
    def test_http_request_timeout(self, mock_socket_class):
        mock_sock_instance = MagicMock()
        mock_socket_class.return_value = mock_sock_instance
        mock_sock_instance.sendall.side_effect = socket.timeout("Send timeout")

        context = RequestContext(url="http://example.com", scheme="http", host="example.com", port=80)
        context.sock = mock_sock_instance

        phase = HTTPRequestPhase()
        with self.assertRaises(HTTPRequestError) as cm:
            phase.run(context)
        self.assertIn("timed out", str(cm.exception))


if __name__ == '__main__':
    unittest.main()

