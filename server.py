"""The Cluv"""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session)

from flask_debugtoolbar import DebugToolbarExtension

from model import User, Article, Image, ArticleType, connect_to_db, db

import boto3, botocore
import os
import uuid

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
def closet():
    article_type = ArticleType.query.all()
    # for t in article_type:
    #     print(t.name)
    #query articles by session user id
    filter_type = request.args.get("filter")
    # print(filter_type)
    current_user = session.get("current_user")
    user_name = User.query.filter_by(user_id=current_user).one()
    # print (user_name.fname)
    page_name = "/my_closet"
    # if user_name.fname.endswith("s"):
    #     page_name = "{}' Closet".format(user_name.fname)
    # else:
    #     page_name = "{}'s Closet".format(user_name.fname)

    closet_info = Article.query.filter_by(owner_id=current_user)

    if filter_type:
        closet_info = closet_info.join(ArticleType).filter(ArticleType.name==filter_type)
    closet_info = closet_info.all()

    return render_template("closet.html", closet_info=closet_info, page_name=page_name, article_type=article_type)

@app.route('/closets')
def all_closet():
#     #query articles by session user id
    current_user = session.get("current_user")
    article_type = ArticleType.query.all()
    page_name = "/closets"

    if current_user:
        closet_info = Article.query.filter_by(is_private=False).all()

    # for item in closet_info: 
    #     print(item.images)


    return render_template("closet.html", closet_info=closet_info, page_name=page_name, article_type=article_type)

@app.route('/article_details/<article_id>')
def artticle_details(article_id):
    current_article = Article.query.get(article_id)
    # print(current_article)
    current_user = session.get("current_user")

    return render_template("article_details.html", current_article=current_article, current_user=current_user)
    
@app.route('/article_details/<article_id>', methods=['POST'])
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
def profile():
  """User profile page."""
  current_user = session.get("current_user")

  user_info = User.query.filter_by(user_id=current_user).first()

  return render_template("profile.html", user_info=user_info)

@app.route('/logout')
def logout():
    session.clear()
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

    current_user = session.get("current_user")
    if current_user:
        return redirect('/my_closet')

    # #flash message here
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
    # print(user_img)
    #check of user entered a image url, if not set default

    if user_img != None:
        user_pic = upload_to_s3(user_img)
    else: 
        print("default image used")
        user_pic = "https://t4.ftcdn.net/jpg/00/97/00/07/160_F_97000700_0UiUzwGrOuZuNRBSuH3aZMB5w1j9K0iA.jpg"

    if password_2 != password:
        return redirect('/register')
    #check if email in Users
    if User.query.filter_by(email=new_email).first():
        return redirect('/login')
    if User.query.filter_by(username=new_username).first():
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
        #add a flash message
    return redirect('/login')

@app.route("/article_add", methods = ['GET'])
def article_add():
    article_type = ArticleType.query.all()
    return render_template("article_add.html", article_type=article_type)

@app.route("/article_add_confirm", methods = ['POST'])
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
