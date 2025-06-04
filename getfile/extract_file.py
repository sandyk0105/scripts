import imaplib
import email
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")

def extract_file(user, password):
    imap_url = 'imap.gmail.com'
    my_mail = imaplib.IMAP4_SSL(imap_url)

    try:
        my_mail.login(user, password)

        my_mail.select('Inbox')

        today = datetime.now()
        yesterday = today - timedelta(days=1)
        yesterday_date_string = yesterday.strftime("%Y-%m-%d")

        # Create folder
        folder_name = today.strftime(f"Mail_Attachments")
        if not os.path.exists(folder_name):
            os.makedirs(folder_name, mode=0o777)
        folder_path = os.path.abspath(folder_name)

        # Filter
        # To be replaced with NUSFastPay's email
        search_query = f'(X-GM-RAW "has:attachment after:{yesterday_date_string} from:{SENDER_EMAIL}")'
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
                        if filename:
                            filepath = os.path.join(folder_path, filename)
                            with open(filepath, 'wb') as f:
                                f.write(part.get_payload(decode=True))
    except Exception as err:
        raise err
    finally:
        my_mail.logout()
