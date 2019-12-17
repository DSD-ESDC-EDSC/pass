from base64 import b64decode
from flask import Flask, request, render_template, jsonify, redirect, url_for, abort, make_response
import flask_login
from functools import wraps
from io import BytesIO
from waitress import serve
from werkzeug.security import generate_password_hash, check_password_hash
import json
import sys
from modules import db
from dotenv import load_dotenv
import os
import gzip
try:
    from StringIO import StringIO ## for Python 2
except ImportError:
    from io import StringIO ## for Python 3
load_dotenv()

APP_SECRET_KEY = os.environ.get('APP_SECRET_KEY')
APP_HOST = os.environ.get('APP_HOST')
APP_PORT = os.environ.get('APP_PORT')
APP_THREADS = int(os.environ.get('APP_THREADS', 4))

USER_NAME = os.environ.get('USER_NAME')
USER_PASSWORD = os.environ.get('USER_PASSWORD')
ADMIN_NAME = os.environ.get('ADMIN_NAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

HTTP_OK = 200
HTTP_BAD_REQ = 400
HTTP_FORBIDDEN = 403

# create flask app
app = Flask(__name__)
app.debug = True
app.secret_key = APP_SECRET_KEY

# login = flask_login.LoginManager(app)
# login.init_app(app)
# login.login_view = 'login'

# class User(flask_login.UserMixin):
# 	def is_admin(self):
# 		return self._admin
#
# 	def set_admin(self):
# 		self._admin = True
#
# # route for confirming username
# @login.user_loader
# def user_loader(username):
# 	if username == USER_NAME:
# 		user = User()
# 		user.id = username
# 		return user
#
# 	elif username == ADMIN_NAME:
# 		user = User()
# 		user.id = username
# 		user.set_admin()
# 		return user
#
# 	return
#
# # Require admin login for the decorated function.
# # To use, replace `@flask_login.login_required` with `@admin_required`.
# def admin_required(func):
# 	@flask_login.login_required
# 	@wraps(func)
# 	def wrapper(*args, **kwargs):
# 		if flask_login.current_user.is_admin():
# 			return func(*args, **kwargs)
# 		else:
# 			abort(HTTP_FORBIDDEN)
#
# 	return wrapper
#
# # Extract and b64-decode a number of files from the body of the request.
# # The arguments to this function are the JSON keys of the files.
# # To use, decorate a route with `@extract_body_file("file1", "file2"...)`,
# # and include arguments for each extracted file. See `createGeoTable` for an example.
# def extract_body_file(*files):
# 	def decorator(func):
# 		@wraps(func)
# 		def wrapper(*args, **kwargs):
# 			decoded_files = []
# 			req = request.get_json()
#
# 			for file in files:
# 				file_b64 = req.get(file)
# 				if not file_b64:
# 					return f'{file} is a required body parameter (base64-encoded file)', HTTP_BAD_REQ
#
# 				decoded = b64decode(file_b64)
# 				decoded_files.append(BytesIO(decoded))
#
# 			return func(*decoded_files, *args, **kwargs)
# 		return wrapper
# 	return decorator

# route for login
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#
# 	next_page = request.args.get('next')
#
# 	# if user is already authenticated, direct them to hub
# 	if flask_login.current_user.is_authenticated:
# 		if next_page:
# 			return redirect(next_page)
# 		else:
# 			return redirect(url_for('index'))
#
# 	error = None
#
# 	if request.method == 'POST':
# 		username = request.form['username']
# 		password = request.form['password']
#
# 		# regular user
# 		if username == USER_NAME and check_password_hash(USER_PASSWORD, password):
# 			user = User()
# 			user.id = username
# 			flask_login.login_user(user, remember=True)
# 			if not next_page:
# 				next_page = url_for('index')
# 			return redirect(next_page)
#
# 		# admin user
# 		elif username == ADMIN_NAME and check_password_hash(ADMIN_PASSWORD, password):
# 			user = User()
# 			user.id = username
# 			user.set_admin()
# 			flask_login.login_user(user, remember=False)
# 			if not next_page:
# 				next_page = url_for('index')
# 			return redirect(next_page)
#
# 		else:
# 			error = 'Invalid Credentials. Please try again.'
#
# 	return render_template('login.html', error=error)

# route for NILFA hub / landing page
@app.route('/')
@flask_login.login_required
def index():
	return render_template('index.html')

# route for retreiving data for the calculator tool
@app.route('/runModel',methods=['POST'])
def getCalculatorData():
	req = request.get_json()
	param = req['param']
	data = json.dumps(db.queryCalculator(param))
	return data

# route for bad HTTP requests
@app.errorhandler(400)
def error(e):
	return render_template('error.html')


if __name__ == '__main__':
	serve(app, host=APP_HOST,port=APP_PORT,threads=APP_THREADS)
