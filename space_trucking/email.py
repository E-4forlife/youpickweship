import boto3
from botocore.exceptions import ClientError
import re

class Email(object):
    def __init__(self, sender, recipient, body_text):
        # This address must be verified with Amazon SES.
        self.sender = sender
        # Replace recipient@example.com with a "To" address. If your account 
        # is still in the sandbox, this address must be verified.
        self.recipient  = recipient
        self.aws_region = "us-east-1"
        # The character encoding for the email.
        self.charset = "UTF-8"
        # The subject line for the email.
        self.subject = "Incoming Order"
        # The email body for recipients with non-HTML email clients.
        self.body_text = body_text
        # regex to give body text html line breaks
        self.body_html = re.sub("\/n", "<br/>", body_text) 
        # Create a new SES resource and specify a region.
        self.client = boto3.client('ses',region_name=self.aws_region)

    def send(self):
        # Try to send the email.

        try:
            #Provide the contents of the email.
            response = self.client.send_email(
            Destination={
                    'ToAddresses': [
                        self.recipient,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': self.charset,
                            'Data': self.body_html,
                        },
                        'Text': {
                            'Charset': self.charset,
                            'Data': self.body_text,
                        },
                    },
                    'Subject': {
                        'Charset': self.charset,
                       'Data': self.subject,
                    },
                },
                Source=self.sender,
            )
        # Display an error if something goes wrong.	
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])

