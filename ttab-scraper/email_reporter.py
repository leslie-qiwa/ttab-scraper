#!/usr/bin/env python3
"""
TTAB Email Reporter - Send scraper results via email with persistent configuration
"""
import smtplib
import csv
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from datetime import datetime

class EmailReporter:
    """Send TTAB scraper results via email"""

    CONFIG_FILE = Path(__file__).parent / 'config.json'

    def __init__(self, smtp_server=None, smtp_port=None):
        # Try to load from config file first
        config = self.load_config()

        self.smtp_server = smtp_server or config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = smtp_port or config.get('smtp_port', 587)
        self.from_email = config.get('from_email')
        self.password = config.get('password')
        self.default_subject = config.get('default_subject', 'TTAB Search Results')

    def load_config(self):
        """Load email configuration from config.json"""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    return config.get('email', {})
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        return {}

    def save_config(self):
        """Save email configuration to config.json"""
        config = {}

        # Load existing config if it exists
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
            except:
                pass

        # Update email section
        config['email'] = {
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'from_email': self.from_email,
            'password': self.password,
            'default_subject': self.default_subject
        }

        # Save
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✓ Email configuration saved to {self.CONFIG_FILE}")
        return self.CONFIG_FILE

    def configure(self, from_email, password, smtp_server=None, smtp_port=None, save=True):
        """
        Configure email credentials

        Args:
            from_email: Sender email address
            password: Email password or app password
            smtp_server: SMTP server (optional, defaults to gmail)
            smtp_port: SMTP port (optional, defaults to 587)
            save: Save configuration to file (default: True)
        """
        self.from_email = from_email
        self.password = password

        if smtp_server:
            self.smtp_server = smtp_server
        if smtp_port:
            self.smtp_port = smtp_port

        if save:
            return self.save_config()

        return None

    def is_configured(self):
        """Check if email is configured"""
        return bool(self.from_email and self.password)

    def generate_summary(self, csv_file):
        """Generate summary statistics from CSV file"""
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            cases = list(reader)

        if not cases:
            return "No cases found in the results."

        # Extract statistics
        total_cases = len(cases)
        filing_dates = [c.get('Filing_Date', '') for c in cases if c.get('Filing_Date')]
        earliest = min(filing_dates) if filing_dates else 'N/A'
        latest = max(filing_dates) if filing_dates else 'N/A'

        # Count unique defendants and plaintiffs
        defendants = set(c.get('Defendant_Name', '') for c in cases if c.get('Defendant_Name'))
        plaintiffs = set(c.get('Plaintiff_Name', '') for c in cases if c.get('Plaintiff_Name'))

        summary = f"""
TTAB Search Results Summary
{'=' * 60}

Total Cases: {total_cases}
Date Range: {earliest} to {latest}
Unique Defendants: {len(defendants)}
Unique Plaintiffs: {len(plaintiffs)}

Sample Cases (First 5):
{'-' * 60}
"""

        for i, case in enumerate(cases[:5], 1):
            summary += f"""
{i}. Case #{case.get('Case_Number', 'N/A')}
   Filed: {case.get('Filing_Date', 'N/A')}
   Defendant: {case.get('Defendant_Name', 'N/A')[:50]}...
   Plaintiff: {case.get('Plaintiff_Name', 'N/A')[:50]}...
   URL: {case.get('Detail_URL', 'N/A')}
"""

        if total_cases > 5:
            summary += f"\n... and {total_cases - 5} more cases (see attached CSV)\n"

        summary += f"""
{'=' * 60}

Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Configuration saved to: {self.CONFIG_FILE}

This is an automated report from the TTAB scraper.
Full results are attached as CSV file.
"""

        return summary

    def send_report(self, to_email, csv_file, subject=None, custom_message=None):
        """
        Send email report with CSV attachment

        Args:
            to_email: Recipient email address
            csv_file: Path to CSV file to attach
            subject: Email subject (optional)
            custom_message: Additional message to include (optional)
        """
        if not self.is_configured():
            return False, "Email not configured. Use configure() first or check config.json"

        csv_path = Path(csv_file)
        if not csv_path.exists():
            return False, f"CSV file not found: {csv_file}"

        # Generate subject if not provided
        if not subject:
            timestamp = datetime.now().strftime('%Y-%m-%d')
            subject = f"{self.default_subject} - {timestamp}"

        # Create message
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Generate summary
        summary = self.generate_summary(csv_file)

        # Build email body
        body = ""
        if custom_message:
            body += f"{custom_message}\n\n"

        body += summary

        msg.attach(MIMEText(body, 'plain'))

        # Attach CSV file
        with open(csv_file, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())

        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {csv_path.name}'
        )
        msg.attach(part)

        # Send email
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.from_email, self.password)
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()

            return True, f"Email sent successfully to {to_email}"

        except Exception as e:
            return False, f"Failed to send email: {str(e)}"


