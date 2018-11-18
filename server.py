"""The Cluv"""

from jinja2 import StrictUndefined

from functools import wraps
from flask import (Flask, render_template, redirect, request, flash,
				   session)

from flask_debugtoolbar import DebugToolbarExtension

from model import User, Article, Image, ArticleType, connect_to_db, db

import boto3, botocore
import os
import uuid

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		current_user = session.get("current_user")
		if current_user is None:
			return redirect('/login')
		return f(*args, **kwargs)
	return decorated_function

S3_KEY = os.environ["S3_KEY"]
S3_SECRET = os.environ["S3_SECRET"]
S3_BUCKET = "thecluv"

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = os.environ["APP_SECRET"]

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
	"""Homepage."""
	#check if user is on the session
	if session.get("current_user"):
		return redirect('/my_closet')
	else:
		return render_template("login.html")

@app.route('/my_closet')
@login_required
def closet():
	current_user = session.get("current_user")
	#query articles by session user id
	filter_type = request.args.get("filter")
	article_type = ArticleType.query.all()

	user_name = User.query.filter_by(user_id=current_user).one()

	page_name = "/my_closet"

	closet_info = Article.query.filter_by(owner_id=current_user)

	if filter_type:
		closet_info = closet_info.join(ArticleType).filter(ArticleType.name==filter_type)
	
	closet_info = closet_info.all()

	return render_template("closet.html", closet_info=closet_info, page_name=page_name, article_type=article_type)

@app.route('/closets')
@login_required
def all_closet():

	#query articles by session user id
	current_user = session.get("current_user")
	print(current_user)
	filter_type = request.args.get("filter")
	article_type = ArticleType.query.all()
	page_name = "/closets"

	if current_user:
		closet_info = Article.query.filter(Article.owner_id!=current_user, Article.is_private==False)

	if filter_type:
		closet_info = closet_info.join(ArticleType).filter(ArticleType.name==filter_type)
	closet_info = closet_info.all()

	return render_template("closet.html", closet_info=closet_info, page_name=page_name, article_type=article_type)

@app.route('/article_details/<article_id>')
@login_required
def article_details(article_id):
	current_article = Article.query.get(article_id)
	article_owner = User.query.filter_by(user_id=current_article.owner_id).one()

	current_user = session.get("current_user")
	current_user_info = User.query.filter_by(user_id=current_user).first()
	return render_template("article_details.html", 
		current_article=current_article, 
		current_user=current_user,
		current_user_info=current_user_info, 
		article_owner=article_owner)
	
@app.route('/article_details/<article_id>', methods=['POST'])
@login_required
def delete_article(article_id):
	
	current_user = session.get("current_user")
	found_article_id = int(request.form.get("article_to_delete"))

	to_delete = Article.query.filter(Article.article_id == found_article_id).one()
	print(to_delete.images)
	
	if current_user:
		delete_img_aws(to_delete)
		db.session.delete(to_delete)
		db.session.commit()
	
	return redirect('/my_closet')

@app.route('/profile')
@login_required
def profile():
	#User profile page.
	current_user = session.get("current_user")
	
	user_info = User.query.filter_by(user_id=current_user).first()
	return render_template("profile.html", user_info=user_info)


@app.route('/profile_edit', methods=['POST', 'GET'])
@login_required
def profile_edit():
	# Edit User info
	current_user = session.get("current_user")
	user_info = User.query.filter_by(user_id=current_user).first()
	# print(user_info)

	if request.method == 'GET':
		return render_template("profile_edit.html", user_info=user_info)

	if request.method == 'POST':
		new_email=request.form.get("email")
		user_info.fname = request.form.get("fname")
		user_info.lname = request.form.get("lname")
		user_info.zipcode = request.form.get("zipcode")
		if new_email != user_info.email:
			email_check = User.query.filter_by(email=new_email).first()
			if email_check:
				flash('This email already exist.')
				return redirect('/profile_edit')
			else: 
				user_info.email = new_email
				db.session.commit()
		
		return render_template("profile.html", user_info=user_info)


@app.route('/logout')
def logout():
	session.clear()
	# flash('You are now logged out.')
	return redirect('/login')

@app.route("/login", methods = ['POST', 'GET'])
def login():
	#maybe check if method is "POST"
	if request.method == 'POST':
		new_username=request.form.get("username")
		password=request.form.get("password")
		current_user = User.query.filter_by(username=new_username).first()

		if current_user and current_user.password == password:
			session["current_user"] = current_user.user_id
		else:
			flash('Either you username or password are incorrect. Please try again.')
	
	current_user = session.get("current_user")
	if current_user:
		return redirect('/my_closet')
	
	
	return render_template("login.html")


@app.route("/register", methods = ['POST', 'GET'])
def register():
	return render_template("register.html")

