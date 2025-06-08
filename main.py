import json
import os
import random
import time
import smtplib
import ssl
import base64
import requests
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from colorama import init, Fore, Style
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
init(autoreset=True)

# Show ASCII Banner
print(f"""{Fore.YELLOW}{Style.BRIGHT}
     ██╗░░██╗███████╗██████╗░███╗░░░███╗███████╗░██████╗
     ██║░░██║██╔════╝██╔══██╗████╗░████║██╔════╝██╔════╝
     ███████║█████╗░░██████╔╝██╔████╔██║█████╗░░╚█████╗░
     ██╔══██║██╔══╝░░██╔══██╗██║╚██╔╝██║██╔══╝░░░╚═══██╗
     ██║░░██║███████╗██║░░██║██║░╚═╝░██║███████╗██████╔╝
     ╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚═╝░░░░░╚═╝╚══════╝╚═════╝░
      ░██████╗███████╗███╗░░██╗██████╗░███████╗██████╗░
      ██╔════╝██╔════╝████╗░██║██╔══██╗██╔════╝██╔══██╗
      ╚█████╗░█████╗░░██╔██╗██║██║░░██║█████╗░░██████╔╝
      ░╚═══██╗██╔══╝░░██║╚████║██║░░██║██╔══╝░░██╔══██╗
      ██████╔╝███████╗██║░╚███║██████╔╝███████╗██║░░██║
      ╚═════╝░╚══════╝╚═╝░░╚══╝╚═════╝░╚══════╝╚═╝░░╚═╝
{Style.RESET_ALL}
{Fore.BLUE}          [§] HERMES ADVANCED EMAIL SENDER v8.13 [§]{Style.RESET_ALL}
{Fore.BLUE}              [§] CODED BY: TELENONYM TEAM [§]{Style.RESET_ALL}
{Fore.BLUE}        [§] PURCHASE LICENSE KEY AT @TELENONYM_BOT [§]{Style.RESET_ALL}
""")

def abort(msg):
    print(f"{Fore.RED}[×] {msg}{Style.RESET_ALL}")
    exit(1)

def check_license():
    license_path = "license.txt"
    if os.path.exists(license_path):
        with open(license_path) as f:
            license_key = f.read().strip()
    else:
        license_key = ""

    if not license_key:
        license_key = input(f"{Fore.CYAN}[?] Enter your license key: {Style.RESET_ALL}").strip()
        with open(license_path, "w") as f:
            f.write(license_key)
        print(f"{Fore.YELLOW}[INFO] License saved to license.txt for future use.{Style.RESET_ALL}")

    try:
        print(f"{Fore.YELLOW}[INFO] Validating license key...{Style.RESET_ALL}")
        response = requests.get("https://amlyze.tech/webhook/key.txt", timeout=10)
        if response.status_code != 200:
            abort("Failed to validate license key (server error).")
        valid_keys = [line.strip() for line in response.text.splitlines()]
        if license_key not in valid_keys:
            abort("Invalid or expired license key. Please purchase one at @TELENONYM_BOT.")
        print(f"{Fore.GREEN}[✓] License validated successfully!{Style.RESET_ALL}")
    except Exception as e:
        abort(f"Error validating license key: {e}")

check_license()

# Load SMTP and config
smtp_host = os.getenv('SMTP_HOST')
smtp_port = int(os.getenv('SMTP_PORT', 587))
smtp_user = os.getenv('SMTP_USER')
smtp_pass = os.getenv('SMTP_PASS')

if not (smtp_host and smtp_user and smtp_pass):
    abort("SMTP credentials are missing in .env file. Exiting.")

config_path = 'config.json'
if not os.path.exists(config_path):
    abort(f"Config file '{config_path}' not found.")
with open(config_path) as config_file:
    config = json.load(config_file)

def check_file(path, desc):
    if not os.path.exists(path):
        abort(f"{desc} file '{path}' not found.")
    return path

def generate_random_number():
    return random.randint(1000000, 9999999)

recipient_file = check_file(config['mail_list'], 'Recipient')
with open(recipient_file) as f:
    emails = [e.strip() for e in f if e.strip()]

subjects_file = check_file(config['subjects'], 'Subjects')
with open(subjects_file) as f:
    raw_subjects = [s.strip() for s in f if s.strip()]

senders_file = check_file(config['sender_name_list'], 'Sender name list')
with open(senders_file) as f:
    senders = [s.strip() for s in f if s.strip()]

letter_file = check_file(config['letter'], 'Email letter')
with open(letter_file) as f:
    email_body_template = f.read()

def image_to_base64(image_path):
    image_path = check_file(image_path, 'Image')
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

logo_base64 = image_to_base64(config['logo'])
image_base64 = image_to_base64(config['image'])
icon_base64 = image_to_base64(config['icon'])

email_body_template = email_body_template.replace('{logo}', f"data:image/png;base64,{logo_base64}")
email_body_template = email_body_template.replace('{image}', f"data:image/png;base64,{image_base64}")
email_body_template = email_body_template.replace('{icon}', f"data:image/png;base64,{icon_base64}")

def html_to_plain_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for br in soup.find_all("br"): br.replace_with("\n")
    for p in soup.find_all("p"): p.insert_after("\n\n")
    for div in soup.find_all("div"): div.insert_after("\n")
    for a in soup.find_all("a", href=True):
        text = a.get_text()
        href = a['href']
        a.replace_with(f"{text} ({href})")
    for li in soup.find_all("li"): li.insert_before("• ")
    return soup.get_text().strip()

