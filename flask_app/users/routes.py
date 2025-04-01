from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required, login_user, logout_user
import base64
import io
from io import BytesIO
from .. import bcrypt
from werkzeug.utils import secure_filename
from ..forms import (
    RegistrationForm,
    LoginForm,
    UpdateUsernameForm,
    UpdateProfilePicForm,
)
from ..models import User, Review


users = Blueprint("users", __name__)

""" ************ User Management views ************ """


# TODO: implement
@users.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data, email=form.email.data, password=hashed_password
        )
        user.save()
        return redirect(url_for("users.login"))

    return render_template("register.html", form=form)


# TODO: implement
@users.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    # if current_user.is_authenticated:
    # return redirect(url_for('movies.index'))

    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("users.account"))
        else:
            flash("Login failed. Check your username and/or password.", "danger")

    return render_template("login.html", form=form)


# TODO: implement
@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("movies.index"))


@users.route("/user/<username>")
@login_required
def user_detail(username):
    user = User.objects(username=username).first()
    reviews = Review.objects(commenter=user)
    
    bytes_im = io.BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return render_template(
        "user_detail.html", user=user, reviews=reviews, error=None, image=image
    )


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    update_username_form = UpdateUsernameForm()
    update_profile_pic_form = UpdateProfilePicForm()
    reviews = Review.objects(user=current_user)
    profile_pic = None
    if current_user.profile_pic.get() is not None:
        bytes_im = BytesIO(current_user.profile_pic.read())
        profile_pic = base64.b64encode(bytes_im.getvalue()).decode()

    if request.method == "POST":
        if update_username_form.submit_username.data and update_username_form.validate():
            new_name = update_username_form.username.data
            existing_user = User.objects(username=new_name).first()

            if existing_user:
                flash("Username is taken, choose another username", "danger")
            else:
                current_user.modify(username=new_name)
                current_user.save()
                flash("Your username is updated!", "success")
                return redirect(url_for("users.account"))


        if update_profile_pic_form.submit_picture.data and update_profile_pic_form.validate():
            pic_file = update_profile_pic_form.picture.data
            filename = secure_filename(pic_file.filename)
            content_type = f'image/{filename.split(".")[-1]}'


            if current_user.profile_pic.get() is None:
                current_user.profile_pic.put(pic_file.stream, content_type=content_type)
            else:
                current_user.profile_pic.replace(pic_file.stream, content_type=content_type)
                
            current_user.save()  
            flash("picture updated!", "success")
           
            if current_user.profile_pic.get() is not None:

                bytes_im = BytesIO(current_user.profile_pic.read())
                profile_pic = base64.b64encode(bytes_im.getvalue()).decode()
                return redirect(url_for("users.account"))
        
        # TODO: handle get requests
    return render_template(
        "account.html",
        update_username_form= update_username_form,
        update_profile_pic_form= update_profile_pic_form,
        user= current_user,
        image = profile_pic,
        reviews = reviews
    )

