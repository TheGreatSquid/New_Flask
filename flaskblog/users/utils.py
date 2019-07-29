
import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail


def save_picture(form_picture):
	# randomize name of image to prevent collision
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_f_name = random_hex + f_ext
	picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_f_name)
	
	output_size = (125, 125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)
	
	return picture_f_name
	
	
def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request', 
		sender='paulmorenkov@gmail.com', 
		recipients=[user.email])
		
	msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request, please ignore this email and no changes will be made.
'''
	mail.send(msg)
