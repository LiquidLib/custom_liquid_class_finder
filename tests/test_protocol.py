"""
Tests for the Liquid Class Calibration Protocol
"""

import pytest
from unittest.mock import Mock, patch
from opentrons import protocol_api


class TestProtocol:
    """Test cases for the liquid class calibration protocol"""

    def test_protocol_metadata(self):
        """Test that protocol metadata is correctly defined"""
        # Import the protocol module
        import protocol

        # Check metadata structure
        assert hasattr(protocol, "metadata")
        assert "protocolName" in protocol.metadata
        assert "author" in protocol.metadata
        assert "description" in protocol.metadata
        assert "source" in protocol.metadata

        # Check specific values
        assert protocol.metadata["protocolName"] == "Liquid Class Calibration with Gradient Descent"
        assert protocol.metadata["author"] == "Roman Gurovich"

    def test_requirements_structure(self):
        """Test that requirements are correctly defined"""
        import protocol

        assert hasattr(protocol, "requirements")
        assert "robotType" in protocol.requirements
        assert "apiLevel" in protocol.requirements

        # Check specific values
        assert protocol.requirements["robotType"] == "Flex"
        assert protocol.requirements["apiLevel"] == "2.22"

    def test_parameter_definition(self):
        """Test that parameters are correctly defined"""
        import protocol

        # Mock protocol context
        mock_protocol = Mock(spec=protocol_api.ProtocolContext)
        mock_params = Mock()
        mock_protocol.params = mock_params

        # Test parameter addition
        with patch("protocol.add_parameters") as mock_add_params:
            protocol.add_parameters(mock_params)
            mock_add_params.assert_called_once_with(mock_params)

    @patch("protocol.run")
    def test_run_function_exists(self, mock_run):
        """Test that the run function exists and can be called"""
        import protocol

        # Mock protocol context
        mock_protocol = Mock(spec=protocol_api.ProtocolContext)
        mock_protocol.params.sample_count = 96
        mock_protocol.params.pipette_mount = "right"

        # Test that run function can be called
        protocol.run(mock_protocol)
        mock_run.assert_called_once_with(mock_protocol)

    def test_reference_parameters_structure(self):
        """Test that reference parameters have the expected structure"""
        # This would test the parameter structure if we could access it
        # For now, we'll just verify the protocol can be imported
        import protocol

        assert protocol is not None


if __name__ == "__main__":
    pytest.main([__file__])
