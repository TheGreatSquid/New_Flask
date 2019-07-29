
try:
	# custom imitation of os.environ, used for Pythonista
	# TODO: remove when os.environ is well-configured, 
	# and computer-centered version is more stable.
	import environvars
	target = environvars.environ
except ModuleNotFoundError as e:
	import os
	target = os.environ


class Config:
	SECRET_KEY = target['BLOG_SECRET_KEY']
	SQLALCHEMY_DATABASE_URI = target['BLOG_DB_URI']
	MAIL_SERVER = 'smtp.googlemail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = target['EMAIL_USER']
	MAIL_PASSWORD = target['EMAIL_APP_PASS']
