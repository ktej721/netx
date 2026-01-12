import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
import socket
import json

from netx.cli.main import main
from netx.core.models import PhaseResult, URLParseResult, DNSResolutionResult, HostAddress, TCPConnectResult, TLSHandshakeResult, HTTPRequestResult, DNSAddress
from netx.core.engine import ExecutionEngine


class TestCli(unittest.TestCase):

    def setUp(self):
        # Redirect stdout to capture print output
        self.held_stdout = sys.stdout
        sys.stdout = self.mock_stdout = StringIO()

    def tearDown(self):
        # Restore stdout
        sys.stdout = self.held_stdout

    @patch('netx.cli.main.ExecutionEngine')
    @patch('argparse.ArgumentParser.parse_args')
    def test_cli_explain_success_text_output(self, mock_parse_args, mock_execution_engine_class):
        # Configure mock_parse_args for text output
        mock_parse_args.return_value = MagicMock(
            command="explain",
            url="https://example.com",
            json=False,
            timeout=5.0,
            retries=3
        )

        # Configure mock_execution_engine_class instance
        mock_engine_instance = MagicMock()
        mock_execution_engine_class.return_value = mock_engine_instance
        
        # Mock results from engine.run()
        mock_engine_instance.run.return_value = [
            PhaseResult(name="URL Parsing", duration_ms=10.0, success=True, data=URLParseResult(scheme="https", host="example.com", port=443, path="/", query="")),
            PhaseResult(name="DNS Resolution", duration_ms=20.0, success=True, data=DNSResolutionResult(addresses=[DNSAddress(ip="1.2.3.4", family="IPv4")], count=1)),
            PhaseResult(name="TCP Connection", duration_ms=30.0, success=True, data=TCPConnectResult(ip="1.2.3.4", port=443, family="IPv4")),
            PhaseResult(name="TLS Handshake", duration_ms=40.0, success=True, data=TLSHandshakeResult(tls_version="TLSv1.3", cipher="AES", sni="example.com")),
            PhaseResult(name="HTTP Request", duration_ms=50.0, success=True, data=HTTPRequestResult(status_code=200, reason="OK", proto="HTTP/1.1", bytes_received=1024))
        ]
        mock_engine_instance.is_success = True
        mock_engine_instance.total_duration_ms = 150.0

        # Run the main function
        main()

        output = self.mock_stdout.getvalue()
        self.assertIn("URL Parsing", output)
        self.assertIn("DNS Resolution", output)
        self.assertIn("TCP Connection", output)
        self.assertIn("TLS Handshake", output)
        self.assertIn("HTTP Request", output)
        self.assertIn("✔ Completed successfully in 150.00 ms", output)
        
        # Verify specific data prints
        self.assertIn("scheme: https", output)
        self.assertIn("Protocol: HTTP/1.1", output)
        self.assertIn("Bytes Received: 1024", output)


    @patch('netx.cli.main.ExecutionEngine')
    @patch('argparse.ArgumentParser.parse_args')
    def test_cli_explain_failure_text_output(self, mock_parse_args, mock_execution_engine_class):
        mock_parse_args.return_value = MagicMock(
            command="explain",
            url="https://example.com",
            json=False,
            timeout=5.0,
            retries=3
        )

        mock_engine_instance = MagicMock()
        mock_execution_engine_class.return_value = mock_engine_instance
        
        # Mock results, with one failure
        mock_engine_instance.run.return_value = [
            PhaseResult(name="URL Parsing", duration_ms=10.0, success=True, data=URLParseResult(scheme="https", host="example.com", port=443, path="/", query="")),
            PhaseResult(name="DNS Resolution", duration_ms=20.0, success=False, error="DNS lookup failed")
        ]
        mock_engine_instance.is_success = False

        with self.assertRaises(SystemExit) as cm:
            main()

        self.assertEqual(cm.exception.code, 1) # Expect failure exit

        output = self.mock_stdout.getvalue()
        self.assertIn("URL Parsing", output)
        self.assertIn("DNS Resolution", output)
        self.assertIn("Error: DNS lookup failed", output)
        self.assertIn("✘ Pipeline failed at DNS Resolution", output)


    @patch('netx.cli.main.ExecutionEngine')
    @patch('argparse.ArgumentParser.parse_args')
    def test_cli_explain_success_json_output(self, mock_parse_args, mock_execution_engine_class):
        mock_parse_args.return_value = MagicMock(
            command="explain",
            url="https://example.com",
            json=True,
            timeout=5.0,
            retries=3
        )

        mock_engine_instance = MagicMock()
        mock_execution_engine_class.return_value = mock_engine_instance
        
        mock_engine_instance.run.return_value = [
            PhaseResult(name="URL Parsing", duration_ms=10.0, success=True, data=URLParseResult(scheme="https", host="example.com", port=443, path="/", query="")),
            PhaseResult(name="HTTP Request", duration_ms=50.0, success=True, data=HTTPRequestResult(status_code=200, reason="OK", proto="HTTP/1.1", bytes_received=1024))
        ]
        mock_engine_instance.is_success = True
        mock_engine_instance.total_duration_ms = 60.0
    
        # Execute main
        main()

        # Verify
        self.assertTrue(mock_execution_engine_class.called)
        output = self.mock_stdout.getvalue()
        self.assertIn('"target": "https://example.com"', output)
        self.assertIn('"success": true', output)

        output_json = json.loads(output)

        self.assertEqual(output_json["target"], "https://example.com")
        self.assertTrue(output_json["success"])
        self.assertEqual(output_json["total_duration_ms"], 60.0)
        self.assertEqual(len(output_json["phases"]), 2)
        self.assertEqual(output_json["phases"][0]["name"], "URL Parsing")
        self.assertEqual(output_json["phases"][0]["data"]["scheme"], "https")
        self.assertEqual(output_json["phases"][1]["data"]["status_code"], 200)


if __name__ == '__main__':
    unittest.main()