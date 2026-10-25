import re
from typing import Dict, Tuple


class PIIMasker:
     """
     Bidirectional PII Masker for sensitive entities:
     - Emails (RFC 5322 compatible regex)
     - Phone numbers (Vietnam national, mobile, and international formats with spaces/dashes)
     - Citizen IDs / National IDs (9 to 12 digits)
     """

     EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
     # Vietnam mobile and international phone formats with optional spaces, dots, or hyphens
     PHONE_PATTERN = re.compile(r"(?:(?:\+84|0)[ .-]?(?:3[2-9]|5[689]|7[06-9]|8[1-5]|9\d)(?:[ .-]?\d){7}\b)")
     # National ID / Citizen ID (CCCD 12 digits, CMND 9 digits)
     ID_PATTERN = re.compile(r"\b(?:0\d{11}|\d{9})\b")

     def mask(self, text: str) -> Tuple[str, Dict[str, str]]:
          """
          Anonymize sensitive PII entities (email, phone, ID) within text.
          Returns (masked_text, pii_map).
          """
          pii_map: Dict[str, str] = {}
          email_counter = 1
          phone_counter = 1
          id_counter = 1

          # 1. Mask Email
          def email_repl(match):
               nonlocal email_counter
               placeholder = f"[EMAIL_{email_counter}]"
               pii_map[placeholder] = match.group(0)
               email_counter += 1
               return placeholder

          masked_text = self.EMAIL_PATTERN.sub(email_repl, text)

          # 2. Mask Phone
          def phone_repl(match):
               nonlocal phone_counter
               placeholder = f"[PHONE_{phone_counter}]"
               pii_map[placeholder] = match.group(0)
               phone_counter += 1
               return placeholder

          masked_text = self.PHONE_PATTERN.sub(phone_repl, masked_text)

          # 3. Mask National ID (only if not already masked)
          def id_repl(match):
               nonlocal id_counter
               val = match.group(0)
               placeholder = f"[ID_{id_counter}]"
               pii_map[placeholder] = val
               id_counter += 1
               return placeholder

          masked_text = self.ID_PATTERN.sub(id_repl, masked_text)

          return masked_text, pii_map

     def unmask(self, text: str, pii_map: Dict[str, str]) -> str:
          """
          Restore original PII entities in the generated response.
          Supports bracket variations ([EMAIL_1], <EMAIL_1>) and case-insensitivity.
          """
          if not pii_map:
               return text

          result = text
          for placeholder, original in pii_map.items():
               # Exact match [TAG]
               result = result.replace(placeholder, original)
               # Angle bracket variation <TAG>
               angle_placeholder = placeholder.replace("[", "<").replace("]", ">")
               result = result.replace(angle_placeholder, original)
               # Case-insensitive fallback
               result = re.sub(re.escape(placeholder), original, result, flags=re.IGNORECASE)
               result = re.sub(re.escape(angle_placeholder), original, result, flags=re.IGNORECASE)

          return result