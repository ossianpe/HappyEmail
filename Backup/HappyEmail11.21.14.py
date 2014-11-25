import smtplib
import requests
import lxml.html
import urllib2
import time
import apiclient
import random
import shutil
import os
import math

from apiclient.discovery import build

from pprint import pprint

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage

#Local file imports
import vocab.word_banks as wbs
import secure.private_data as pd
import format.email as ef
import scrape.urls as ur

#List used for storing names of downloaded images so that image file containers will be known
files = []

def check_connection(test_url):
    try:
        response = urllib2.urlopen(test_url, timeout=1)
        print "Connected to \"" + test_url + " successfully."
    except urllib2.URLError as err:
        print "No connection to " + "\"" + test_url + "\"."
        exit()

def getURL(url):
    check_connection(url)
    r = requests.get(url)
    print ("Downloaded from " + str(url))
    return r

def remove_last_line_from_string(s):
    return s[:s.rfind('\n')]

#Retrives word of the day from url pulled by requests and parsed by lxml
def getScrape(word_url, word_selector):
    r = getURL(word_url)
    tree = lxml.html.fromstring(r.text)
    return str(tree.xpath(word_selector)).strip("[]\'\'")

#Retrives a quote from url pulled by requests and parsed by lxml
def getQuote():
    r = getURL(ur.RANDOM_QUOTE_URL)
    #Removes the last three lines (containing two whitespace and the URL source)
    quote_remove_source = remove_last_line_from_string(remove_last_line_from_string(remove_last_line_from_string(str(r.text))))
    #Replaces strange text with cleaner presentation
    quote_replace_chars = quote_remove_source.replace("&quot;", "\"")
    return quote_replace_chars

def makeIdiom():
    idiom = ""
    determine_str = random.randrange(0, 2, 1)
    #Generates first half of idiom based on plurals (string one holds single case, string two holds plural case)
    if determine_str == 0:
        determine_selection = random.randrange(0, len(wbs.RANDOM_IDIOM_START1), 1)
        idiom = wbs.RANDOM_IDIOM_START1[determine_selection] + " "
    if determine_str == 1:
        determine_selection = random.randrange(0, len(wbs.RANDOM_IDIOM_START2), 1)
        idiom = wbs.RANDOM_IDIOM_START2[determine_selection] + " "
    #Generates second half of idiom based on plurals (string one holds single case, string two holds plural case)
    if determine_str == 0:
        determine_selection = random.randrange(0, len(wbs.RANDOM_IDIOM_END1), 1)
        idiom = idiom + wbs.RANDOM_IDIOM_END1[determine_selection]
    if determine_str == 1:
        determine_selection = random.randrange(0, len(wbs.RANDOM_IDIOM_END2), 1)
        idiom = idiom + wbs.RANDOM_IDIOM_END2[determine_selection]
    return idiom

def pickPerson():
    determine_selection = random.randrange(0, len(wbs.RANDOM_NAME), 1)
    return wbs.RANDOM_NAME[determine_selection]

#Save word of day into variable so excessive URL fetches are not done
word_of_day = str(getScrape(ur.WORD_OF_DAY_URL, ur.WORD_OF_DAY_SELECTOR))

#Code is for pulling urls for a google image search
#NEED TO BUILD IN EXCEPTION ERROR FOR "googleapiclient.errors.HttpError"
def getImages():
    try:
        service = build("customsearch", "v1",
                       developerKey=pd.GCSEARCH_DEV_KEY)
        
        res = service.cse().list(
            q=word_of_day,
            cx=pd.GCSEARCH_CX,
            searchType='image',
            num=ef.NUMBER_OF_RESULTS,
            imgType='photo',
            fileType='png',
            safe= 'high'
        ).execute()
        
        if not 'items' in res:
            print('No result !!\nres is: {}'.format(res))
        else:
            images = []
            for item in res['items']:
                #print('{}:\n\t{}'.format(item['title'], item['link']))
                images.append(item['link'])
            return images            
    except apiclient.errors.HttpError, err:
        #Yeahhh this needs work
        print "STUPID HTTP API ERROR.."
        getImages()

#Downloads images from URL. Creates files in /images/ directory with name word of the day + current number of result
#   and file container. Prints download percentage.
#   https://gist.github.com/gourneau/1430932
def downloadImage(download_url, ii):
    baseFile = os.path.basename(download_url)
 
    #move the file to a more uniq path
    os.umask(0002)
    temp_path = "/images/"
    try:    
        #Create file based off of the word of the day, number of results, and the original file container
        find_container = download_url.split(".")
        container = find_container[-1]
        file_name = word_of_day + str(ii) + "." + str(container)
 
        req = urllib2.urlopen(download_url)
        total_size = int(req.info().getheader('Content-Length').strip())
        downloaded = 0
        CHUNK = 50 * 10240
        with open(file_name, 'wb') as fp:
            while True:
                chunk = req.read(CHUNK)
                downloaded += len(chunk)
                print "Downloading image " + file_name + " " + str(math.floor( (downloaded / total_size) * 100 )) + "%"
                if not chunk: break
                fp.write(chunk)
        files.append(file_name)
    except urllib2.HTTPError, e:
        print "HTTP Error:",e.code , download_url
        return False
    except urllib2.URLError, e:
        print "URL Error:",e.reason , download_url
        return False

