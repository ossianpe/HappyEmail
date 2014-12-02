import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage

from lib.various_utilities_lib import VariousUtilities

varutil = VariousUtilities()

class Email:
    def __init__(self, gmail_sender_username, gmail_sender_password, emai_subj, bod_of_em):
        self.gmail_sender_username = gmail_sender_username
        self.gmail_sender_password = gmail_sender_password
        self.msgAlternative = MIMEMultipart('alternative')
        self.msgText = MIMEText('This is the alternative plain text message.')
        self.msgPicText = MIMEText(bod_of_em, 'html')
        self.email_subject = emai_subj
        self.msgRoot = MIMEMultipart('related')
    #Sends email without pictures.
    def build_email(self, recipient):
        # The below code never changes, though obviously those variables need values.
        self.msgRoot = "\r\n".join(["from: " + self.gmail_sender_username,
                               "subject: " + email_subject,
                               "to: " + recipient,
                               "mime-version: 1.0",
                               "content-type: text/html"])
        
        # body_of_email can be plaintext or html!                    
        content = headers + "\r\n\r\n" + body_of_email
        
    #Sends pictures with email. Requires local picture download first.
    #  Look into this site for bypassing local download:
    #    http://code.activestate.com/recipes/473851-compose-html-mail-with-embedded-images-from-url-or/
    def build_picture_email(self, relative_directory, num_of_results, image_store_location, files_list):
        # Create the root message and fill in the from, to, and subject headers

        self.msgRoot['From'] = self.gmail_sender_username
        self.msgRoot['Subject'] = self.email_subject

        self.msgRoot.preamble = 'This is a multi-part message in MIME format.'
        
        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.

        self.msgRoot.attach(self.msgAlternative)
        self.msgAlternative.attach(self.msgText)
        
        # We reference the image in the IMG SRC attribute by the ID we give it below

        self.msgAlternative.attach(self.msgPicText)
        
        # This example assumes the image is in the current directory
        for ii in range(num_of_results):
            fp = open(varutil.open_subdirectory(relative_directory, image_store_location, files_list[ii]), 'rb')
            msgImage = MIMEImage(fp.read())
            print "Successfully added image " + files_list[ii]
            fp.close()
            # Define the image's ID as referenced above
            msgImage.add_header('Content-ID', '<image' + str(ii) + '>')
            self.msgRoot.attach(msgImage)
        
        # Send the email (this example assumes SMTP authentication is required)
        
    def send_email(self, recipient):
        try:
            self.msgRoot['To'] = recipient
            smtp = smtplib.SMTP()
            smtp.connect('smtp.gmail.com', 587)
            smtp.ehlo()
            smtp.starttls()
            print "Connected to gmail smtp server"
            smtp.login(self.gmail_sender_username, self.gmail_sender_password)
            print "Logged into " + self.gmail_sender_username + " account"
            print "Sending mail to " + str(recipient)
            smtp.sendmail(self.gmail_sender_username, str(recipient), self.msgRoot.as_string())
            smtp.quit()

            #Removes 'To' key so email recpients will not see each other
            del self.msgRoot['To']

        except KeyError:
            print "Couldn't find the \'To\' key in msgRoot"
        
    #Sends emails to everyone in list, will need to change for database
    def picture_mail_all_list(self, relative_directory, num_of_results, image_store_location, list_of_recips, files_list):
        self.build_picture_email(relative_directory, num_of_results, image_store_location, files_list)
        for ii in range(len(list_of_recips)):
            self.send_email(str(list_of_recips))
            print "Sent Picture Email!"

    def picture_mail_all(self, relative_directory, num_of_results, image_store_location, all_recips, files_list):
        self.build_picture_email(relative_directory, num_of_results, image_store_location, files_list)
        for ii in all_recips:
            if ii["Subscribed"].find("Yes")!=-1:
                self.send_email(ii["Address"])
                print "Sent Picture Email!"