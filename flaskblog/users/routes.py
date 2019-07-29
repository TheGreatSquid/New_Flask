
from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db
from flaskblog.models import User, Post
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flaskblog.users.utils import hash_pw, save_picture, send_reset_email


users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	
	form = RegistrationForm()	
	if form.validate_on_submit():
		# since no salt is passed, one is generated randomly
		# `fullhash` is of the form `salt$hash`
		full_hash = '$'.join(hash_pw(form.password.data))
		user = User(username=form.username.data, email=form.email.data, password=full_hash)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created! You are now able to log in.', 'success')
		return redirect(url_for('users.login'))
		
	return render_template('register.html', title='Register', form=form)

	
@users.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		# separate the parts of the stored password
		salt, hash = user.password.split('$')
		# use stored salt to hash login password
		_, login_hash = hash_pw(form.password.data, salt)
		# test if the two hashes are equivalent (connecting the salts back is a waste of time)
		if user and hash == login_hash:
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('main.home'))
		else:
			flash('Login Unsuccessful. Please check email and password', 'danger')
	
	return render_template('login.html', title='Login', form=form)

	
@users.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('main.home'))
	
	
@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			if current_user.image_file != 'default.jpg':
				old_pic_name = current_user.image_file
				old_path = os.path.join(app.root_path, 'static/profile_pics', old_pic_name)
				os.remove(old_path)
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('users.account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('account.html', title='Account', image_file=image_file, form=form)


@users.route('/user/<string:username>')
def user_posts(username):
	page = request.args.get('page', 1, type=int)
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.filter_by(author=user)\
		.order_by(Post.date_posted.desc())\
		.paginate(page=page, per_page=5)
	return render_template('user_posts.html', posts=posts, user=user)
	
	
@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email with instructions for resetting your password has been sent.', 'success')
		return redirect(url_for('users.login'))
	return render_template('reset_request.html', title='Reset Password', form=form)
	
	
@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('That token is invalid or has expired.', 'warning')
		return redirect(url_for('users.reset_request'))
	# token was valid
	form = ResetPasswordForm()
	if form.validate_on_submit():
		# since no salt is passed, one is generated randomly
		# `fullhash` is of the form `salt$hash`
		full_hash = '$'.join(hash_pw(form.password.data))
		user.password = full_hash
		db.session.commit()
		flash('Your password has been updated! You are now able to log in.', 'success')
		return redirect(url_for('users.login'))
	return render_template('reset_token.html', title='Reset Password', form=form)