@app.route("/register_confirm", methods = ['POST'])
def register_confirm():
	fname=request.form.get("fname")
	lname=request.form.get("lname")
	new_username=request.form.get("username")
	user_img=request.files.get("user_img")
	new_email=request.form.get("email")
	password=request.form.get("password")
	password_2=request.form.get("password_2")
	zipcode=request.form.get("zipcode")

	#check of user entered a image url, if not set default

	if user_img != None:
		user_pic = upload_to_s3(user_img)
	else: 
		print("default image used")
		user_pic = "https://t4.ftcdn.net/jpg/00/97/00/07/160_F_97000700_0UiUzwGrOuZuNRBSuH3aZMB5w1j9K0iA.jpg"

	if password_2 != password:
		flash('Your passwords do not match.')
		return redirect('/register')
	#check if email in Users
	if User.query.filter_by(email=new_email).first():
		flash('The email you entered already exist.')
		return redirect('/login')
	if User.query.filter_by(username=new_username).first():
		flash('The username you entered already exist.')
		return redirect('/register')
	else:   
		pwd = request.form.get('password')
		user = User(
				fname=fname,
				lname=lname,
				username=new_username,
				user_img=user_pic,
				email=new_email,
				password=pwd,
				zipcode=zipcode
				)
		db.session.add(user)
		db.session.commit()
	session["current_user"] = user.user_id
	flash('Welcome!!!')
	return redirect('/login')

@app.route("/article_add", methods = ['GET'])
@login_required
def article_add():
	article_type = ArticleType.query.all()
	
	return render_template("article_add.html", article_type=article_type)

@app.route("/article_edit/<article_id>", methods = ['GET', 'POST'])
@login_required
def article_edit(article_id):
	current_user = session.get("current_user")
	current_article = Article.query.filter_by(article_id=article_id).first()
	article_type = ArticleType.query.all()
	
	if request.method == 'GET':
		return render_template("article_edit.html", current_article=current_article, article_type=article_type)

	if request.method == 'POST':
		is_private = request.form.get("is_private")
		is_loanable = request.form.get("is_loanable")
		is_giveaway = request.form.get("is_giveaway")
		current_article.size = request.form.get("size")
		current_article.color = request.form.get("color")
		current_article.material = request.form.get("material")
		current_article.notes = request.form.get("notes")

		bool_convert = {"True": True, "False": False}
		
		current_article.is_private = bool_convert[is_private]
		current_article.is_loanable = bool_convert[is_loanable]
		current_article.is_giveaway = bool_convert[is_giveaway]

		db.session.commit()
		flash('This article has been updated.')
		return render_template("article_details.html", current_article=current_article, current_user=current_user)

@app.route("/article_add_confirm", methods = ['POST'])
@login_required
def article_add_confirm():
	# print(request.files)
	user_id = session["current_user"]
	type_id=request.form.get("type_id")
	image_file_1=request.files.get("image")
	image_file_2=request.files.get("image_2")
	image_file_3=request.files.get("image_3")
	image_file_4=request.files.get("image_4")
	size=request.form.get("size")
	color=request.form.get("color")
	material=request.form.get("material")
	notes=request.form.get("notes")
	is_private=request.form.get("is_private")
	is_loanable=request.form.get("is_loanable")
	is_giveaway=request.form.get("is_giveaway")

	bool_convert = {"True": True, "False": False}
	article = Article(
				owner_id=user_id,
				type_id=type_id,
				size=size,
				color=color,
				material=material,
				notes=notes,
				is_private=bool_convert[is_private],
				is_loanable=bool_convert[is_loanable],
				is_giveaway=bool_convert[is_giveaway]
				)

	#check if images are there
	img_1 = upload_to_s3(image_file_1)
	image = Image (img_url=img_1)
	article.images.append(image)
	
	#check if images exist and if yes add them to the database
	img_in_form = [image_file_2, image_file_3, image_file_4]
	for img_file in img_in_form:
		if img_file != None:
			img = upload_to_s3(img_file)
			image = Image (img_url=img)
			article.images.append(image)

	
	db.session.add(article)
	db.session.commit()
	
	flash('New article added.')
	return redirect('/my_closet')

def upload_to_s3(image):
	s3 = boto3.client("s3",
		aws_access_key_id=S3_KEY,
		aws_secret_access_key=S3_SECRET)

	unused_filename, file_extension = os.path.splitext(image.filename)
		
	filename = str(uuid.uuid4()) + file_extension

	reponce = s3.upload_fileobj(image,
			S3_BUCKET,
			filename,
			ExtraArgs={
				"ACL": "public-read",
				"ContentType": image.content_type
				}
			)
	# print ("https://s3-us-west-1.amazonaws.com/thecluv/{}".format(filename))
	return "https://s3-us-west-1.amazonaws.com/thecluv/{}".format(filename)

def delete_img_aws(article_obj):

	session = boto3.Session(
	aws_access_key_id=S3_KEY,
	aws_secret_access_key=S3_SECRET,
	region_name="us-west-1")

	s3 = session.resource("s3")
	for i in article_obj.images:
		img_to_delete = i.img_url[43:]
		print(img_to_delete)
		obj = s3.Object(S3_BUCKET, img_to_delete)
		obj.delete()

		return "Images Deleted"


if __name__ == "__main__":
	# We have to set debug=True here, since it has to be True at the
	# point that we invoke the DebugToolbarExtension
	app.debug = True
	# DEBUG_TB_INTERCEPT_REDIRECTS = False
	# make sure templates, etc. are not cached in debug mode
	app.jinja_env.auto_reload = app.debug

	connect_to_db(app)

	# Use the DebugToolbar
	# DebugToolbarExtension(app)

	app.run(port=5000, host='0.0.0.0')
