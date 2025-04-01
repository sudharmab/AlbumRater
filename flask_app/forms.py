from ast import Pass
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, RadioField, HiddenField
from wtforms.validators import (
    InputRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
)


from .models import User


class SearchForm(FlaskForm):
    search_query = StringField(
        "Query", validators=[InputRequired(), Length(min=1, max=100)]
    )
    submit = SubmitField("Search")


class MovieReviewForm(FlaskForm):
    text = TextAreaField(
        "Comment", validators=[InputRequired(), Length(min=5, max=500)]
    )
    submit = SubmitField("Enter Comment")


# NICO: Form for star ratings for songs
class SongRatingForm(FlaskForm):
    rating = RadioField(
        "Rate the Song",
        choices=[("5", "1 ★"), ("4", "2 ★"), ("3", "3 ★"), ("2", "4 ★"), ("1", "5 ★")],
        validators=[InputRequired()],
    )
    submit = SubmitField("Submit Rating")

#SHAD: Form for liking a song/album 
class SongLikeForm(FlaskForm):
    like = RadioField(
        "Like this song",
        choices=[("1", "Liked")],  # Only one choice: liked (1)
        validators=[InputRequired()]
    )
    submit = SubmitField("Submit Like")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is taken")

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user is not None:
            raise ValidationError("Email is taken")


# TODO: implement fields
class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


# TODO: implement
class UpdateUsernameForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    submit_username = SubmitField("Update")

    # TODO: implement
    def validate_username(self, username):
        updated_user = User.objects(username=username.data).first()
        if updated_user and updated_user.id != current_user.id:
            raise ValidationError("Username is taken")


# TODO: implement
class UpdateProfilePicForm(FlaskForm):
    picture = FileField(
        "Profile Picture",
        validators=[
            FileRequired(),
            FileAllowed(["jpg", "png"], "Please use .jpg and .png files only"),
        ],
    )
    submit_picture = SubmitField("Update")
