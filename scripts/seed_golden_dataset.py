import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.logging import app_logger

GOLDEN_DATA = [
    # ==========================================
    # IN-DOMAIN: Password & Access Control (1-10)
    # ==========================================
    {
        "question": "What is the minimum required password length according to company policy?",
        "ground_truth": "Passwords must be at least 12 characters long.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What character types must be included in passwords?",
        "ground_truth": "Passwords must include uppercase letters, lowercase letters, numbers, and special characters.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What is the mandatory password expiration frequency?",
        "ground_truth": "Passwords must be changed periodically every 90 days.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "When is Multi-Factor Authentication (MFA) required for employees?",
        "ground_truth": "All employees are required to use Multi-Factor Authentication (MFA) when accessing the internal corporate VPN.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "Can employees share their credentials or accounts with colleagues?",
        "ground_truth": "Sharing individual accounts or login credentials with colleagues is strictly forbidden under the access control policy.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What happens after multiple consecutive failed login attempts?",
        "ground_truth": "Accounts are locked automatically after 5 consecutive failed login attempts.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What is the required idle session lock timeout for workstations?",
        "ground_truth": "Workstations must automatically lock after 15 minutes of inactivity.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What are the rules regarding password reuse?",
        "ground_truth": "Employees cannot reuse any of their previous 10 passwords.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "Is administrative access granted permanently to all engineers?",
        "ground_truth": "Administrative privileges are granted strictly based on the principle of least privilege and require manager approval.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "How are access rights handled when an employee leaves the company?",
        "ground_truth": "All system and building access rights are revoked immediately upon employee termination.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },

    # ==========================================
    # IN-DOMAIN: Data Protection & PII (11-20)
    # ==========================================
    {
        "question": "How should customer Personally Identifiable Information (PII) be encrypted?",
        "ground_truth": "Customers' Personally Identifiable Information (PII) must be encrypted using the AES-256 standard both at-rest and in-transit.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What types of customer data are classified as PII?",
        "ground_truth": "PII includes full names, phone numbers, Social Security numbers, and credit card details.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "Can PII data be shared via email or public chat channels?",
        "ground_truth": "Sharing files containing PII via public chat channels or unapproved personal email is strictly prohibited.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What protocol is required for data transmission in-transit?",
        "ground_truth": "Data in-transit must be encrypted using TLS 1.3 or higher.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "How long must customer audit logs be retained?",
        "ground_truth": "Audit logs must be retained securely for a minimum of 1 year.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What are the restrictions on using external USB storage devices?",
        "ground_truth": "Using unapproved external USB drives or personal storage media on company machines is strictly prohibited.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "How should confidential paper documents be disposed of?",
        "ground_truth": "Confidential paper documents must be shredded using cross-cut shredders before disposal.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "Are employees allowed to copy production database data to local laptops?",
        "ground_truth": "Exporting or copying unmasked production customer data to personal or local workstations is prohibited.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What is the policy regarding database backups?",
        "ground_truth": "Database backups must be executed daily, encrypted with AES-256, and stored in a separate geographical region.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "Who must approve access to sensitive customer PII tables?",
        "ground_truth": "Access to sensitive customer PII requires written approval from the Data Protection Officer (DPO).",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },

    # ==========================================
    # IN-DOMAIN: Remote Work & Device Security (21-30)
    # ==========================================
    {
        "question": "Is using public Wi-Fi networks allowed for remote work?",
        "ground_truth": "Using public Wi-Fi networks to access internal systems is strictly prohibited without corporate VPN connection.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What software must be installed on personal devices used for work?",
        "ground_truth": "All personal devices used for work must have company-approved antivirus software and MDM installed.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What is the minimum operating system update requirement for laptops?",
        "ground_truth": "All laptops must have automated security patches enabled and installed within 7 days of release.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "How should lost or stolen company devices be reported?",
        "ground_truth": "Lost or stolen company devices must be reported to the IT Security Helpdesk within 2 hours of discovery.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "Are family members allowed to use company-issued laptops?",
        "ground_truth": "Company-issued laptops are for authorized employee business use only; family members are strictly prohibited from using them.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What full-disk encryption standard is required for corporate laptops?",
        "ground_truth": "All company laptops must have full-disk encryption enabled (BitLocker for Windows, FileVault for macOS).",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What is the policy for installing unauthorized third-party software?",
        "ground_truth": "Employees cannot install unapproved third-party software on company endpoints without IT clearance.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What is the clean desk policy requirement at the end of the day?",
        "ground_truth": "All physical sensitive notes and tokens must be locked away in drawers when leaving the desk.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "How often must employees complete security awareness training?",
        "ground_truth": "All staff must complete mandatory cybersecurity awareness training annually.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What should an employee do if they receive a suspicious phishing email?",
        "ground_truth": "Suspicious emails must be forwarded immediately to the security operations center via the Report Phishing button.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },

    # ==========================================
    # IN-DOMAIN: Engineering & CI/CD Security (31-35)
    # ==========================================
    {
        "question": "What is the minimum unit test code coverage required before merging code?",
        "ground_truth": "Unit tests must achieve a minimum code coverage of 80% before merging into the main branch.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "How many peer code approvals are mandatory before deploying to production?",
        "ground_truth": "At least one senior peer review approval is required on all Pull Requests targeting production.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "Are hardcoded secrets permitted in source code repositories?",
        "ground_truth": "Hardcoding API keys, passwords, or secrets in git repositories is strictly forbidden and blocked by pre-commit hooks.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What container vulnerability scanning threshold blocks production deployment?",
        "ground_truth": "Any critical or high CVE vulnerabilities detected by container scanners block deployment to production.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What is the incident response SLA for critical security vulnerabilities?",
        "ground_truth": "Critical severity vulnerabilities must be patched and deployed within 24 hours of notification.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },

    # ==========================================
    # OUT-OF-DOMAIN: Hallucination & Gate Verification (36-50)
    # ==========================================
    {
        "question": "What is the best recipe for authentic Italian carbonara pasta?",
        "ground_truth": "The internal documentation does not contain cooking recipes.",
        "source_file": "",
        "is_in_domain": False
    },
    {
        "question": "Who won the FIFA World Cup in 2022?",
        "ground_truth": "The internal documentation does not contain sports tournament records.",
        "source_file": "",
        "is_in_domain": False
    },
    {
        "question": "What is the distance between the Earth and the Moon?",
        "ground_truth": "The internal documentation does not contain astronomical measurements.",
        "source_file": "",
        "is_in_domain": False
    },
    {
        "question": "How do you change an engine oil filter on a Toyota Camry?",
        "ground_truth": "The internal documentation does not contain automotive repair guides.",
        "source_file": "",
        "is_in_domain": False
    },
    {
        "question": "What are the top tourist attractions to visit in Kyoto, Japan?",
        "ground_truth": "The internal documentation does not contain travel guides.",
        "source_file": "",
        "is_in_domain": False
    },
    {
        "question": "Can you explain the rules of American football?",
        "ground_truth": "The internal documentation does not contain sports rules.",
        "source_file": "",
        "is_in_domain": False
    },
    {
        "question": "What was the capital city of the Byzantine Empire?",
        "ground_truth": "The internal documentation does not contain ancient history facts.",
        "source_file": "",
        "is_in_domain": False
    },
    {
        "question": "How do you prune bonsai trees in winter?",
        "ground_truth": "The internal documentation does not contain gardening instructions.",
        "source_file": "",
        "is_in_domain": False
    },
    {
        "question": "What is the stock price prediction for Apple next month?",
        "ground_truth": "The internal documentation does not contain financial trading advice.",
        "source_file": "",
        "is_in_domain": False
    },
    {
        "question": "How does photosynthesis convert sunlight into chemical energy?",
        "ground_truth": "The internal documentation does not contain biology textbooks.",
        "source_file": "",
        "is_in_domain": False
    },
    {
        "question": "What is the boiling point of liquid nitrogen?",
        "ground_truth": "The internal documentation does not contain physics constants.",
        "source_file": "",
        "is_in_domain": False
    },
    {
        "question": "Who composed the Four Seasons violin concertos?",
        "ground_truth": "The internal documentation does not contain classical music history.",
        "source_file": "",
        "is_in_domain": False
    },
    {
        "question": "What are the rules of Texas Hold'em poker?",
        "ground_truth": "The internal documentation does not contain card game rules.",
        "source_file": "",
        "is_in_domain": False
    },
    {
        "question": "How do aircraft jet engines generate thrust?",
        "ground_truth": "The internal documentation does not contain aerospace engineering manuals.",
        "source_file": "",
        "is_in_domain": False
    },
    {
        "question": "What are the main differences between Python and Ruby programming languages?",
        "ground_truth": "The internal documentation does not contain general programming language comparisons.",
        "source_file": "",
        "is_in_domain": False
    }
]


def seed_dataset(output_path: str = "data/golden/golden_dataset.json"):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(GOLDEN_DATA, f, indent=4, ensure_ascii=False)
    in_domain_count = sum(1 for x in GOLDEN_DATA if x["is_in_domain"])
    out_domain_count = sum(1 for x in GOLDEN_DATA if not x["is_in_domain"])
    app_logger.info(
        f"[Seed] Successfully seeded {len(GOLDEN_DATA)} items to {output_path} "
        f"({in_domain_count} in-domain [70%], {out_domain_count} out-of-domain [30%])"
    )


if __name__ == "__main__":
    seed_dataset()
