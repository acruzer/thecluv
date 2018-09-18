"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import User
from model import Article
from model import Image
from model import ArticleImage
from model import ArticleType
from model import Loan
from model import Article
from model import PreviousOwner

from model import connect_to_db, db
from server import app

import datetime


def load_users():
    """Load users from u.user into database."""

    print("Users")

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/users_seed.txt"):
        row = row.rstrip()
        user_id, fname, lname, username, password, email, user_img, zipcode = row.split("|")

        user = User(user_id=user_id,
                    fname=fname,
                    lname=lname,
                    username=username,
                    password=password,
                    email=email,
                    user_img=user_img,
                    zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_articles():
    """Load articles into database."""

    print ("Articles")

    Article.query.delete()

    for row in open("seed_data/articles_seed.txt"):
        row = row.rstrip()
        owner_id, type_id, size, color, material, notes, is_private, is_loanable, is_giveaway = row.split("|")

        is_private = True if is_private == "T" else False
        is_loanable = True if is_loanable == "T" else False
        is_giveaway = True if is_giveaway == "T" else False

        article = Article(owner_id=owner_id,
                    type_id=type_id,
                    size=size,
                    color=color,
                    material=material,
                    notes=notes,
                    is_private=is_private,
                    is_loanable=is_loanable,
                    is_giveaway=is_giveaway)

        # We need to add to the session or it won't ever be stored
        db.session.add(article)

    # Once we're done, we should commit our work
    db.session.commit()



def load_types():
    """Load types into database."""

    print("Article Types")

    ArticleType.query.delete()

    for row in open("seed_data/type_seed.txt"):
        row = row.rstrip()
        type_id, name = row.split("|")

        article_type = ArticleType(type_id=type_id,
                    name=name)

        # We need to add to the session or it won't ever be stored
        db.session.add(article_type)

    # Once we're done, we should commit our work
    db.session.commit()


def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    print(max_id)

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()




# def set_val_user_id():
#     """Set value for the next user_id after seeding database"""

#     # Get the Max user_id in the database
#     result = db.session.query(func.max(User.user_id)).one()
#     max_id = int(result[0])

#     # Set the value for the next user_id to be max_id + 1
#     query = "SELECT setval('users_user_id_seq', :new_id)"
#     db.session.execute(query, {'new_id': max_id + 1})
#     db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_types()
    load_articles()
    set_val_user_id()
