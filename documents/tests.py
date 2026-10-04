import tempfile
import unittest
from pathlib import Path
import fitz
from .precheck import gstin_check_digit, validate_gstin, precheck_gst_certificate


class GSTPrecheckTests(unittest.TestCase):
    def test_gstin_checksum(self):
        # 27AABCA1234F1Z -> 9
        chk = gstin_check_digit("27AABCA1234F1Z")
        self.assertEqual(chk, "9")

    def test_validate_gstin_valid(self):
        checks = validate_gstin("27AABCA1234F1Z9")
        for name, passed, detail in checks:
            self.assertTrue(passed, f"Check '{name}' failed with detail: {detail}")

    def test_precheck_gst_certificate_pdf(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            doc = fitz.open()
            page = doc.new_page()
            content = (
                "Government of India\n"
                "Registration Certificate\n"
                "Registration Number: 27AABCA1234F1Z9\n"
                "Legal Name: Amol Foods Pvt Ltd\n"
                "Trade Name: Amol Foods\n"
            )
            page.insert_text((50, 50), content)
            doc.save(str(tmp_path))
            doc.close()

            res = precheck_gst_certificate(tmp_path, profile_name="Amol Foods Pvt Ltd", expected_state_code="27")
            self.assertEqual(res["status"], "Pre-validated")
            self.assertEqual(res["score"], 100.0)
            self.assertEqual(res["gstin"], "27AABCA1234F1Z9")
            self.assertEqual(res["legal_name"], "Amol Foods Pvt Ltd")
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
