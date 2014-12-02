#!/usr/bin/python2.7

#This program scrapes pseudo-randomly generated quotes, creates idioms and claims they were
# spoken by a pseudo-randomly selected famous person, and scrapes a word of the day and uses
# it to find related pictures on Google and sends it in an HTML-formatted email to a database
# of subscribed email addresses.

#Email addresses are stored in a SQLite database. Email addresses can be registered in the
# database, yet inactive for receiving email.

Note: Do not need Google Custom Search credentials for debug mode.

--------------------------------------------------------------------

Dependencies that are not installed by default

OSX (tested on 10.9 & 10.10):

**Need working pip & brew installs prior to installing dependencies**

apiclient
    pip install --upgrade google-api-python-client
lxml
    brew install libxml2
    pip install lxml
requests
    pip install requests
sqlite3
	(should be installed with python)
flask
    pip install flask
wtforms
    pip install wtforms
Flask-WTF
	pip install Flask-WTF


Linux (tested on Amazon Linux AMI [Red Hat], unconfirmed: maybe same for CentOS and related distros as well):

pip
	yum install python-pip
apiclient
    pip install --upgrade google-api-python-client
lxml
	yum install python-devel
	yum install libxslt-devel
	pip install lxml
requests
	(already installed)
sqlite3
	(should be installed with python)
flask (as well as: Werkzeug Jinja2 itsdangerous markupsafe)
    pip install flask
wtforms
    pip install wtforms
Flask-WTF
    pip install Flask-WTF

--------------------------------------------------------------------

Steps to run this program:

1)
Install missing dependencies on system.

2)
Enable Google Custom Search on your Google Account (Can skip to step 4 if planning to run ONLY in debug mode)..

"Go to your Custom Search Engine, then select your custom search engine, then in Basics tab,
 set Image search option to ON, and for Sites to search section, select Search the entire web
 but emphasize included site option."
 
Follow the solution
http://stackoverflow.com/questions/22866579/download-images-with-google-custom-search-api

3)
In ./data/secure/private_data.py

Enter your Google Custom Search API Key and Custom Search Engine ID (cx)
Enter your Google account and password for sending emails.

4)
Execute by running "python HappyEmail.py". No are available flags.

Program can be run in debug mode by setting debug_mode to "true"

Debug mode will bypass Google Custom Searching, due to low search limitation and high setup time.

#Todo..

Create python egg

Backend:
Fix UnicodeEncodeError for scraping quotes
Figure out why Google Search API fails every other search and fix apiclient.errors.HttpError handling
Cleanup imported libraries
Encapsulate "files" dictionary
Abstract BuildContent, Image, and BuildFormatting classes
Create classes inheriting from Database for email_address database as well as individualized history databases for each email address
Delete images once email has been sent

Frontend:
Admin portal to view subscribers