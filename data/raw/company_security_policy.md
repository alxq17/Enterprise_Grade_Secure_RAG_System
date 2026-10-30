## Enterprise Information Security Policy
## 1. Access Control
All employees are required to use Multi-Factor Authentication (MFA) when accessing the internal corporate VPN.
Passwords must be at least 12 characters long and include uppercase letters, lowercase letters, numbers, and special characters.
Passwords must be changed every 90 days.

## 2. Personally Identifiable Information (PII) Management and Privacy
Customers’ Personally Identifiable Information (PII), including full names, phone numbers, Social Security numbers, and credit card information, must be encrypted using the AES-256 standard both at rest and in transit.
Sharing files containing PII through public chat platforms or unapproved personal email accounts is strictly prohibited.
## 3. System Deployment Requirements (CI/CD)
All source code changes must pass automated tests before being merged into the main branch:
- Unit Testing: Code coverage must be at least 80%.
- Security Scanning: Trivy scans must report no High or Critical severity vulnerabilities.
- Internal AI Models: Internal AI models must pass quality evaluation tests, including Faithfulness and Recall.
## 4. Remote Work Policy
Remote employees must connect to internal systems through the company VPN.
Using public Wi-Fi networks to access internal systems is prohibited.
All personal devices used for work must have antivirus software provided by the IT department installed.
## 5. Incident Reporting Procedures
Employees must report any detected security incidents to the IT department within 24 hours of discovery.
Employees must not attempt to handle incidents independently or conceal them.
All security incidents must be investigated and documented in accordance with ISO 27001 procedures.