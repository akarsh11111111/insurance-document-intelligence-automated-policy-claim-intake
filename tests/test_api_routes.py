import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app


class ExtractionRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("api.routes.extract_entities", return_value='{"Claim Summary": {}}')
    @patch(
        "api.routes.process_document",
        return_value=SimpleNamespace(
            processed_bytes=b"enhanced image",
            processed_mime_type="image/png",
            enhanced_text="clean OCR text",
        ),
    )
    def test_api_preprocesses_raw_upload_before_ai(self, process_document, extract):
        response = self.client.post(
            "/extract",
            files={"file": ("claim.png", b"raw image", "image/png")},
        )

        self.assertEqual(response.status_code, 200)
        process_document.assert_called_once_with(b"raw image", "image/png")
        extract.assert_called_once_with(
            b"enhanced image",
            "image/png",
            ocr_text="clean OCR text",
        )

    @patch("api.routes.extract_entities", return_value='{"Claim Summary": {}}')
    @patch("api.routes.process_document")
    def test_frontend_preprocessed_upload_is_not_processed_twice(
        self, process_document, extract
    ):
        response = self.client.post(
            "/extract",
            files={"file": ("claim.png", b"enhanced image", "image/png")},
            data={"preprocessed": "true", "ocr_text": "clean OCR text"},
        )

        self.assertEqual(response.status_code, 200)
        process_document.assert_not_called()
        extract.assert_called_once_with(
            b"enhanced image",
            "image/png",
            ocr_text="clean OCR text",
        )


if __name__ == "__main__":
    unittest.main()
