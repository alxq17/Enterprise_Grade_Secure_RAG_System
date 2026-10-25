import re
from typing import Dict, Tuple

class PIIMasker:
    # Regex chuẩn cho Email và Số điện thoại (quốc tế + Việt Nam)
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    PHONE_PATTERN = re.compile(r"(?:\+84|0)(?:3[2-9]|5[6|8|9]|7[0|6-9]|8[1-5]|9[0-9])[0-9]{7}\b")

    def mask(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Anonymizing email addresses and phone numbers within a string"""
        pii_map: Dict[str, str] = {}
        email_counter = 1
        phone_counter = 1

        # 1 Mask Email
        def email_repl(match):
            nonlocal email_counter
            placeholder = f"[EMAIL_{email_counter}]"
            pii_map[placeholder] = match.group(0)
            email_counter += 1
            return placeholder
        masked_text = self.EMAIL_PATTERN.sub(email_repl, text)
        
        # 2 Mask Phone
        def phone_repl(match):
            nonlocal phone_counter
            placeholder = f"[PHONE_{phone_counter}]"
            pii_map[placeholder] = match.group(0)
            phone_counter += 1
            return placeholder
        masked_text = self.PHONE_PATTERN.sub(phone_repl, masked_text)

        return masked_text, pii_map

    def unmask(self, text: str, pii_map: Dict[str, str]) -> str:
        if not pii_map:
            return text
        result = text
        for placeholder, original in pii_map.items():
            result = result.replace(placeholder, original)
        return result