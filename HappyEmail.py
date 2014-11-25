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
import sys

from apiclient.discovery import build
from pprint import pprint
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage

from data.database import Database

#Local file imports
import data.vocab.word_banks as wbs
import data.secure.private_data as pd
import data.content.email as ef
import data.content.search as ser
import data.scrape.urls as ur

#List used for storing names of downloaded images so that image file containers will be known
files = []

def check_connection(test_url):
    try:
        response = urllib2.urlopen(test_url, timeout=1)
        print "Connected to \"" + test_url + " successfully."
    except urllib2.URLError as err:
        print "No connection to " + "\"" + test_url + "\". Hmm..."
        exit()

def open_subdirectory(subdir, file_name):
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    rel_path = subdir + file_name
    return os.path.join(script_dir, rel_path)

def check_file(file_name_and_location):
    if os.path.isfile(file_name_and_location):
        return "true"
    else:
        print "Error: Missing Database"
        time.sleep(1)
        return "false"

class FrequentVariables:
    def __init__(self):
        word_of_day = ""
        files = []
        lenght_of_database_table = 0
    def set_wod(self, wod):
        self.word_of_day = wod
    def get_wod(self):
        return self.word_of_day
    def set_files(self, fil):
        self.files = fil
    def get_files(self):
        return self.files
    def set_length_of_database_table(self, lodt):
        temp_lodt_str = ""
        temp_lodt_str = str(lodt).replace("(", "").replace(",", "").replace(")", "")
        self.length_of_database_table = int(temp_lodt_str)
    def get_length_of_database_table(self):
        return self.length_of_database_table

class BuildContent:
    #is self correct here??
    def get_URL(self, url):
        check_connection(url)
        r = requests.get(url)
        print ("Downloaded from " + str(url))
        return r
    
    def remove_last_line_from_string(self, s):
        return s[:s.rfind('\n')]
    
    #Retrives word of the day from url pulled by requests and parsed by lxml
    def get_scrape(self, word_url, word_selector):
        r = self.get_URL(word_url)
        tree = lxml.html.fromstring(r.text)
        return str(tree.xpath(word_selector)).strip("[]\'\'")
    
    #Retrives a quote from url pulled by requests and parsed by lxml
    def get_quote(self):
        try:
            r = self.get_URL(ur.RANDOM_QUOTE_URL)
            while len(r.text)>ef.MAX_QUOTE_SIZE:
                print "Quote is too long. " + str(len(r.text)) + " > 300 characters. Scraping again."
                r = self.get_URL(ur.RANDOM_QUOTE_URL)
            #Removes the last three lines (containing two whitespace and the URL source)
            #NEED TO FIX THIS
            #Think it's fixed.. nope
            '''
            Traceback (most recent call last):
              File "HappyEmail.py", line 415, in <module>
                buildform.create_body_of_email(buildcont.get_quote(), ii)
              File "HappyEmail.py", line 109, in get_quote
                self.remove_last_line_from_string(str(r.text))))
            UnicodeEncodeError: 'ascii' codec can't encode characters in position 140-141: ordinal not in range(128)
            '''
            #Removes website source
            quote_remove_source = self.remove_last_line_from_string(
                                    self.remove_last_line_from_string(
                                        self.remove_last_line_from_string(str(r.text))))
            
            #Replaces strange text with cleaner presentation
            quote_replace_chars = quote_remove_source.replace("&quot;", "\"")
            return quote_replace_chars
        except UnicodeEncodeError, err:
            print "Unicode Encode Error.. trying again."
            self.get_quote()
    
    def make_idiom(self):
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
    
    def pick_person(self):
        determine_selection = random.randrange(0, len(wbs.RANDOM_NAME), 1)
        return wbs.RANDOM_NAME[determine_selection]

