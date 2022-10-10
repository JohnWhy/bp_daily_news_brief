# import the required libraries
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import base64
from bs4 import BeautifulSoup

# Define the SCOPES. If modifying it, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def connectGmail():
    # Variable creds will store the user access token.
    # If no valid token found, we will create one.
    creds = None

    # The file token.pickle contains the user access token.
    # Check if it exists
    if os.path.exists('token.pickle'):
        # Read the token from the file and store it in the variable creds
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If credentials are not available or are invalid, ask the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the access token in token.pickle file for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Connect to the Gmail API
    service = build('gmail', 'v1', credentials=creds)

    return service


def getEmails():
    service = connectGmail()
    # request a list of all the messages
    result = service.users().messages().list(userId='me').execute()

    # We can also pass maxResults to get any number of emails. Like this:
    # result = service.users().messages().list(maxResults=200, userId='me').execute()
    messages = result.get('messages')
    # messages is a list of dictionaries where each dictionary contains a message id.

    # iterate through all the messages
    emails = []
    for msg in messages:
        # Get the message from its id
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()

        # Use try-except to avoid any Errors
        # Get value of 'payload' from dictionary 'txt'
        payload = txt['payload']
        headers = payload['headers']

        # Look for Subject and Sender Email in the headers
        for d in headers:
            if d['name'] == 'Subject':
                subject = d['value']
            if d['name'] == 'From':
                sender = d['value']
        if '<dailybrief@e.cfr.org>' in sender:
            # print('found email')
            data = payload['parts'][0]['body']['data']
            data = data.replace("-", "+").replace("_", "/")
            decoded_data = base64.b64decode(data)

            # Now, the data obtained is in lxml. So, we will parse
            # it with BeautifulSoup library
            soup = BeautifulSoup(decoded_data, 'html.parser')
            body = soup.body()
            emails.append({'subject': subject,
                           'sender': sender,
                           'body': body,
                           'decoded': decoded_data})
    return emails


def parse_body(body):
    soup = BeautifulSoup(body, 'html.parser')
    r = soup.find_all('span', style="font-size:13px;")
    sections = []
    for i in r:
        sections.append(i.getText())

    all_stories = []
    headlines = soup.find_all('h1')
    texts = soup.find_all('div', style="font-family:sans-serif")
    regions = soup.find_all('span', style="font-size:13px;")
    texts.remove(texts[0])  # remove date
    texts.remove(texts[-1])  # remove Email preferences
    final_texts = []
    for i in texts:
        if i.getText() == 'Analysis':  # remove any analysis and it's associated text
            texts.remove(texts[texts.index(i) + 1])
            texts.remove(texts[texts.index(i)])
    for i in texts:
        text = i.getText()
        links = i.find_all('a')
        for link in links:
            linkText = '['+link.getText()+']('
            url = link.get('href')+')'
            text = text.replace(link.getText(), linkText+url)
        final_texts.append(text)
    for i in headlines:
        try:
            all_stories.append({'header': i.getText(),
                                'text': final_texts[headlines.index(i)],
                                'region': regions[headlines.index(i)].getText()})
        except:
            pass
    return all_stories


# def get_link(body, date):
#     links = body.split('"')
#     for i in links:
#         if 'https://www.worldpoliticsreview.com/news-wire/'+date in i:
#             return i
