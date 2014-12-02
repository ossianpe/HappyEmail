import requests
import lxml.html
import urllib2
import time
import apiclient
import random
import shutil
import math
import os
import sys

from apiclient.discovery import build
from pprint import pprint

from lib.database_lib import Database
from lib.email_lib import Email
from lib.various_utilities_lib import VariousUtilities
from lib.frequent_variables_lib import FrequentVariables

#Local file imports
import lib.vocab.word_banks as wbs
import lib.secure.private_data as pd
import lib.settings.email_settings as ef
import lib.settings.search_settings as ser
import lib.scrape.urls as ur

varutil = VariousUtilities()

class BuildContent:
    #is self correct here??
    def get_URL(self, url):
        varutil.check_connection(url)
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
            print "API Client: HTTPError.. trying again."
            time.sleep(2)
            self.get_image_URLs()
        except apiclient.errors.TypeError, err:
            print "API Client: TypeError.. trying again."
            time.sleep(2)
            self.get_image_URLs()
    
    #Downloads images from URL. Creates files in /images/ directory with name word of the day + current number of result
    #   and file container. Prints download percentage.
    #   https://gist.github.com/gourneau/1430932
    def download_image(self, relative_directory, download_url, image_store_location, ii):
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
            
            with open(varutil.open_subdirectory(relative_directory, image_store_location, file_name), 'wb') as fp:
                while True:
                    chunk = req.read(CHUNK)
                    downloaded += len(chunk)
                    print "Downloading image " + file_name + " " + str(math.floor( (downloaded / total_size) * 100 )) + "%"
                    if not chunk: break
                    fp.write(chunk)
            freqv.append_files(file_name)
        except urllib2.HTTPError, e:
            print "HTTP Error:",e.code , download_url, "Image Download Failed."
            return False
        except urllib2.URLError, e:
            print "URL Error:",e.reason , download_url, "Image Download Failed."
            return False

    def download_iterator(self, image_store_location):
        images = self.get_image_URLs()
        for ii in range(ef.NUMBER_OF_RESULTS):
            self.download_image(__file__, str(images[ii]), image_store_location, ii)

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

#Use this mode for testing.. can easily go over Google Custom Search API limit of 100 daily searches.
# Also, debug test images have a small file size allowing for quicker emailing for testing.
debug_mode = "false"

freqv = FrequentVariables()

database_check = ""
database_check = varutil.check_file(pd.EMAIL_ADDRESS_DB)

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
    img.download_image(__file__, ur.DEBUG_URL1, ser.IMAGE_DOWNLOAD_LOCATION, 1)
    img.download_image(__file__, ur.DEBUG_URL2, ser.IMAGE_DOWNLOAD_LOCATION, 2)
    img.download_image(__file__, ur.DEBUG_URL3, ser.IMAGE_DOWNLOAD_LOCATION, 3)
else:
    img.download_iterator(ser.IMAGE_DOWNLOAD_LOCATION)

buildform = BuildFormatting()

buildform.create_email_subject(buildcont.make_idiom(), buildcont.pick_person(), freqv.get_wod())

for ii in range(ef.NUMBER_OF_RESULTS):
    buildform.create_body_of_email(buildcont.get_quote(), ii)

print "***********************EMAIL SUBJECT***********************"
print buildform.get_email_subject()
print "***********************EMAIL BODY***********************"
print buildform.get_body_of_email()

mail = Email(pd.GMAIL_SENDER_USERNAME, pd.GMAIL_SENDER_PASSWORD, buildform.get_email_subject(), buildform.get_body_of_email())

sqldb.print_table()

mail.picture_mail_all(__file__, ef.NUMBER_OF_RESULTS, ser.IMAGE_DOWNLOAD_LOCATION, sqldb.retrieve_data(), freqv.get_files())

sqldb.disconnect()
