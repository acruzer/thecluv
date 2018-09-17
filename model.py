"""Models and database functions for hackbright project."""

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of cluv website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    fname = db.Column(db.String(64), nullable=False)
    lname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False, unique=True)
    username = db.Column(db.String(15), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
<<<<<<< HEAD
    user_img = db.Column(db.String(), nullable=True)
=======
>>>>>>> 3cfcb4e0bc0ceb09c4a6a55df0f3abed321061af
    zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""
        return f"<User user_id={self.user_id} email={self.email}>"

class Article(db.Model):
    """Article of users"""
    

    __tablename__ = "articles"

    article_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('article_types.type_id'), nullable=False)
    size = db.Column(db.String(10), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    material = db.Column(db.String(64), nullable=False)
    notes = db.Column(db.String(150), nullable=True)
    is_private = db.Column(db.Boolean, default=True)
    is_loanable = db.Column(db.Boolean, default=False)
    is_giveaway = db.Column(db.Boolean, default=False)

    images = db.relationship("Image",
                             secondary="article_images",
                             backref="articles")
<<<<<<< HEAD
    type_value = db.relationship("ArticleType")
=======

>>>>>>> 3cfcb4e0bc0ceb09c4a6a55df0f3abed321061af

    def __repr__(self):
        """Provide helpful representation when printed."""
        return f"<Article article_id={self.article_id} type_id={self.type_id}>"


class Image(db.Model):
    """Images of articles"""
    

    __tablename__ = "images"

    img_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    img_url = db.Column(db.String, nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""
        return f"<Article article_id={self.article_id} type_id={self.type_id}>"

class ArticleImage(db.Model):
    """Images and articles connection"""
    

    __tablename__ = "article_images"

    article_img_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    img_id = db.Column(db.ForeignKey('images.img_id'), nullable=False)
    item_id = db.Column(db.ForeignKey('articles.article_id'), nullable=False)

<<<<<<< HEAD
    # image = db.relationship('Image', backref='images')
    # article = db.relationship('Article', backref='articles')
=======
    image = db.relationship('Image', backref='images')
    article = db.relationship('Article', backref='articles')
>>>>>>> 3cfcb4e0bc0ceb09c4a6a55df0f3abed321061af

    def __repr__(self):
        """Provide helpful representation when printed."""
        return f"<Article Image item_id={self.item_id} img_id={self.img_id}>"


class ArticleType(db.Model):
    """Article and type connection"""


    __tablename__ = "article_types"

    type_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""
        return f"<Article Type type_id={self.type_id} name={self.name}>"

class Loan(db.Model):
    """Articles loaned and return by users"""

    __tablename__ = "loans"

    loan_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    item_id = db.Column(db.ForeignKey('articles.article_id'), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    loan_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)

    borrower = db.relationship('User', backref='loans')
<<<<<<< HEAD
    article = db.relationship('Article', backref='loans')
=======
    article = db.relationship('Article', backref='articles')
>>>>>>> 3cfcb4e0bc0ceb09c4a6a55df0f3abed321061af

    def __repr__(self):
        """Provide helpful representation when printed."""
        return f"<Loan loan_id={self.loan_id} item_id={self.item_id} loan_date={self.loan_date}>"

class PreviousOwner(db.Model):
    """Tracks owner history of articles"""

    __tablename__ = "previous_owners"

    prev_owner_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    old_owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    item_id = db.Column(db.ForeignKey('articles.article_id'), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)

<<<<<<< HEAD
    user = db.relationship('User', backref='previous_owners')
    article = db.relationship('Article', backref='previous_owners')
=======
    user = db.relationship('User', backref='users')
    article = db.relationship('Article', backref='articles')
>>>>>>> 3cfcb4e0bc0ceb09c4a6a55df0f3abed321061af

    def __repr__(self):
        """Provide helpful representation when printed."""
        return f"<Previous Owner old_owner_id={self.old_owner_id} item_id={self.item_id}>"


##############################################################################
# Helper functions

def init_app():
    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print("Connected to DB.")


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our database.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///thecluv'
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    init_app()
