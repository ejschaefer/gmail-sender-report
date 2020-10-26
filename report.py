import pickle
import os.path, re, sys
import sqlite3
import logging
import argparse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request



logger = logging.getLogger()
logger.setLevel(logging.INFO)

def init_database(database):
    conn = None
    try: 
        conn = sqlite3.connect(database)
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS messages 
            (
                message_id text,
                from_address text,
                UNIQUE(message_id)
            );
            """)

        conn.commit()
        conn.row_factory = sqlite3.Row
    except:
        logger.error("Error connecting to Sqlite DB: {}".format(e))
    
    return conn


def init_service(credentials_file):
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('gmail', 'v1', credentials=creds)    
    
    return service


def get_messages_from_api(query="label:inbox"):
    messages = []
    try:
        response = service.users().messages().list(userId='me', q=query).execute()
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId='me', q=query,
                pageToken=page_token).execute()
            messages.extend(response['messages'])
    except HttpError as he:
        logger.error("HttpError received when retrieving messages: {}".format(he.error_details))

    return messages


def get_messages_from_db():
    try:
        c = conn.cursor()
        c.execute("SELECT * from messages where from_address is null")
        return c.fetchall()
    except Error as e:
        logger.error("Error retrieving messages from database: {}".format(e))


def store_messages_in_db(messages):
    messageDb = []
    for message in messages:
        m = (message['id'], None)
        messageDb.append(m)
    try:
        c = conn.cursor()
        c.executemany('INSERT OR IGNORE INTO messages VALUES (?,?)', messageDb)
        conn.commit()
    except Error as e:
        logger.error("Error storing messages in DB: {}".format(e))

    
def store_message_data(message_id, from_address):
    try:
        c = conn.cursor()
        data = (from_address,message_id,)
        c.execute('UPDATE messages set from_address = ? where message_id = ?', data)
        conn.commit()
    except Error as e:
        logger.error("Error updating messages in DB: {}".format(e))
    

def extract_email_address(email_address):
    regex = '<.+>'
    real_address = re.search(regex, email_address)[0]
    return real_address.replace('<', '').replace('>', '')

def get_message_details(message_id):

    try:
        msgRes = service.users().messages().get(userId='me', id=message_id, format='metadata').execute(num_retries=5)
        msgHeaders = msgRes['payload']['headers']
        msgFrom = next(item for item in msgHeaders if item["name"].upper() == "FROM")
        if '<' in msgFrom['value']:
            from_address = extract_email_address(msgFrom['value'])
        else:
            from_address = msgFrom['value']
        
    except HttpError as he:
        print("HttpError received: {}".format(he.error_details))
        print("HttpError received: {}".format(he.content))

    return {'message_id': message_id, 'from_address': from_address}

def get_message_senders():
    try:
        c = conn.cursor()
        c.execute("SELECT count(*) as total, from_address FROM messages GROUP BY from_address ORDER BY total DESC")
        return c.fetchall()
    except Error as e:
        logger.error("Error retrieving messages from database: {}".format(e))


def generate_report(message_results):
    from jinja2 import Environment, FileSystemLoader
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('sender_report.html')
    output = template.render(messages=message_results)
    
    with open("report-output.html", "w") as fh:
        fh.write(output)

    print("Email Senders report written to 'report-output.html'")



database = 'gmail.db'
conn = init_database(database) # Initialize SQLite db connection and table

credentials_file="credentials.json" # OAuth2 clientId, client secret, etc
service = init_service(credentials_file) # Initialize Google API credentials and 

    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--seed",
        help="Seed the database with message IDs from Gmail API",
        default=False,
        action="store_true"
    )

    parser.add_argument(
        "--report-only", '-r',
        dest="report",
        help="Render the email sender report from database",
        default=False,
        action="store_true"
    )

    args = parser.parse_args()


    if args.report:
        message_details = get_message_senders()
        generate_report(message_details)


    else:
        if args.seed:
            logger.info("Getting message from Gmail API")
            messages = get_messages_from_api()
            store_messages_in_db(messages)

        messages = get_messages_from_db()

        for message in messages:
            message_id = message['message_id']
            details = get_message_details(message_id)
            
            logger.info(details) # outputting to stdout just-in-case
            store_message_data(details['message_id'], details['from_address'])

            message_details = get_message_senders()
            generate_report(message_details)


if __name__ == '__main__':
    main()