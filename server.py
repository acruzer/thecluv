"""The Cluv"""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session)

from flask_debugtoolbar import DebugToolbarExtension

from model import User, ArticleType, connect_to_db, db

import boto3, botocore
import os
import uuid

S3_KEY = "TEMP"
S3_SECRET = "TEMP"
S3_BUCKET = "thecluv"

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

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
def closet():
    #query articles by session user id
    return render_template("closet.html")

@app.route('/profile/<user_id>')
def profile():
  """User profile page."""
  return render_template("profile.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    new_username=request.form.get("username")
    password=request.form.get("password")
    current_user = User.query.filter_by(username=new_username).first()

    if current_user:
        if current_user.password == password:
            session["current_user"] = current_user.user_id
            return redirect('/my_closet')
    #flash message here
    return render_template("login.html")

@app.route("/register", methods = ['POST', 'GET'])
def register():
    return render_template("register.html")

@app.route("/register_confirm", methods = ['POST'])
def register_confirm():

    fname=request.form.get("fname")
    lname=request.form.get("lname")
    new_username=request.form.get("username")
    user_img=request.form.get("user_img")
    new_email=request.form.get("email")
    password=request.form.get("password")
    password_2=request.form.get("password_2")
    zipcode=request.form.get("zipcode")
    print(user_img)
    #check of user entered a image url, if not set default
    if user_img == "":
        user_img = "https://t4.ftcdn.net/jpg/00/97/00/07/160_F_97000700_0UiUzwGrOuZuNRBSuH3aZMB5w1j9K0iA.jpg"

    if password_2 != password:
        return redirect('/register')
    #check if email in Users
    if User.query.filter_by(email=new_email).first():
        return redirect('/register')
    if User.query.filter_by(username=new_username).first():
        return redirect('/register')
    else:   
        pwd = request.form.get('password')
        user = User(
                fname=fname,
                lname=lname,
                username=new_username,
                user_img=user_img,
                email=new_email,
                password=pwd,
                zipcode=zipcode
                )
        db.session.add(user)
        db.session.commit()

        # print("user id is: ",user_id)
        print(user)
    return render_template('index.html',
                            username=new_username)

@app.route("/article_add", methods = ['GET'])
def article_add():
    article_type = ArticleType.query.all()
    return render_template("article_add.html", article_type=article_type)

@app.route("/article_add_confirm", methods = ['POST'])
def article_add_confirm():
    user_id = session["current_user"]
    type_id=request.form.get("type_id")
    image_file=request.files["image"]
    #check if images are there
    # image_2=request.form.get("image_2")
    # image_3=request.form.get("image_3")
    size=request.form.get("size")

    # article = Article (
    #             owner_id=user_id,
    #             type_id=type_id,
    #             )
    # db.session.add(article)
    # db.session.flush()
    # article.article_id


    # image = Image (
    #             article_id=article.article_id
    #             )
    upload_to_s3(image_file)

def upload_to_s3(image):
    s3 = boto3.client("s3",
        aws_access_key_id=S3_KEY,
        aws_secret_access_key=S3_SECRET)

    unused_filename, file_extension = os.path.splitext(image.filename)
        
    filename = str(uuid.uuid1()) + file_extension

    reponce = s3.upload_fileobj(image,
            S3_BUCKET,
            filename,
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": image.content_type
                }
            )
    print ("https://s3-us-west-1.amazonaws.com/thecluv/{}".format(filename))

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
