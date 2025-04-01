import base64, io
from io import BytesIO
from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user, login_required

from .. import movie_client
from ..forms import MovieReviewForm, SearchForm, SongRatingForm, SongLikeForm
from ..models import User, Review
from ..utils import current_time

movies = Blueprint("movies", __name__)
""" ************ Helper for pictures uses username to get their profile picture************ """


def get_b64_img(username):
    user = User.objects(username=username).first()
    bytes_im = io.BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image


""" ************ View functions ************ """


@movies.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for("movies.query_results", query=form.search_query.data))

    return render_template("index.html", form=form)


@movies.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    try:
        results = movie_client.search(query)
    except ValueError as e:
        return render_template("query.html", error_msg=str(e))

    return render_template("query.html", results=results)


# NICO: Song rating route
@movies.route("/rate/<movie_id>", methods=["POST"])
@login_required
def rate_song(movie_id):
    try:
        result = movie_client.get_album_by_id(movie_id)
    except ValueError as e:
        return render_template("song_comments.html", error_msg=str(e))
    rating_form = SongRatingForm()
    comment_form = MovieReviewForm()
    
    if rating_form.validate_on_submit():
        rating_value = int(rating_form.rating.data)
        review = Review(
            commenter=current_user._get_current_object(),
            content=f"Rated {rating_value} stars.",
            date=current_time(),
            imdb_id=movie_id,
            movie_title=result.name,
            rating=rating_value,
        )
        review.save()
        flash("Thank you for rating the song!", "success")
        return redirect(url_for("movies.movie_detail", movie_id=movie_id))

    flash("Please select a valid rating before submitting.", "error")
    return redirect(url_for("movies.index", movie_id=movie_id))

# SHAD: Song like route:
@movies.route("/like/<movie_id>", methods=["POST"])
@login_required
def like_song(movie_id):
    try:
        # Retrieve the movie by ID
        result = movie_client.get_album_by_id(movie_id)
    except ValueError as e:
        return render_template("song_comments.html", error_msg=str(e))

    like_form = SongLikeForm()

    # Debug form validation
    if like_form.validate_on_submit():
        print("Form validated!")
        # Get the like choice (1 means liked)
        like_choice = int(like_form.like.data)

        # Save the "Liked!" comment
        liked_comment = Review(
            like=like_choice,
            commenter=current_user._get_current_object(),
            content="Liked!",
            date=current_time(),
            imdb_id=movie_id,
            movie_title=result.name,
        )
        liked_comment.save()
        print("Liked comment saved: ", liked_comment.content)

        flash("Thank you for liking the song!", "success")
        return redirect(url_for("movies.movie_detail", movie_id=movie_id))
    else:
        print("Form validation failed:", like_form.errors)

    flash("An error occurred while processing your like.", "error")
    return redirect(url_for("movies.index"))




# NICO: Song comments route
@movies.route("/movies/<movie_id>", methods=["GET", "POST"])
def movie_detail(movie_id):
    try:
        result = movie_client.get_album_by_id(movie_id)
    except ValueError as e:
        return render_template("song_comments.html", error_msg=str(e))

    rating_form = SongRatingForm()
    like_form = SongLikeForm()
    comment_form = MovieReviewForm()
    if comment_form.validate_on_submit():
        comment = Review(
            commenter=current_user._get_current_object(),
            content=comment_form.text.data,
            date=current_time(),
            imdb_id=movie_id,
            movie_title=result.name,
        )
        comment.save()
        return redirect(request.path)

    comments = Review.objects(imdb_id=movie_id)

    return render_template(
        "song_comments.html",
        rating_form=rating_form,
        like_form=like_form,
        comment_form=comment_form,
        movie=result,
        reviews=comments,
    )



@movies.route("/user/<username>")
def user_detail(username):
    # uncomment to get review image
    # user = find first match in db
    # img = get_b64_img(user.username) use their username for helper function
    return "user_detail"
