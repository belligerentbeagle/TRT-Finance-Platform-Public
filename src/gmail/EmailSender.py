import os.path
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email import encoders
import mimetypes
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",'https://www.googleapis.com/auth/gmail.send','https://www.googleapis.com/auth/gmail.modify']

def test_api():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = authenticate_user()

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])

    if not labels:
      print("No labels found.")
      return
    print("Labels:")
    for label in labels:
      print(label["name"])

  except HttpError as error:
    print(f"An error occurred: {error}")

def authenticate_user():
  creds = None

  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("./config/token.json"):
    creds = Credentials.from_authorized_user_file("./config/token.json", SCOPES)

  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      try:
          creds.refresh(Request())
      except Exception as e:
          print("Error refreshing credentials:", e)
          creds = None
    if not creds:
      flow = InstalledAppFlow.from_client_secrets_file(
        "./config/credentials.json", SCOPES)
      creds = flow.run_local_server(port=0)

      # Save the credentials for the next run
      with open("./config/token.json", "w") as token:
        token.write(creds.to_json())

  return creds


def send_message(recipientEmail="", subject="", body="", pdf_file_path=None):
  """Create and send an HTML email message with optional PDF attachment"""
  print("authenticating user")
  creds = authenticate_user()

  try:
      service = build("gmail", "v1", credentials=creds)
      
      # Create MIME Multipart message
      message = MIMEMultipart('mixed')  # Change to mixed for attachments
      message["To"] = recipientEmail
      message["From"] = "gduser2@workspacesamples.dev"
      message["Subject"] = subject

      # Create alternative part for plain/html
      alt_part = MIMEMultipart('alternative')
      
      # Convert plain text to HTML with compact template
      html_template = '''<!DOCTYPE html>
          <html>
          <head>
          
          </head>
          <body>
          {}
          </body>
          </html>
          '''
      
      # Format HTML body with replaced newlines
      html_body = html_template.format(body.replace('\n', '<br>'))

      # Create both plain text and HTML versions
      text_part = MIMEText(body, 'plain', 'utf-8')
      html_part = MIMEText(html_body, 'html', 'utf-8')

      # Add parts to alternative container
      alt_part.attach(text_part)
      alt_part.attach(html_part)
      
      # Add alternative container to message
      message.attach(alt_part)

      # If there is a PDF file, attach it
      if pdf_file_path:
          with open(pdf_file_path, 'rb') as fp:
              pdf_part = MIMEApplication(fp.read(), _subtype='pdf')
              pdf_part.add_header(
                  'Content-Disposition',
                  'attachment',
                  filename=os.path.basename(pdf_file_path)
              )
              message.attach(pdf_part)

      # Create raw message
      raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
      
      # Send the email
      send_message = service.users().messages().send(
          userId="me",
          body={'raw': raw_message}
      ).execute()
      
      return send_message
  except HttpError as error:
    send_message = None
    st.error("Email failed to send: ", send_message)
    return send_message

# def emailSender():
#   # test_api()
#   message_sent = send_message("ethanweibiz@gmail.com")
  
