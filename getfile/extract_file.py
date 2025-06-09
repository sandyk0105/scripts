import imaplib
import email
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

CSV_RECEIVER_EMAIL = os.getenv("CSV_RECEIVER_EMAIL")
CSV_RECEIVER_PASSWORD = os.getenv("CSV_RECEIVER_PASSWORD")
CSV_SENDER_EMAIL = os.getenv("CSV_SENDER_EMAIL")

def extract_file(folder_path):
    imap_url = 'imap.gmail.com'
    my_mail = imaplib.IMAP4_SSL(imap_url)

    files_extracted = []

    try:
        my_mail.login(CSV_RECEIVER_EMAIL, CSV_RECEIVER_PASSWORD)

        # Assumes the mail does not go to spam
        my_mail.select('INBOX', readonly=True)

        today = datetime.now()
        yesterday = today - timedelta(days=1)
        yesterday_date_string = yesterday.strftime("%Y-%m-%d")

        # Filter
        # To be replaced with NUSFastPay's email
        search_query = f'(X-GM-RAW "has:attachment after:{yesterday_date_string} from:{CSV_SENDER_EMAIL}")'
        _, data = my_mail.search(None, search_query)

        mail_id_list = data[0].split() # IDs of all emails we want to fetch

        raw_emails = [] # Empty list to capture all messages
        for num in mail_id_list:
            typ, data = my_mail.fetch(num, '(RFC822)') # Fetch the whole message
            raw_emails.append(data)

        for raw_email in raw_emails:
            for response_part in raw_email:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    for part in msg.walk():
                        if part.get_content_maintype() == 'multipart':
                            continue
                        if part.get('Content-Disposition') is None:
                            continue

                        filename = part.get_filename()
                        if filename and filename.endswith(".csv"):
                            filepath = os.path.join(folder_path, filename)
                            with open(filepath, 'wb') as f:
                                f.write(part.get_payload(decode=True))
                            files_extracted.append(filepath)
        
        return files_extracted
    except Exception as err:
        raise err
    finally:
        my_mail.logout()
