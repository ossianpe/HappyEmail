from flask import Flask
from flask import request, url_for, redirect
from flask import render_template
from wtforms import Form, BooleanField, TextField, validators

from data.database import Database

import data.secure.private_data as pd

app = Flask(__name__)

MIN_NAME_CHARS=4
MAX_NAME_CHARS=25

MIN_EMAIL_CHARS=6
MAX_EMAIL_CHARS=35

sqldb = Database()

class User():
    def __init__(self, username, email):
        self.username = username
        self.email = email

class RegistrationForm(Form):
    name = TextField('Name', [validators.Length(min=MIN_NAME_CHARS,
                                                max=MAX_NAME_CHARS,
                                                message="Name must be between " + str(MIN_NAME_CHARS) + " and " +
                                                    str(MAX_NAME_CHARS) + " characters long.")])
    email = TextField('Email Address', [validators.Length(min=MIN_EMAIL_CHARS,
                                                          max=MAX_EMAIL_CHARS,
                                                          message="Email must be between " + str(MIN_EMAIL_CHARS) +
                                                                " and " + str(MAX_EMAIL_CHARS) + " characters long."),
                                        validators.Email("Not a valid email address")])
    accept_tos = BooleanField('I accept the TOS agreement.', [validators.Required("Check the box, moron.")])

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        sqldb.connect(pd.EMAIL_ADDRESS_DB)
        sqldb.set_selected_table(pd.EMAIL_ADDRESS_CONTACTS_TABLE)
        sqldb.add_address_to_table(str(form.email.data), str(form.name.data), "Yes")
        sqldb.disconnect()
        #user = User(form.username.data, form.email.data)
        #db_session.add(user)
        #flash('Thanks for registering')
        return redirect(url_for('registered'))
    return render_template('register.html', form=form)

@app.route('/registered')
def registered():
    return 'Thank you for registering!'
    
@app.route('/t3')
def my_form():
    return render_template("Subscribe.html")

@app.route('/t3', methods=['POST'])
def my_form_post():

    text = request.form['name']
    processed_text = text.upper()
    return render_template("Subscribed.html")

if __name__ == '__main__':
    app.debug = True
    app.run()