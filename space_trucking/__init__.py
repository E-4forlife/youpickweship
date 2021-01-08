from esipy import EsiApp, EsiClient, EsiSecurity
from flask import Flask, request, Response, render_template, redirect, session, flash
from random import randint, randrange
from time import strftime
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, RadioField

import hashlib
import random
import os
import re
import json
import hmac

# This was built following this resource: https://kyria.github.io/EsiPy/examples/sso_login_esipy/
############################## CONSTANTS #########################
# (Saved in user eve account)
DEBUG = True
REDIRECT_URI='http://localhost/oauth-callback'
DEV_API_KEY = (os.environ['DEV_API_KEY'])
DEV_API_SECRET_KEY = (os.environ['DEV_API_SECRET_KEY'])
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = (os.environ['APP_SECRET_KEY_2'])
######################################################################

security = EsiSecurity(
    redirect_uri = REDIRECT_URI,
    client_id    = DEV_API_KEY,
    secret_key   = DEV_API_SECRET_KEY,
    headers = {'User-Agent': 'doyouevenliftumadbro@gmail.com'},)

esiapp = EsiApp().get_latest_swagger
client = EsiClient(
    retry_requests = False,
    headers = {'User-Agent': 'doyouevenliftumadbro@gmail.com'},
    security = security
)

''' This is the first step, its a log in process for eve SSO, it returns a url for a user to log
    in from. Once a user logs in it will return a response URL that looks like this:
    http://localhost/oauth-callback?code=xKUaKODBeEyo2giHHrc9NQ&state=SomeRandomGeneratedState
    This will return a 404 (until the app is done and can properly reroute to the page to fill
    an order), you can use that code from within to get security tokens from it, using the code below
'''
def login():
    token = generate_token()
    return(security.get_auth_uri(state=token, scopes=[]))

def generate_token():
    """Generates a non-guessable OAuth token used as a state for client connection"""
    chars = ('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    rand = random.SystemRandom()
    random_string = ''.join(rand.choice(chars) for _ in range(40))
    return hmac.new(
       app.config['SECRET_KEY'].encode('utf-8'),
        random_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

class ReusableForm(Form):
#    name           = session['name']
    system_options = RadioField('system_options',choices=[('h65-he','h65-he'),('p-zmzv','p-zmzv')])
    contract       = RadioField('contract',choices=[('yes','yes'),('no','no')])
    tax            = RadioField('tax',choices=[('yes','yes'),('no','no')])
    multibuy       = TextAreaField('multibuy', [validators.Length(min=1, max=10000)])

def get_time():
    time = strftime("%Y-%m-%d %H:%M")
    return time

def write_to_disk(name, system_options, contract, tax, multibuy):
    data = open('file.log', 'a')
    timestamp = get_time()
    data.write('Form submitted at: {}\n'
               'Character Name: {}\n'
               'System to ship to: {}\n'
               'Did user agree to completing contract?: {}\n'
               'Did user agree to pay for the tax and fee?: {}\n'
               'Multibuy:\n{}\n\n'.format(timestamp, name, system_options, contract, tax, multibuy))
    data.close()


# Redirects / forces login
@app.route("/")
def index():
    return redirect('/login')


@app.route('/login')
def hello():
    sso_url = login()
    eve = {'sso_login': sso_url}
    return render_template('login.html', title='Home', eve=eve)


#This is where the user comes after they log in through SSO
@app.route('/oauth-callback')
def respond():
    # Gets the code back from from after logging in, this is used to get tokens 
    code = request.args.get('code')
    tokens = security.auth(code)
    api_info = security.verify()
    session['name'] = api_info['name']
    return redirect('/shipping')


# Shipping Form
@app.route('/shipping', methods=['GET', 'POST'])
def hello_world():
    form = ReusableForm(request.form)
    if request.method == 'POST' and form.validate() and form.contract.data == "yes" and form.tax.data == "yes":
        #print("errors:",form.errors)
        name     = session['name']
        system   = form.system_options.data
        contract = form.contract.data
        tax      = form.tax.data
        multibuy = request.form['multibuy']

        write_to_disk(name, system, contract, tax, multibuy)
        flash('{}, Your order has been submitted.'.format(name))
    
    elif request.method == 'POST' and len(request.form['name']) > 40:
        print(form.system_options.data)
        flash('Error: User name length, user name must be between 1 and 40 characters')

    elif request.method == 'POST' and len(request.form['multibuy']) > 20000:
        print(form.system_options.data)
        flash('Error: Multibuy length, Multibuy must be between 1 and 10,000 characters')

    elif form.contract.data == "no":
        flash('Error: You must agree to completing the contract to submit this order.')

    elif form.tax.data == "no":
        flash('Error: You must agree to paying tax and fees to submit this order.')

    else:
        print(form.system_options.data)
        flash('Error: All fields are required')

    return render_template('shipping.html', form=form, player_name=session['name'])

# How to run: flask run --host=0.0.0.0 --port=80
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

