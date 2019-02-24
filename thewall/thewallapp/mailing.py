import os
import unittest

import sendgrid
from rest_framework import status
from sendgrid import Email
from sendgrid.helpers.mail import Mail, Content


"""
For this mailing module to work, you need to follow the next steps:
1- Create a sendgrid account.
2- Create an API Key for your application. The API Key requires, at least, Full access to Mail Send.
3- Set the env variable 'SG_APIKEY' value to the API Key obtained in step 2
"""

def send_emails(from_email,to_email,subject,message):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SG_APIKEY'))
    from_email = Email(from_email)
    to_email = Email(to_email)
    subject = subject
    content = Content("text/plain", message)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response.status_code,response.body,response.headers


class MailTest(unittest.TestCase):
    @unittest.skipIf('SG_APIKEY' not in os.environ,'You need to set the SG_APIKEY env variable first.'
                                                   'Check the module for documentation')
    def test_mail_test(self):
        status_code,body,headers = send_emails('noreply@thewallapp.com','test@test.com','Test','This is a test')
        self.assertEqual(status_code,status.HTTP_202_ACCEPTED)


if __name__ == "__main__":
    unittest.main()