import os
from flask import Flask, render_template, request, url_for, redirect, flash, make_response
import requests
import datetime
from requests_oauthlib import OAuth1Session
from configparser import ConfigParser
import logging
import json

app = Flask(__name__)

app.debug = False

log_level = logging.DEBUG
logging.basicConfig(filename='authorizer.log', level=log_level)

def config(filename,section):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        logging.error('Error in reading config file : Section {0} not found in the {1} file'.format(section, filename))
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

webInformation = config('../../config.ini','webconfiguration')

request_token_url = str(webInformation['request_token_url'])
access_token_url = str(webInformation['access_token_url'])
authorize_url = str(webInformation['authorize_url'])
show_user_url = str(webInformation['show_user_url'])
truman_url = str(webInformation['app_route'])
account_settings_url = str(webInformation['account_settings_url'])

oauth_store = {}

@app.route('/')
def start():
    app_callback_url = url_for('callback', _external=True)
    cred = config('../../config.ini','twitterapp')

    try:
        request_token = OAuth1Session(client_key=cred['key'],client_secret=cred['key_secret'])
        content = request_token.post(request_token_url, data = {"oauth_callback":app_callback_url})
        logging.info('Twitter access successfull')
    except Exception as error:
        print('Twitter access failed with error : '+str(error))
        logging.error('Twitter access failed with error : '+str(error))

    #request_token = dict(urllib.parse.parse_qsl(content))
    #oauth_token = request_token[b'oauth_token'].decode('utf-8')
    #oauth_token_secret = request_token[b'oauth_token_secret'].decode('utf-8')

    data_tokens = content.text.split("&")

    oauth_token = data_tokens[0].split("=")[1]
    oauth_token_secret = data_tokens[1].split("=")[1] 
    oauth_store[oauth_token] = oauth_token_secret
    start_url = authorize_url+"?oauth_token="+oauth_token
    #res = make_response(render_template('index.html', authorize_url=authorize_url, oauth_token=oauth_token, request_token_url=request_token_url))
    res = make_response(render_template('YouGov.html', start_url=start_url, screenname="###", truman_url="###"))
    # Trying to add a browser cookie
    res.set_cookie('exp','infodiversity',max_age=1800)
    return res
    #return render_template('index.html', authorize_url=authorize_url, oauth_token=oauth_token, request_token_url=request_token_url)


@app.route('/cookie', methods=['GET']) # This is a function to set a flask cookie
def index():
    print("Creating cookie")
    res = make_response("<h1>cookie is set</h1>")  
    res.set_cookie('foo1','bar1')
    return res

@app.route('/get-cookie', methods=['GET'])
def get_cookie():
    #return request.cookies.get("Exp")
    if not request.cookies.get('Exp'):
        print("No cookie found!")
    else:
        res = make_response("Value of cookie Exp is {}".format(request.cookies.get('Exp')))
        return res

    return "Failed"    

@app.route('/callback')
def callback():
    print("IN CALLBACK")
    oauth_token = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')
    oauth_denied = request.args.get('denied')

    if oauth_denied:
        if oauth_denied in oauth_store:
            del oauth_store[oauth_denied]
        return render_template('error.html', error_message="the OAuth request was denied by this user")

    if not oauth_token or not oauth_verifier:
        return render_template('error.html', error_message="callback param(s) missing")

    # unless oauth_token is still stored locally, return error
    if oauth_token not in oauth_store:
        return render_template('error.html', error_message="oauth_token not found locally")

    oauth_token_secret = oauth_store[oauth_token]

    # if we got this far, we have both callback params and we have
    # found this token locally

    #consumer = oauth.Consumer(
    #    app.config['APP_CONSUMER_KEY'], app.config['APP_CONSUMER_SECRET'])
    #token = oauth.Token(oauth_token, oauth_token_secret)
    #token.set_verifier(oauth_verifier)
    #client = oauth.Client(consumer, token)

    #resp, content = client.request(access_token_url, "POST")
    
    cred = config('../../config.ini','twitterapp')
    oauth_access_tokens = OAuth1Session(client_key=cred['key'],client_secret=cred['key_secret'],resource_owner_key=oauth_token,resource_owner_secret=oauth_token_secret,verifier=oauth_verifier)
    content = oauth_access_tokens.post(access_token_url)  

    #access_token = dict(urllib.parse.parse_qsl(content))

    access_token = content.text.split("&")

    # These are the tokens you would store long term, someplace safe
    real_oauth_token = access_token[0].split("=")[1]
    real_oauth_token_secret = access_token[1].split("=")[1]
    user_id = access_token[2].split("=")[1]
    screen_name = access_token[3].split("=")[1]

    oauth_account_settings = OAuth1Session(client_key=cred['key'],client_secret=cred['key_secret'],resource_owner_key=real_oauth_token,resource_owner_secret=real_oauth_token_secret)
    response = oauth_account_settings.get(account_settings_url)
    account_settings_user = json.dumps(json.loads(response.text))
    
    resp_worker_id = requests.get('http://' + webInformation['localhost'] + ':5052/insert_user?twitter_id='+str(user_id)+'&account_settings='+account_settings_user)
    worker_id = resp_worker_id.json()["data"]

    attn = 0
    page = 0
    pre_attn_check = 1

    truman_url_agg = str(webInformation['app_route']) + '?access_token=' + str(real_oauth_token) + '&access_token_secret=' + str(real_oauth_token_secret) + '&worker_id=' + str(worker_id) + '&attn=' + str(attn) + '&page=' + str(page) + '&pre_attn_check=' + str(pre_attn_check) 
    #truman_url_agg = 'http://127.0.0.1:3000' + '?access_token=' + str(real_oauth_token) + '&access_token_secret=' + str(real_oauth_token_secret) + '&worker_id=' + str(worker_id) + '&attn=' + str(attn) + '&page=' + str(page) + '&pre_attn_check=' + str(pre_attn_check)

    del oauth_store[oauth_token]

    redirect(truman_url + '?access_token=' + real_oauth_token + '&access_token_secret=' + real_oauth_token_secret)

    #return render_template('placeholder.html', worker_id=worker_id, access_token=real_oauth_token, access_token_secret=real_oauth_token_secret)
    return render_template('YouGov.html', start_url="###", screenname=screen_name, truman_url=truman_url_agg)

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_message='uncaught exception'), 500

  
if __name__ == '__main__':
    app.run(host="0.0.0.0")
