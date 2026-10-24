from src.ingestion.cleaners import TextCleaner

def test_text_cleaner():
    raw_text = "Dữ liệu   mẫu\n\n\n\nChính sách bảo mật.\r\nĐiều 1:   Mật khẩu.  "
    cleaned = TextCleaner.clean(raw_text)

    assert "\r" not in cleaned
    assert "\n\n\n" not in cleaned
    assert "   " not in cleaned
    assert "Điều 1: Mật khẩu." in cleaned