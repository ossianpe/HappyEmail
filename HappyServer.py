from flask import Flask
from flask import request, url_for, redirect
from flask import render_template
from werkzeug import secure_filename
from wtforms import Form, BooleanField, TextField, IntegerField, FormField, FileField, SelectField, PasswordField, validators
from flask_wtf.file import FileAllowed

from lib.database_lib import Database

import lib.secure.private_data as pd

app = Flask(__name__)
app.debug=True

MIN_NAME_CHARS=4
MAX_NAME_CHARS=25

MIN_EMAIL_CHARS=6
MAX_EMAIL_CHARS=35

sqldb = Database()

class RegistrationForm(Form):
    name = TextField('* Name', [validators.Length(min=MIN_NAME_CHARS,
                                                max=MAX_NAME_CHARS,
                                                message="Name must be between " + str(MIN_NAME_CHARS) + " and " +
                                                    str(MAX_NAME_CHARS) + " characters long.")])
    email = TextField('* Email Address', [validators.Length(min=MIN_EMAIL_CHARS,
                                                          max=MAX_EMAIL_CHARS,
                                                          message="Email must be between " + str(MIN_EMAIL_CHARS) +
                                                                " and " + str(MAX_EMAIL_CHARS) + " characters long."),
                                        validators.Email("Not a valid email address")])
    subscribe = SelectField('* Subscription Status', choices=[('Yes', 'Subscribe'), ('No', 'Unsubscribe')])
    phone = TextField('Phone Number')
    #picture = FileField(u'Personal Picture', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    accept_tos = BooleanField('* I accept the TOS agreement.', [validators.DataRequired("Check the box, moron.")])

class Administrative(Form):
    username = TextField('Username:')
    password = PasswordField('Password:')

@app.route('/')
def root_index():
    return 'Happy happy happy.. email.'

@app.route('/landing')
def landing():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        #filename = secure_filename(form.photo.data.filename)
        #form.photo.data.save('uploads/' + filename)
        sqldb.connect(pd.EMAIL_ADDRESS_DB)
        sqldb.set_selected_table(pd.EMAIL_ADDRESS_CONTACTS_TABLE)
        #sqldb.add_address_to_table(str(form.email.data), str(form.name.data), str(form.subscribe.data))
        sqldb.disconnect()
        #flash('Thanks for registering')
        #return redirect(url_for('registered'))
    return render_template('register.html', form=form)

@app.route('/registered')
def registered():
    return 'Thank you for registering!'

@app.route('/admin', methods=['GET', 'POST'])
def administrative():
    form = Administrative(request.form)
    if request.method == 'POST' and form.validate():
        #filename = secure_filename(form.photo.data.filename)
        #form.photo.data.save('uploads/' + filename)
        sqldb.connect(pd.EMAIL_ADDRESS_DB)
        sqldb.set_selected_table(pd.EMAIL_ADDRESS_CONTACTS_TABLE)
        #sqldb.add_address_to_table(str(form.email.data), str(form.name.data), str(form.subscribe.data))
        sqldb.disconnect()
        #flash('Thanks for registering')
        #return redirect(url_for('registered'))
    return render_template('admin.html', form=form)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)