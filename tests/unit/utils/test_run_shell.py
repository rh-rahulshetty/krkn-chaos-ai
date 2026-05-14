"""
run_shell unit tests
"""

import pytest
from unittest.mock import patch

from krkn_ai.models.custom_errors import ShellCommandTimeoutError
from krkn_ai.utils import run_shell


class TestRunShell:
    """Test run_shell timeout behavior"""

    def test_timeout_raises_shell_command_timeout_error(self):
        with pytest.raises(ShellCommandTimeoutError):
            run_shell("sleep 10", timeout=5)

    @patch("krkn_ai.utils.subprocess.Popen")
    def test_oserror_returns_empty_string_and_127(self, mock_popen):
        """Test that run_shell catches OSError (like FileNotFoundError) and returns empty string and 127"""
        mock_popen.side_effect = FileNotFoundError("Mocked file not found error")
        logs, returncode = run_shell("krknctl --version")
        assert returncode == 127
        assert logs == ""

    @patch("krkn_ai.utils.subprocess.Popen")
    def test_permission_error_returns_empty_string_and_127(self, mock_popen):
        """Test that run_shell catches OSError (like PermissionError) and returns empty string and 127"""
        mock_popen.side_effect = PermissionError("Mocked permission error")
        logs, returncode = run_shell("podman --version")
        assert returncode == 127
        assert logs == ""