downloadImage("http://upload.wikimedia.org/wikipedia/commons/d/d4/JPEG_example_image_decompressed.jpg", 1)
downloadImage("http://www.marinawimmer.co.uk/mental_imagery.png", 2)
downloadImage("http://upload.wikimedia.org/wikipedia/commons/3/3e/Phalaenopsis_JPEG.png", 3)

def downloadIterator():
    images = getImages()
    for ii in range(ef.NUMBER_OF_RESULTS):
        downloadImage(str(images[ii]), ii)

def randomFontType():
    determine_font = random.randrange(0, 5, 1)
    if determine_font == 0:
        return "arial"
    if determine_font == 1:
        return "braggadocio"
    if determine_font == 2:
        return "courier"
    if determine_font == 3:
        return "impact"
    if determine_font == 4:
        return "verdana"

def randomFontColor():
    determine_font_color = random.randrange(0, 5, 1)
    if determine_font_color == 0:
        return "black"
    if determine_font_color == 1:
        return "blue"
    if determine_font_color == 2:
        return "red"
    if determine_font_color == 3:
        return "green"
    if determine_font_color == 4:
        return "brown"
    

#Assembles email using HTML
def createBodyOfEmail():
    content = ""
    for ii in range(ef.NUMBER_OF_RESULTS):
        content = (content
            + "<font face=\"" + randomFontType() + "\" " + "color=\"" + randomFontColor() + "\" " + "size=\"" + str(ef.EMAIL_FONT_SIZE) + "\">" + getQuote() + "</font>\n"
            + "<br><img src=\"cid:image" + str(ii) + "\"><br>"
            + "<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>")
        time.sleep(1)
    return content

ALL_RECIPIENTS = ['cephasara@gmail.com']
#, 'purpleblouse22@yahoo.com']

email_subject = "\"" + str(makeIdiom()) + "\"" + " --" + pickPerson() + " [" + word_of_day + "]"
body_of_email = createBodyOfEmail()

print email_subject + "\n"
print body_of_email

class Email:
    def __init__(self, gmail_sender_username, gmail_sender_password):
        self.gmail_sender_username = gmail_sender_username
        self.gmail_sender_password = gmail_sender_password
        self.msgRoot = MIMEMultipart('related')
        self.msgAlternative = MIMEMultipart('alternative')
        self.msgText = MIMEText('This is the alternative plain text message.')
        self.msgPicText = MIMEText(body_of_email, 'html')
    #Sends email without pictures.
    def build_email(recipient):
        # The below code never changes, though obviously those variables need values.
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.ehlo()
        session.starttls()
        session.login(self.gmail_sender_username, self.gmail_sender_password)
        
        headers = "\r\n".join(["from: " + self.gmail_sender_username,
                               "subject: " + email_subject,
                               "to: " + RECIPIENT,
                               "mime-version: 1.0",
                               "content-type: text/html"])
        
        # body_of_email can be plaintext or html!                    
        content = headers + "\r\n\r\n" + body_of_email
        session.sendmail(self.gmail_sender_username, recipient, content)
        
    #Sends pictures with email. Requires local picture download first.
    #  Look into this site for bypassing local download:
    #    http://code.activestate.com/recipes/473851-compose-html-mail-with-embedded-images-from-url-or/
    def build_picture_email(self, recipient):
        # Create the root message and fill in the from, to, and subject headers
        self.msgRoot['Subject'] = email_subject
        self.msgRoot['From'] = self.gmail_sender_username
        self.msgRoot['To'] = recipient
        self.msgRoot.preamble = 'This is a multi-part message in MIME format.'
        
        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.

        self.msgRoot.attach(self.msgAlternative)
        
        
        self.msgAlternative.attach(self.msgText)
        
        # We reference the image in the IMG SRC attribute by the ID we give it below

        self.msgAlternative.attach(self.msgPicText)
        
        # This example assumes the image is in the current directory
        for ii in range(ef.NUMBER_OF_RESULTS):
            fp = open(files[ii], 'rb')
            msgImage = MIMEImage(fp.read())
            print "Successfully added image " + files[ii]
            fp.close()
            # Define the image's ID as referenced above
            msgImage.add_header('Content-ID', '<image' + str(ii) + '>')
            self.msgRoot.attach(msgImage)
        
        # Send the email (this example assumes SMTP authentication is required)
        print "Sent Picture Email!"
        
    def send_email(self, recipient):
        smtp = smtplib.SMTP()
        smtp.connect('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()
        print "Connected to gmail smtp server"
        smtp.login(self.gmail_sender_username, self.gmail_sender_password)
        print "Logged into account"
        print "Sending mail to " + str(recipient)
        smtp.sendmail(self.gmail_sender_username, str(recipient), self.msgRoot.as_string())
        smtp.quit()
        
    #Sends emails to everyone in list, will need to change for database
    def mail_all():
        for ii in range(len(ALL_RECIPIENTS)):
            build_picture_email(str(ALL_RECIPIENTS[ii]))
            send_email(str(ALL_RECIPIENTS[ii]))

#downloadIterator()
mail = Email(pd.GMAIL_SENDER_USERNAME, pd.GMAIL_SENDER_PASSWORD)
mail.build_picture_email(str(ALL_RECIPIENTS[0]))
mail.send_email(str(ALL_RECIPIENTS[0]))
#mailAll()