def main():
    """Example usage and configuration utility"""
    import sys

    if len(sys.argv) < 2:
        print("TTAB Email Reporter")
        print("=" * 60)
        print("\nUsage:")
        print("  Configure: python email_reporter.py config <from_email>")
        print("  Send:      python email_reporter.py send <csv_file> <to_email>")
        print("  Check:     python email_reporter.py check")
        print("\nExamples:")
        print("  python email_reporter.py config sender@gmail.com")
        print("  python email_reporter.py send output/results.csv legal@company.com")
        print("  python email_reporter.py check")
        sys.exit(0)

    command = sys.argv[1]

    if command == 'config':
        if len(sys.argv) < 3:
            print("Usage: python email_reporter.py config <from_email>")
            sys.exit(1)

        from_email = sys.argv[2]

        # Prompt for password securely
        import getpass
        password = getpass.getpass(f"Enter password/app password for {from_email}: ")

        # Optional: custom SMTP
        smtp_server = input(f"SMTP server (default: smtp.gmail.com): ").strip() or 'smtp.gmail.com'
        smtp_port = input(f"SMTP port (default: 587): ").strip() or '587'

        # Create reporter and save config
        reporter = EmailReporter()
        config_file = reporter.configure(from_email, password, smtp_server, int(smtp_port), save=True)

        print(f"\n✓ Email configuration saved!")
        print(f"  Config file: {config_file}")
        print(f"  From: {from_email}")
        print(f"  SMTP: {smtp_server}:{smtp_port}")
        print("\nConfiguration will persist across Claude Code sessions.")

    elif command == 'send':
        if len(sys.argv) < 4:
            print("Usage: python email_reporter.py send <csv_file> <to_email>")
            sys.exit(1)

        csv_file = sys.argv[2]
        to_email = sys.argv[3]

        # Load configuration
        reporter = EmailReporter()

        if not reporter.is_configured():
            print("✗ Email not configured!")
            print("  Run: python email_reporter.py config <your-email@gmail.com>")
            sys.exit(1)

        print(f"\nSending report from config...")
        print(f"  From: {reporter.from_email}")
        print(f"  To: {to_email}")
        print(f"  File: {csv_file}")

        success, message = reporter.send_report(to_email, csv_file)

        if success:
            print(f"\n✓ {message}")
        else:
            print(f"\n✗ {message}")
            sys.exit(1)

    elif command == 'check':
        reporter = EmailReporter()

        print("Email Configuration Status")
        print("=" * 60)

        if reporter.is_configured():
            print("✓ Email is configured")
            print(f"  Config file: {reporter.CONFIG_FILE}")
            print(f"  From: {reporter.from_email}")
            print(f"  SMTP: {reporter.smtp_server}:{reporter.smtp_port}")
            print("\n✓ Ready to send emails")
        else:
            print("✗ Email is not configured")
            print(f"  Config file: {reporter.CONFIG_FILE} (not found)")
            print("\n  To configure, run:")
            print("  python email_reporter.py config <your-email@gmail.com>")

    else:
        print(f"Unknown command: {command}")
        print("Valid commands: config, send, check")
        sys.exit(1)


if __name__ == '__main__':
    main()
