import unittest
from unittest.mock import Mock, patch

from services.entity_extraction import extract_entities


class EntityExtractionTests(unittest.TestCase):
    @patch("services.entity_extraction.genai.Client")
    def test_ocr_text_is_added_as_context_for_dip_processed_input(self, client_factory):
        client = client_factory.return_value
        client.models.generate_content.return_value = Mock(text="{}")

        result = extract_entities(
            b"processed image",
            "image/png",
            api_key="test-key",
            ocr_text="Claimant: Ada Example",
        )

        request = client.models.generate_content.call_args.kwargs
        self.assertEqual(
            request["contents"][-1],
            "OpenCV-enhanced Tesseract OCR text:\nClaimant: Ada Example",
        )
        self.assertIn('"Claim Summary"', result)

    @patch("services.entity_extraction.genai.Client")
    def test_existing_call_without_ocr_text_remains_supported(self, client_factory):
        client = client_factory.return_value
        client.models.generate_content.return_value = Mock(text="{}")

        extract_entities(b"processed image", "image/png", api_key="test-key")

        request = client.models.generate_content.call_args.kwargs
        self.assertEqual(len(request["contents"]), 2)


if __name__ == "__main__":
    unittest.main()
