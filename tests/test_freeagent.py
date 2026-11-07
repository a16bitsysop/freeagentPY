"""
Unit tests for the public FreeAgent client.
"""

import unittest

from freeagent import FreeAgent


class FreeAgentClientTestCase(unittest.TestCase):
    """
    Tests for FreeAgent client construction.
    """

    def test_default_api_base_url(self):
        """Test the client uses the live API URL by default."""
        client = FreeAgent()
        self.assertEqual(client.api_base_url, "https://api.freeagent.com/v2/")

    def test_custom_api_base_url(self):
        """Test a sandbox URL can be passed in and is used by the client."""
        sandbox = "https://api.sandbox.freeagent.com/v2/"
        client = FreeAgent(api_base_url=sandbox)
        self.assertEqual(client.api_base_url, sandbox)
        self.assertIs(client.bank.parent, client)


if __name__ == "__main__":
    unittest.main()
