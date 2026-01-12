import unittest
from unittest.mock import patch, MagicMock
from netx.core.engine import ExecutionEngine
from netx.core.models import RequestContext, PhaseResult
from netx.core.exceptions import PhaseError


class TestExecutionEngine(unittest.TestCase):

    def setUp(self):
        # Create mock phases
        self.mock_url_parse_phase = MagicMock()
        self.mock_url_parse_phase.execute.return_value = PhaseResult(name="URL Parsing", duration_ms=10.0, success=True)

        self.mock_dns_phase = MagicMock()
        self.mock_dns_phase.execute.return_value = PhaseResult(name="DNS Resolution", duration_ms=20.0, success=True)

        self.mock_tcp_phase = MagicMock()
        self.mock_tcp_phase.execute.return_value = PhaseResult(name="TCP Connection", duration_ms=30.0, success=True)

        self.mock_tls_phase = MagicMock()
        self.mock_tls_phase.execute.return_value = PhaseResult(name="TLS Handshake", duration_ms=40.0, success=True)

        self.mock_http_phase = MagicMock()
        self.mock_http_phase.execute.return_value = PhaseResult(name="HTTP Request", duration_ms=50.0, success=True)

    def test_pipeline_success(self):
        engine = ExecutionEngine(
            url="https://example.com",
            timeout=5.0,
            retries=1,
            pipeline=[
                self.mock_url_parse_phase,
                self.mock_dns_phase,
                self.mock_tcp_phase,
                self.mock_tls_phase,
                self.mock_http_phase,
            ]
        )

        results = engine.run()

        self.assertEqual(len(results), 5)
        self.assertTrue(engine.is_success)
        self.assertEqual(engine.total_duration_ms, 150.0)
        
        # Verify execution order
        self.mock_url_parse_phase.execute.assert_called_once()
        self.mock_dns_phase.execute.assert_called_once()
        self.mock_tcp_phase.execute.assert_called_once()
        self.mock_tls_phase.execute.assert_called_once()
        self.mock_http_phase.execute.assert_called_once()

    def test_pipeline_failure(self):
        # Simulate DNS phase failure
        self.mock_dns_phase.execute.return_value = PhaseResult(
            name="DNS Resolution",
            duration_ms=20.0,
            success=False,
            error="DNS lookup failed"
        )

        engine = ExecutionEngine(
            url="https://example.com",
            timeout=5.0,
            retries=1,
            pipeline=[
                self.mock_url_parse_phase,
                self.mock_dns_phase,
                self.mock_tcp_phase,
            ]
        )

        results = engine.run()

        self.assertEqual(len(results), 2) # URL + DNS
        self.assertFalse(engine.is_success)
        self.assertEqual(results[-1].name, "DNS Resolution")
        self.assertEqual(results[-1].error, "DNS lookup failed")
        
        # Verify execution stops after failure
        self.mock_url_parse_phase.execute.assert_called_once()
        self.mock_dns_phase.execute.assert_called_once()
        self.mock_tcp_phase.execute.assert_not_called()


if __name__ == '__main__':
    unittest.main()