class Image:
    def __init__(self):
        self.wod = ""
    def set_wod(self, wor_of_da):
        self.wod = wor_of_da
    #Code is for pulling urls for a google image search
    def get_image_URLs(self):
        try:
            service = build("customsearch", "v1",
                           developerKey=pd.GCSEARCH_DEV_KEY)
            res = service.cse().list(
                q=self.wod,
                cx=pd.GCSEARCH_CX,
                searchType=ser.SEARCH_TYPE,
                num=ef.NUMBER_OF_RESULTS,
                imgType=ser.IMAGE_TYPE,
                fileType=ser.FILE_TYPE,
                safe= ser.SAFE_SEARCH
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
            #Yeahhh this needs work..
            print "STUPID HTTP API ERROR.."
            time.sleep(2)
            self.get_image_URLs()
    
    #Downloads images from URL. Creates files in /images/ directory with name word of the day + current number of result
    #   and file container. Prints download percentage.
    #   https://gist.github.com/gourneau/1430932
    def download_image(self, download_url, ii):
        baseFile = os.path.basename(download_url)
        #move the file to a more uniq path
        os.umask(0002)
        try:    
            #Create file based off of the word of the day, number of results, and the original file container
            find_container = download_url.split(".")
            container = find_container[-1]
            file_name = self.wod + str(ii) + "." + str(container)
     
            req = urllib2.urlopen(download_url)
            total_size = int(req.info().getheader('Content-Length').strip())
            downloaded = 0
            CHUNK = 50 * 10240
            
            with open(open_subdirectory("storage/images/", file_name), 'wb') as fp:
                while True:
                    chunk = req.read(CHUNK)
                    downloaded += len(chunk)
                    print "Downloading image " + file_name + " " + str(math.floor( (downloaded / total_size) * 100 )) + "%"
                    if not chunk: break
                    fp.write(chunk)
            files.append(file_name)
        except urllib2.HTTPError, e:
            print "HTTP Error:",e.code , download_url, "Image Download Failed."
            return False
        except urllib2.URLError, e:
            print "URL Error:",e.reason , download_url, "Image Download Failed."
            return False

    def download_iterator(self):
        images = self.get_image_URLs()
        for ii in range(ef.NUMBER_OF_RESULTS):
            self.download_image(str(images[ii]), ii)

class BuildFormatting:
    def __init__(self):
        self.content = ""
        self.email_subject = ""
        
    def random_font_type(self):
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
    
    def random_font_color(self):
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
    
    def create_email_subject(self, idiom, famous_person, wor_of_da):
        self.email_subject = "\"" + str(idiom) + "\"" + " --" + famous_person + " [" + wor_of_da + "]"
    
    def get_email_subject(self):
        return self.email_subject
    
    #Assembles email using HTML
    def create_body_of_email(self, quote, num_of_res):
        self.content = (self.content
            + "<font face=\"" + self.random_font_type() + "\" " + "color=\"" + self.random_font_color()
            + "\" " + "size=\"" + str(ef.EMAIL_FONT_SIZE) + "\">" + str(quote) + "</font>\n"
            + "<br><img src=\"cid:image" + str(num_of_res) + "\"><br>"
            + "<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>")
        time.sleep(1)
    def get_body_of_email(self):
        return self.content
    
class Email:
    def __init__(self, gmail_sender_username, gmail_sender_password, emai_subj, bod_of_em):
        self.gmail_sender_username = gmail_sender_username
        self.gmail_sender_password = gmail_sender_password
        self.msgRoot = MIMEMultipart('related')
        self.msgAlternative = MIMEMultipart('alternative')
        self.msgText = MIMEText('This is the alternative plain text message.')
        self.msgPicText = MIMEText(bod_of_em, 'html')
        self.email_subject = emai_subj
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
    def build_picture_email(self, num_of_results):
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
            fp = open(open_subdirectory("storage/images/", files[ii]), 'rb')
            msgImage = MIMEImage(fp.read())
            print "Successfully added image " + files[ii]
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
            print "Logged into account"
            print "Sending mail to " + str(recipient)
            smtp.sendmail(self.gmail_sender_username, str(recipient), self.msgRoot.as_string())
            smtp.quit()

            #Removes 'To' key so email recpients will not see each other
            del self.msgRoot['To']

        except KeyError:
            print "Couldn't find the \'To\' key in msgRoot"
        
    #Sends emails to everyone in list, will need to change for database
    def picture_mail_all_list(self, num_of_results):
        self.build_picture_email(num_of_results)
        for ii in range(len(pd.ALL_RECIPIENTS)):
            self.send_email(str(pd.ALL_RECIPIENTS[ii]))
            print "Sent Picture Email!"

    def picture_mail_all(self, num_of_results, all_recips):
        self.build_picture_email(num_of_results)
        for ii in all_recips:
            if ii["Subscribed"].find("Yes")!=-1:
                self.send_email(ii["Address"])
                print "Sent Picture Email!"

#Use this mode for testing.. can easily go over Google Custom Search API limit of 100 daily searches.
# Also, debug test images have a small file size allowing for quicker emailing for testing.
debug_mode = "true"

freqv = FrequentVariables()

database_check = ""
database_check = check_file(pd.EMAIL_ADDRESS_DB)

if database_check == "true":
    sqldb = Database()
    sqldb.connect(pd.EMAIL_ADDRESS_DB)
    sqldb.set_selected_table(pd.EMAIL_ADDRESS_CONTACTS_TABLE)
    print "Found existing database " + pd.EMAIL_ADDRESS_DB
elif database_check == "false":
    sqldb = Database()
    sqldb.connect(pd.EMAIL_ADDRESS_DB)
    print "Created new database " + pd.EMAIL_ADDRESS_DB_FILENAME
    sqldb.set_selected_table(pd.EMAIL_ADDRESS_CONTACTS_TABLE)
    sqldb.create_table('Address TEXT, Name TEXT, Subscribed TEXT')
    print "Created " + sqldb.get_selected_table() + " table."

freqv.set_length_of_database_table(sqldb.get_length_of_table())

if freqv.get_length_of_database_table()==0:
    print ("Length of " + sqldb.get_selected_table() + " table in " + pd.EMAIL_ADDRESS_DB_FILENAME
        + " is zero")
    print ""
    print "****************************************************************************"
    print "**Please add some email addresses to " + pd.EMAIL_ADDRESS_DB + "**"
    print "****************************************************************************"
    print "To do so.. type the following in a terminal window:"
    print "\"sqlite3 " + pd.EMAIL_ADDRESS_DB + "\""
    print "\"INSERT INTO " + pd.EMAIL_ADDRESS_CONTACTS_TABLE + " VALUES('insertyouremailaddresshere', 'Nameofperson', 'Subscriptionstatus')\""
    print "****************************************************************************"
    print "Where:"
    print "   insertyouremailaddresshere is a recipient's full email address (i.e. " + pd.GMAIL_SENDER_USERNAME + ")"
    print "   Nameofperson is a recipient's name. Can include spaces."
    print "   Subscriptionstatus must be 'Yes' in order to receive email. Case sensative."
    print "     Any other value will disqualify from receiving email."
    print "****************************************************************************"
    print "To view values in the " + pd.EMAIL_ADDRESS_CONTACTS_TABLE + " table type:"
    print "\".mode column\""
    print "\".headers on\""
    print "\"SELECT * FROM " + pd.EMAIL_ADDRESS_CONTACTS_TABLE + ";\""
    print "****************************************************************************"
    print "After you have done so rerun the program."
    print "****************************************************************************"
    quit()

buildcont = BuildContent()

#Save word of day into frequently accessed variable so excessive URL fetches are not done
freqv.set_wod(buildcont.get_scrape(ur.WORD_OF_DAY_URL, ur.WORD_OF_DAY_SELECTOR))

img = Image()
img.set_wod(freqv.get_wod())

if debug_mode == "true":
    img.download_image(ur.DEBUG_URL1, 1)
    img.download_image(ur.DEBUG_URL2, 2)
    img.download_image(ur.DEBUG_URL3, 3)
else:
    img.download_iterator()

buildform = BuildFormatting()

buildform.create_email_subject(buildcont.make_idiom(), buildcont.pick_person(), freqv.get_wod())

for ii in range(ef.NUMBER_OF_RESULTS):
    buildform.create_body_of_email(buildcont.get_quote(), ii)

print buildform.get_email_subject()
print buildform.get_body_of_email()

mail = Email(pd.GMAIL_SENDER_USERNAME, pd.GMAIL_SENDER_PASSWORD, buildform.get_email_subject(), buildform.get_body_of_email())

sqldb.print_table()

#mail.picture_mail_all(ef.NUMBER_OF_RESULTS, sqldb.retrieve_data())

sqldb.disconnect()
