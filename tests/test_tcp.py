import unittest
from unittest.mock import patch, MagicMock
import socket

from netx.core.models import RequestContext, HostAddress
from netx.phases.tcp import TCPConnectPhase
from netx.core.exceptions import TCPConnectionError


class TestTCPConnectPhase(unittest.TestCase):

    @patch('socket.socket')
    def test_tcp_connection_success(self, mock_socket_class):
        # Create a mock socket instance
        mock_socket_instance = MagicMock()
        mock_socket_class.return_value = mock_socket_instance

        # Setup context with resolved addresses
        resolved_addresses = [
            HostAddress(ip='::1', family=socket.AF_INET6),
            HostAddress(ip='127.0.0.1', family=socket.AF_INET)
        ]
        context = RequestContext(
            url="https://localhost",
            host="localhost",
            port=443,
            resolved_addresses=resolved_addresses,
            timeout=1
        )
        phase = TCPConnectPhase()

        # Execute the phase
        result = phase.run(context)

        # Assertions
        self.assertEqual(result.ip, '::1')
        self.assertEqual(result.port, 443)
        self.assertEqual(result.family, 'IPv6')
        mock_socket_instance.settimeout.assert_called_with(1)
        mock_socket_instance.connect.assert_called_with(('::1', 443))
        self.assertIsNotNone(context.sock)

    @patch('socket.socket')
    def test_tcp_connection_fallback(self, mock_socket_class):
        # First attempt fails, second succeeds
        mock_socket_instance_fail = MagicMock()
        mock_socket_instance_fail.connect.side_effect = socket.timeout("Timeout")
        mock_socket_instance_success = MagicMock()

        # The mock class will return the failing instance first, then the succeeding one
        mock_socket_class.side_effect = [mock_socket_instance_fail, mock_socket_instance_success]

        resolved_addresses = [
            HostAddress(ip='::1', family=socket.AF_INET6),
            HostAddress(ip='127.0.0.1', family=socket.AF_INET)
        ]
        context = RequestContext(
            url="https://localhost",
            host="localhost",
            port=443,
            resolved_addresses=resolved_addresses,
            timeout=1
        )
        phase = TCPConnectPhase()
        result = phase.run(context)

        self.assertEqual(result.ip, '127.0.0.1')
        self.assertEqual(result.family, 'IPv4')
        self.assertEqual(mock_socket_class.call_count, 2)
        mock_socket_instance_fail.close.assert_called_once()
        mock_socket_instance_success.connect.assert_called_with(('127.0.0.1', 443))

    @patch('socket.socket')
    def test_tcp_connection_failure(self, mock_socket_class):
        mock_socket_instance = MagicMock()
        mock_socket_instance.connect.side_effect = socket.timeout("Timeout")
        mock_socket_class.return_value = mock_socket_instance

        resolved_addresses = [HostAddress(ip='127.0.0.1', family=socket.AF_INET)]
        context = RequestContext(
            url="http://localhost",
            host="localhost",
            port=80,
            resolved_addresses=resolved_addresses,
            timeout=1
        )
        phase = TCPConnectPhase()

        with self.assertRaises(TCPConnectionError):
            phase.run(context)


if __name__ == '__main__':
    unittest.main()
