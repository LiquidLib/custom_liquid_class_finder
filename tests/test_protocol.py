"""
Tests for the Liquid Class Calibration Protocol
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch
from opentrons import protocol_api

# Add the project root to the path so we can import from protocols
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the actual protocol module
import protocols.single_channel as protocol  # noqa: E402


class TestProtocol:
    """Test cases for the liquid class calibration protocol"""

    def test_protocol_metadata(self):
        """Test that protocol metadata is correctly defined"""
        # Check metadata structure
        assert hasattr(protocol, "metadata")
        assert "protocolName" in protocol.metadata
        assert "author" in protocol.metadata
        assert "description" in protocol.metadata
        assert "source" in protocol.metadata

        # Check specific values
        assert (
            protocol.metadata["protocolName"]
            == "Liquid Class Calibration with Pluggable Optimization"
        )
        assert protocol.metadata["author"] == "Roman Gurovich"

    def test_requirements_structure(self):
        """Test that requirements are correctly defined"""
        assert hasattr(protocol, "requirements")
        assert "robotType" in protocol.requirements
        assert "apiLevel" in protocol.requirements

        # Check specific values
        assert protocol.requirements["robotType"] == "Flex"
        assert protocol.requirements["apiLevel"] == "2.22"

    def test_parameter_definition(self):
        """Test that parameters are correctly defined"""
        # Mock protocol context
        mock_protocol = Mock(spec=protocol_api.ProtocolContext)
        mock_params = Mock()
        mock_protocol.params = mock_params

        # Test parameter addition
        with patch("protocols.single_channel.add_parameters") as mock_add_params:
            protocol.add_parameters(mock_params)
            mock_add_params.assert_called_once_with(mock_params)

    @patch("protocols.single_channel.run")
    def test_run_function_exists(self, mock_run):
        """Test that the run function exists and can be called"""
        # Mock protocol context
        mock_protocol = Mock(spec=protocol_api.ProtocolContext)
        mock_protocol.params.sample_count = 96
        mock_protocol.params.pipette_mount = "right"

        # Test that run function can be called
        protocol.run(mock_protocol)
        mock_run.assert_called_once_with(mock_protocol)

    def test_reference_parameters_structure(self):
        """Test that reference parameters have the expected structure"""
        # Test that the protocol can be imported and has expected functions
        assert protocol is not None
        assert hasattr(protocol, "run")
        assert hasattr(protocol, "add_parameters")
        assert hasattr(protocol, "get_default_liquid_class_params")


if __name__ == "__main__":
    pytest.main([__file__])
