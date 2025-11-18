"""
Test suite for MikroTik Fail2Ban filters

This module tests the regex patterns in Fail2Ban filter configurations
to ensure they correctly match failed login attempts and ignore successful ones.
"""

import re
import pytest
from pathlib import Path


def load_filter_regex(filter_file):
    """
    Load failregex patterns from a Fail2Ban filter configuration file.
    
    Args:
        filter_file: Path to the filter configuration file
        
    Returns:
        List of compiled regex patterns
    """
    filter_path = Path(__file__).parent.parent / "fail2ban" / "filter.d" / filter_file
    
    if not filter_path.exists():
        raise FileNotFoundError(f"Filter file not found: {filter_path}")
    
    patterns = []
    with open(filter_path, 'r') as f:
        in_failregex = False
        for line in f:
            line = line.strip()
            
            # Start of failregex section
            if line.startswith('failregex ='):
                pattern = line.split('=', 1)[1].strip()
                if pattern and not pattern.startswith('^'):
                    pattern = '^' + pattern
                if pattern:
                    patterns.append(pattern)
                in_failregex = True
            # Continuation of failregex
            elif in_failregex and line and not line.startswith('#') and not line.startswith('['):
                if line.startswith('ignoreregex'):
                    break
                if not line.startswith('failregex'):
                    patterns.append(line)
    
    # Replace <HOST> placeholder with IPv4 regex pattern
    host_pattern = r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
    compiled_patterns = []
    for pattern in patterns:
        pattern = pattern.replace('<HOST>', host_pattern)
        try:
            compiled_patterns.append(re.compile(pattern))
        except re.error as e:
            print(f"Warning: Could not compile pattern '{pattern}': {e}")
    
    return compiled_patterns


def _test_log_line(patterns, log_line):
    """
    Test if any of the patterns match the given log line.
    
    Args:
        patterns: List of compiled regex patterns
        log_line: Log line to test
        
    Returns:
        True if any pattern matches, False otherwise
    """
    for pattern in patterns:
        if pattern.search(log_line):
            return True
    return False


class TestMikroTikLoginFilter:
    """Tests for mikrotik-login.conf filter"""
    
    @pytest.fixture
    def patterns(self):
        return load_filter_regex("mikrotik-login.conf")
    
    def test_failed_ssh_login(self, patterns):
        """Test that failed SSH login attempts are matched"""
        log_lines = [
            "Jan 10 12:34:56 mikrotik login failure for user admin from 192.168.1.100 via ssh",
            "Jan 10 12:34:57 mikrotik login failure for user test from 10.0.0.50 via ssh",
            "login failure for user root from 172.16.0.1 via ssh",
        ]
        for log_line in log_lines:
            assert _test_log_line(patterns, log_line), f"Should match: {log_line}"
    
    def test_failed_winbox_login(self, patterns):
        """Test that failed Winbox login attempts are matched"""
        log_lines = [
            "Jan 10 12:34:56 mikrotik login failure for user admin from 192.168.1.100 via winbox",
            "login failure for user test from 10.0.0.50 via winbox",
        ]
        for log_line in log_lines:
            assert _test_log_line(patterns, log_line), f"Should match: {log_line}"
    
    def test_failed_api_login(self, patterns):
        """Test that failed API login attempts are matched"""
        log_lines = [
            "Jan 10 12:34:56 mikrotik login failure for user admin from 192.168.1.100 via api",
            "login failure for user apiuser from 10.0.0.50 via api",
        ]
        for log_line in log_lines:
            assert _test_log_line(patterns, log_line), f"Should match: {log_line}"
    
    def test_successful_login_not_matched(self, patterns):
        """Test that successful logins are NOT matched"""
        log_lines = [
            "Jan 10 12:34:56 mikrotik user admin logged in from 192.168.1.100 via ssh",
            "Jan 10 12:34:57 mikrotik admin logged in via winbox",
            "authentication succeeded for user admin from 192.168.1.100",
        ]
        for log_line in log_lines:
            assert not _test_log_line(patterns, log_line), f"Should NOT match: {log_line}"


class TestMikroTikL2TPFilter:
    """Tests for mikrotik-l2tp.conf filter"""
    
    @pytest.fixture
    def patterns(self):
        return load_filter_regex("mikrotik-l2tp.conf")
    
    def test_failed_l2tp_login(self, patterns):
        """Test that failed L2TP login attempts are matched"""
        log_lines = [
            "Jan 10 12:34:56 mikrotik l2tp,ppp,info <192.168.1.100>: sent CHAP Failure id=0x5",
            "l2tp,ppp,info <10.0.0.50>: sent CHAP Failure id=0x3",
            "l2tp <172.16.0.1>: sent CHAP Failure id=0x1",
        ]
        for log_line in log_lines:
            assert _test_log_line(patterns, log_line), f"Should match: {log_line}"
    
    def test_failed_sstp_login(self, patterns):
        """Test that failed SSTP login attempts are matched"""
        log_lines = [
            "Jan 10 12:34:56 mikrotik sstp,ppp,info <192.168.1.100>: sent CHAP Failure id=0x5",
            "sstp,ppp,info <10.0.0.50>: sent CHAP Failure id=0x3",
            "sstp <172.16.0.1>: sent CHAP Failure id=0x1",
        ]
        for log_line in log_lines:
            assert _test_log_line(patterns, log_line), f"Should match: {log_line}"
    
    def test_successful_l2tp_login_not_matched(self, patterns):
        """Test that successful L2TP logins are NOT matched"""
        log_lines = [
            "Jan 10 12:34:56 mikrotik l2tp,ppp,info <192.168.1.100>: authenticated",
            "l2tp,ppp,info <10.0.0.50>: connected",
            "l2tp user testuser logged in from 192.168.1.100",
        ]
        for log_line in log_lines:
            assert not _test_log_line(patterns, log_line), f"Should NOT match: {log_line}"


class TestMikroTikOVPNFilter:
    """Tests for mikrotik-ovpn.conf filter"""
    
    @pytest.fixture
    def patterns(self):
        return load_filter_regex("mikrotik-ovpn.conf")
    
    def test_failed_ovpn_login(self, patterns):
        """Test that failed OpenVPN login attempts are matched"""
        log_lines = [
            "Jan 10 12:34:56 mikrotik ovpn,info <192.168.1.100>: user 'testuser' authentication failed",
            "ovpn,error <10.0.0.50> authentication failed",
            "openvpn,info <172.16.0.1>: authentication failed",
        ]
        for log_line in log_lines:
            assert _test_log_line(patterns, log_line), f"Should match: {log_line}"
    
    def test_successful_ovpn_login_not_matched(self, patterns):
        """Test that successful OpenVPN logins are NOT matched"""
        log_lines = [
            "Jan 10 12:34:56 mikrotik ovpn,info <192.168.1.100>: authenticated",
            "ovpn,info <10.0.0.50>: connected",
            "openvpn user testuser logged in from 192.168.1.100",
        ]
        for log_line in log_lines:
            assert not _test_log_line(patterns, log_line), f"Should NOT match: {log_line}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
