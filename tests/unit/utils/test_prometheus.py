"""
Prometheus client unit tests
"""

import os
import pytest
from unittest.mock import Mock, patch
from krkn_ai.utils.prometheus import is_openshift, create_prometheus_client
from krkn_ai.models.custom_errors import PrometheusConnectionError


class TestPrometheusUtils:
    """Test Prometheus utility functions"""

    def test_is_openshift_returns_true_when_clusterversions_exist(self):
        """Test is_openshift returns True when cluster is OpenShift"""
        with patch("krkn_ai.utils.prometheus.run_shell", return_value=("", 0)):
            result = is_openshift("/tmp/test-kubeconfig")
            assert result is True

    def test_is_openshift_returns_false_when_clusterversions_not_exist(self):
        """Test is_openshift returns False when cluster is not OpenShift"""
        with patch("krkn_ai.utils.prometheus.run_shell", return_value=("", 1)):
            result = is_openshift("/tmp/test-kubeconfig")
            assert result is False

    def test_create_prometheus_client_uses_environment_variables_when_set(self):
        """Test create_prometheus_client uses PROMETHEUS_URL and PROMETHEUS_TOKEN from env"""
        with patch.dict(
            os.environ,
            {
                "PROMETHEUS_URL": "https://prometheus.example.com",
                "PROMETHEUS_TOKEN": "test-token",
            },
        ):
            with patch("krkn_ai.utils.prometheus.KrknPrometheus") as mock_prom_class:
                mock_client = Mock()
                mock_client.process_query.return_value = None
                mock_prom_class.return_value = mock_client

                client = create_prometheus_client("/tmp/test-kubeconfig")

                mock_prom_class.assert_called_once_with(
                    "https://prometheus.example.com", "test-token"
                )
                assert client == mock_client

    def test_create_prometheus_client_fetches_url_from_openshift_route_when_env_not_set(
        self,
    ):
        """Test create_prometheus_client fetches URL from OpenShift route when env vars not set"""
        import json

        with patch.dict(os.environ, {}, clear=True):
            with patch("krkn_ai.utils.prometheus.is_openshift", return_value=True):
                route_json = json.dumps(
                    {
                        "items": [
                            {
                                "spec": {
                                    "host": "thanos-query-openshift-monitoring.apps.example.com"
                                }
                            }
                        ]
                    }
                )
                with patch("krkn_ai.utils.prometheus.run_shell") as mock_shell:
                    # Mock OpenShift route query and token fetch
                    mock_shell.side_effect = [
                        (route_json, 0),  # route query
                        ("test-token", 0),  # token fetch
                    ]
                    with patch(
                        "krkn_ai.utils.prometheus.KrknPrometheus"
                    ) as mock_prom_class:
                        mock_client = Mock()
                        mock_client.process_query.return_value = None
                        mock_prom_class.return_value = mock_client

                        create_prometheus_client("/tmp/test-kubeconfig")

                        # Verify URL was constructed correctly
                        mock_prom_class.assert_called_once()
                        call_args = mock_prom_class.call_args[0]
                        assert (
                            call_args[0]
                            == "https://thanos-query-openshift-monitoring.apps.example.com"
                        )
                        assert call_args[1] == "test-token"

    def test_create_prometheus_client_raises_error_when_connection_fails(self):
        """Test create_prometheus_client raises PrometheusConnectionError when connection fails"""
        with patch.dict(
            os.environ,
            {
                "PROMETHEUS_URL": "https://prometheus.example.com",
                "PROMETHEUS_TOKEN": "test-token",
                "MOCK_FITNESS": "",
            },
        ):
            with patch("krkn_ai.utils.prometheus.KrknPrometheus") as mock_prom_class:
                mock_client = Mock()
                mock_client.process_query.side_effect = Exception("Connection failed")
                mock_prom_class.return_value = mock_client

                with pytest.raises(PrometheusConnectionError):
                    create_prometheus_client("/tmp/test-kubeconfig")
