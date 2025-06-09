
Hermes Sender - Feature Explanation
===================================

📁 Folder Structure:
--------------------
hermes-sender-main/
├── config.json                  - Main configuration file for sender behavior
├── main.pyc                     - Compiled Python code (main logic)
├── requirements.txt             - Lists Python dependencies
├── config/
│   ├── senders.txt              - List of sender names
│   └── subjects.txt             - List of email subject lines used randomly
├── images/
│   ├── images.png              - Logo used in email template              - Warning icon for alert-styled emails
├── letter/
│   ├── letter.html             - HTML phishing-style template for Binance                 - HTML template for One-Time Password/2FA alert
├── list/
│   └── mailist.txt                 - File containing list of target email addresses

✅ Feature Overview:
---------------------
1. 🔄 Rotating Senders:
   - Pulls fake or multiple sender identities from config/senders.txt.
   - Helps bypass spam filters and increases legitimacy.

2. ✉️ Subject Line Randomization:
   - Loads different subject lines from config/subjects.txt.
   - Avoids pattern-based spam detection.

3. 💌 HTML Email Templates:
   - Professional-looking templates impersonate popular services.
   - Email content is styled and pre-written in letter/*.html.

4. 🖼️ Embedded Images:
   - Brand logos included to mimic real emails.
   - Images stored in /images and referenced in the HTML files.

5. 📄 Target Email List:
   - Email list stored in /list/test.txt.
   - Each line is a separate target email address.

6. ⚙️ Custom Configuration:
   - Behavior and options are adjustable via config.json (e.g., limits, delays).

7. 📜 Python Dependency Setup:
   - requirements.txt used to set up the Python environment.
   - Can be installed with: pip install -r requirements.txt

Happy spamming :)

