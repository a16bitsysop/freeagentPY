import unittest
from unittest.mock import MagicMock
from pathlib import Path
import tempfile
import os

# Import BankAPI from bank.py
from freeagent.bank import BankAPI

# Dummy ExplanationPayload class for testing
class DummyPayload:
    def __init__(self):
        self.attachment = None
        self.description = "Test"
        self.gross_value = 123.45

class BankAPITestCase(unittest.TestCase):
    def setUp(self):
        # Dummy parent with API methods mocked
        self.parent = MagicMock()
        self.api = BankAPI(self.parent)

    def test_check_file_size_allows_small_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"x" * (1024 * 10))  # 10KB
            tmp.flush()
            size = self.api._check_file_size(Path(tmp.name))
        self.assertEqual(size, 10240)
        os.unlink(tmp.name)

    def test_check_file_size_raises_on_large(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"x" * (6 * 1024 * 1024))  # 6MB
            tmp.flush()
            with self.assertRaises(ValueError):
                self.api._check_file_size(Path(tmp.name))
        os.unlink(tmp.name)

    def test_encode_file_base64(self):
        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tmp:
            content = b"abc123"
            tmp.write(content)
            tmp.flush()
            b64 = self.api._encode_file_base64(Path(tmp.name))
        import base64
        self.assertEqual(b64, base64.b64encode(content).decode("utf-8"))
        os.unlink(tmp.name)

    def test_get_filetype_valid_and_invalid(self):
        valid = Path("file.pdf")
        self.assertEqual(self.api._get_filetype(valid), "application/x-pdf")
        invalid = Path("file.exe")
        with self.assertRaises(ValueError):
            self.api._get_filetype(invalid)

    def test_attach_file_to_explanation(self):
        # Prepare a small file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"data")
            tmp.flush()
            payload = DummyPayload()
            self.api._get_filetype = MagicMock(return_value="application/x-pdf")
            self.api._encode_file_base64 = MagicMock(return_value="ZGF0YQ==")
            self.api.attach_file_to_explanation(payload, Path(tmp.name), "desc")
            self.assertIn("file_name", payload.attachment)
            self.assertEqual(payload.attachment["description"], "desc")
        os.unlink(tmp.name)

    def test_explain_transaction_dryrun(self):
        payload = DummyPayload()
        self.api.serialize_for_api = MagicMock(return_value={"description": "desc", "gross_value": 111})
        self.api.explain_transaction(payload, dryrun=True)
        self.parent.post_api.assert_not_called()

    def test_explain_transaction_real(self):
        payload = DummyPayload()
        self.api.serialize_for_api = MagicMock(return_value={"description": "desc", "gross_value": 111})
        self.api.explain_transaction(payload, dryrun=False)
        self.parent.post_api.assert_called_once()

    def test_explain_update_dryrun(self):
        payload = DummyPayload()
        self.api.serialize_for_api = MagicMock(return_value={"description": "desc", "gross_value": 111})
        self.api.explain_update("url", payload, dryrun=True)
        self.parent.put_api.assert_not_called()

    def test_explain_update_real(self):
        payload = DummyPayload()
        self.api.serialize_for_api = MagicMock(return_value={"description": "desc", "gross_value": 111})
        self.api.explain_update("url", payload, dryrun=False)
        self.parent.put_api.assert_called_once()

    def test_get_unexplained_transactions(self):
        dummy_return = {"transactions": [1,2,3]}
        self.parent.get_api.return_value = dummy_return
        result = self.api.get_unexplained_transactions("accid")
        self.parent.get_api.assert_called_once()
        self.assertEqual(result, dummy_return)

    def test_get_paypal_id_works(self):
        self.parent.get_api.return_value = {"bank_accounts": [{"name": "PayPal Account", "url": "http://x/y/123"}]}
        id = self.api.get_paypal_id("PayPal Account")
        self.assertEqual(id, "123")
    
    def test_get_first_paypal_id(self):
        self.parent.get_api.return_value = {"bank_accounts": [{"url": "http://x/y/456"}]}
        id = self.api.get_first_paypal_id()
        self.assertEqual(id, "456")
        self.parent.get_api.return_value = {"bank_accounts": []}
        id = self.api.get_first_paypal_id()
        self.assertIsNone(id)

    def test_get_id(self):
        self.parent.get_api.return_value = {"bank_accounts": [{"name": "Test", "url": "http://x/y/789"}]}
        id = self.api.get_id("Test")
        self.assertEqual(id, "789")

    def test_get_primary(self):
        self.parent.get_api.return_value = {"bank_accounts": [
            {"is_primary": False, "url": "http://x/y/111"},
            {"is_primary": True, "url": "http://x/y/222"}
        ]}
        id = self.api.get_primary()
        self.assertEqual(id, "222")
        self.parent.get_api.return_value = {"bank_accounts": []}
        id = self.api.get_primary()
        self.assertIsNone(id)

if __name__ == "__main__":
    unittest.main()