def create_message(email, html_body, plain_text, subject, sender_name, from_email, sender_domain):
    recipient_name = email.split('@')[0]
    unique_id = f"{''.join(random.choices('0123456789abcdef', k=16))}-{''.join(random.choices('0123456789abcdef', k=16))}"
    message_id = f"<{unique_id}@{random.choice(['sparkpostmail.com', 'amazonses.com', sender_domain])}>"
    x_mailer = random.choice([
        "Microsoft Outlook 16.0", "Mozilla Thunderbird", "Apple Mail",
        "Roundcube Webmail", "Airmail 3.6", "Mailbird",
        "MailerLite", f"Mailer-{random.randint(1000,9999)}-{random.choice(['X','Y','Z'])}"
    ])
    reply_to = f"{sender_name} <{random.choice(['support','info','contact','noreply'])}@{sender_domain}>"
    unsubscribe_id = ''.join(random.choices('abcdef1234567890', k=10))
    unsubscribe_header = f'<mailto:unsubscribe@{sender_domain}?id={unsubscribe_id}>, <https://{sender_domain}/unsubscribe?id={unsubscribe_id}>'
    msg = MIMEMultipart('alternative')
    msg['From'] = f"{sender_name} <{from_email}>"
    msg['To'] = f"{recipient_name} <{email}>"
    msg['Subject'] = subject
    msg['Message-ID'] = message_id
    msg.add_header('X-Mailer', x_mailer)
    msg.add_header('Reply-To', reply_to)
    msg.add_header('List-Unsubscribe', unsubscribe_header)
    msg.add_header('X-Priority', str(config.get('x_priority', 3)))
    msg.add_header('X-MSMail-Priority', str(config.get('x_ms_mail_priority', 'Normal')))
    msg.add_header('X-Auto-Response-Suppress', 'OOF')
    msg.add_header('Precedence', 'bulk')
    msg.add_header('Auto-Submitted', 'auto-generated')
    msg.add_header('X-Pm-Origin', 'internal')
    msg.add_header('X-Pm-Content-Encryption', 'end-to-end')
    msg.add_header('X-Pm-Spamscore', '0')
    msg.add_header('List-Id', f"{sender_name} <{reply_to}>")
    msg.attach(MIMEText(plain_text, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    return msg

def main():
    email_delay = config.get('delay_per_email', 2)
    pause_after = config.get('pause_after', 100)
    pause_duration = config.get('pause_duration', 60)
    print(f"{Fore.YELLOW} [INFO] {Fore.CYAN}CONNECTING TO SMTP SERVER...{Style.RESET_ALL}")

    server = None
    try:
        context = ssl.create_default_context()
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, context=context)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
            server.ehlo()
            try:
                server.starttls(context=context)
                server.ehlo()
            except smtplib.SMTPException:
                print(f"{Fore.RED} [ERROR]{Fore.YELLOW} STARTTLS not supported or not needed on port {smtp_port}, continuing...{Style.RESET_ALL}")

        server.login(smtp_user, smtp_pass)

        counter = 0
        from_email = config['from_email']
        sender_domain = from_email.split('@')[1]
        today = datetime.today().strftime('%Y-%m-%d')

        print(f"{Fore.YELLOW} [INFO] {Fore.CYAN}AUTHENTICATED SUCCESSFULLY{Style.RESET_ALL}")
        print(f"{Fore.YELLOW} [INFO] {Fore.CYAN}STARTING EMAIL DELIVERY...{Style.RESET_ALL}")

        for email in emails:
            recipient_name = email.split('@')[0]
            subject_template = random.choice(raw_subjects)

            otp_code = ''.join(random.choices('0123456789', k=6))
            case_id = ''.join(random.choices('0123456789', k=7))
            ranum = generate_random_number()

            subject = subject_template.replace('{name}', recipient_name).replace('{date}', today)\
                .replace('{email}', email).replace('{otp}', otp_code)\
                .replace('{case_id}', case_id).replace('{ranum}', str(ranum))

            html_body = email_body_template.replace('{name}', recipient_name)\
                .replace('{url}', config['url'])\
                .replace('{email}', email).replace('{otp}', otp_code)\
                .replace('{case_id}', case_id).replace('{date}', today)\
                .replace('{ranum}', str(ranum))

            plain_text = html_to_plain_text(html_body)
            sender_name = random.choice(senders)
            msg = create_message(email, html_body, plain_text, subject, sender_name, from_email, sender_domain)
            server.send_message(msg)

            print(f"{Fore.GREEN}{Style.BRIGHT} [+] SENT => {Fore.CYAN}{email}{Style.RESET_ALL}")
            counter += 1
            time.sleep(email_delay)
            if pause_after > 0 and counter % pause_after == 0:
                print(f"{Fore.YELLOW} [INFO] {Fore.BLUE}PAUSING FOR {Fore.CYAN}{pause_duration} SECONDS...{Style.RESET_ALL}")
                time.sleep(pause_duration)

        print(f"{Fore.YELLOW} [INFO] {Fore.CYAN}ALL EMAILS SENT SUCCESSFULLY.{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED} [×] ERROR SENDING EMAIL: {str(e)}{Style.RESET_ALL}")
    finally:
        if server is not None:
            try:
                server.quit()
            except Exception:
                pass

if __name__ == "__main__":
    main()