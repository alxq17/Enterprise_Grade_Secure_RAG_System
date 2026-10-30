import pytest

from src.guardrails.pii_masker import PIIMasker


@pytest.fixture
def masker():
    return PIIMasker()


def test_email_mask_and_unmask(masker):
    text = "Please reach out to support@acme-corp.com or john.doe_1@gmail.com for assistance."
    masked, pii_map = masker.mask(text)

    assert "[EMAIL_1]" in masked
    assert "[EMAIL_2]" in masked
    assert "support@acme-corp.com" not in masked
    assert "john.doe_1@gmail.com" not in masked

    unmasked = masker.unmask(masked, pii_map)
    assert unmasked == text


def test_phone_mask_and_unmask(masker):
    text = "Call John at 0912345678 or +84987654321, or office 0912-345-678."
    masked, pii_map = masker.mask(text)

    assert "[PHONE_1]" in masked
    assert "[PHONE_2]" in masked
    assert "0912345678" not in masked

    unmasked = masker.unmask(masked, pii_map)
    assert unmasked == text


def test_id_mask_and_unmask(masker):
    text = "Employee CCCD is 001202001234."
    masked, pii_map = masker.mask(text)

    assert "[ID_1]" in masked
    assert "001202001234" not in masked

    unmasked = masker.unmask(masked, pii_map)
    assert unmasked == text


def test_bracket_variation_unmasking(masker):
    # Tests that <EMAIL_1> format produced by some LLMs is also unmasked properly
    pii_map = {"[EMAIL_1]": "admin@company.com"}
    response_with_angle_brackets = "Contact <EMAIL_1> immediately."
    unmasked = masker.unmask(response_with_angle_brackets, pii_map)
    assert unmasked == "Contact admin@company.com immediately."


def test_no_pii_in_text(masker):
    text = "What is the policy regarding password rotation every 90 days?"
    masked, pii_map = masker.mask(text)
    assert masked == text
    assert len(pii_map) == 0
    assert masker.unmask(masked, pii_map) == text
