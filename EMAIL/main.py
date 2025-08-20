import imaplib
import smtplib
from email.mime.text import MIMEText
from flanker import mime
from datetime import datetime, timedelta
from flask import Flask,render_template

app = Flask(__name__, template_folder="frontend")

# -------------------CONFIG----------------------------
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ACCOUNT = 'thendralraj1901@gmail.com'
EMAIL_PASSWORD = 'urwd dywh mzrg bkqq'
three_weeks_ago = (datetime.now() - timedelta(weeks=3)).strftime("%d-%b-%Y")

#define categories and keywords
CATEGORIES = {
    'Jobs': ['job', 'career', 'vacancy'],
    'Job Alerts': ['job alert', 'job opening', 'job listing'],
    'Job Applications': ['job application', 'resume', 'cover letter','Assessment','interview'],
    "Confirmations": ["confirm", "acknowledgment", "received"]
}

#------------------------CONNECT IMAP------------------------
mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
mail.select('inbox')

status, messages = mail.search(None, f'(SINCE {three_weeks_ago})')
email_ids = messages[0].split()

for email_id in email_ids:
    status, msg_data = mail.fetch(email_id, '(RFC822)')
    raw_email = msg_data[0][1]

    #parse email using flanker
    msg = mime.from_string(raw_email.decode())
    subject = msg.subject.lower() if msg.subject else ""
    from_email = msg.headers.get("from")

    body = msg.body.lower() if msg.body else ""
    content = (subject + " " + body).lower()

    category_found = None
    for cat, keywords in CATEGORIES.items():
        if any(k in content for k in keywords):
            category_found = cat
            break

    print(f"From: {from_email}\nSubject: {subject}\nCategory: {category_found}\n")


#------------------------AUTOMATED REPLY------------------------
if category_found == "Confirmations":
        reply = MIMEText("Thank you for your email. Your application has been received.")
        reply["Subject"] = f"Re: {msg.subject}"
        reply["From"] = EMAIL_ACCOUNT
        reply["To"] = from_email

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ACCOUNT, from_email, reply.as_string())
        server.quit()

    # Optional: move email to folder/label (Gmail example)
    # mail.store(eid, '+X-GM-LABELS', category_found)

mail.logout()
print("Done processing emails!")

#------------------------------APIS--------------------------------
