from datetime import datetime as dt, date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List
# Import your forms from the forms.py
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
import smtplib, os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(20)
ckeditor = CKEditor(app)
Bootstrap5(app)

# TODO: Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

admins = ["timon@riegerx.de", "maxkompass@gmail.com"]

# TODO: Configure Flask-Gravatar
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///blog.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CONFIGURE TABLES
# TODO: Create a User table for all your registered users.
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False)
    #Relationships
    posts: Mapped[List["BlogPost"]] = relationship("BlogPost", back_populates="author")
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="comment_author")

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    # Relationships
    author: Mapped[str] = relationship("User", back_populates="posts")
    author_id: Mapped[int] = db.Column(Integer, db.ForeignKey("users.id"))
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="parent_post")

class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    time: Mapped[str] = mapped_column(String, nullable=False)
    #Relationships
    author_id: Mapped[int] = db.Column(Integer, db.ForeignKey("users.id"))
    comment_author: Mapped[str] = relationship("User", back_populates="comments")
    post_id: Mapped[int] = db.Column(Integer, db.ForeignKey("blog_posts.id"))
    parent_post: Mapped[str] = relationship("BlogPost", back_populates="comments")

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

def admin_only(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            if current_user.email not in admins:
                return abort(403)
            return function(*args, **kwargs)
        else:
            return redirect(url_for("login"))
    return decorated_function

# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        already_user = db.session.execute(db.Select(User).where(User.email == register_form.email.data)).scalar()
        username_used = db.session.execute(db.Select(User).where(User.username == register_form.username.data)).scalar()
        if already_user:
            flash("You've already signed up with that email, log in instead.")
            return redirect(url_for("login"))
        elif username_used:
            flash("This username is already taken, choose another one.")
        elif not already_user:
            new_user = User(
                email=register_form.email.data,
                password=generate_password_hash(register_form.password.data, "pbkdf2:sha256", salt_length=8),
                username=register_form.username.data
            )

            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            flash("Registered and logged in successfully.")

            return redirect(url_for("get_all_posts"))

    return render_template("register.html", form=register_form)


# TODO: Retrieve a user from the database based on their email. 
@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = db.session.execute(db.Select(User).where(User.email == login_form.email.data)).scalar()
        if not user:
            flash("Register first.")
            return redirect(url_for("register"))
        elif check_password_hash(user.password, login_form.password.data):
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for("get_all_posts"))
        else:
            flash('Wrong password, try again.')

    return render_template("login.html", form=login_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost)).scalars().all()
    # page = int(request.args.get("page", 1))
    # start = (page - 1) * 10
    # end = page * 10
    # posts = result[start:end]
    # if not posts:
        # page = 1
        # start = 0
        # end = 10
        # posts = result[start:end]
    page = 1
    posts = result[::-1]
    return render_template("index.html", all_posts=posts, page=page, admins=admins)


# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    # post_comments = db.session.execute(db.select(Comment).where(Comment.post_id == post_id)).scalars()
    # comment_form = CommentForm()
    # if comment_form.validate_on_submit():
    #     if current_user.is_authenticated:
    #         time = dt.now().strftime("%b %d, %Y") + " at " + dt.now().strftime("%H:%M")
    #         new_comment = Comment(
    #             text=comment_form.comment.data,
    #             comment_author=current_user,
    #             parent_post=db.get_or_404(BlogPost, post_id),
    #             time=time
    #         )
    #         db.session.add(new_comment)
    #         db.session.commit()
    #         return redirect(url_for('show_post', post_id=post_id))
    #     else:
    #         flash("You need to login or register to comment")
    #         return redirect(url_for("login"))
    return render_template("post.html", post=requested_post) #, comments=post_comments, form=comment_form)
    # <!--        <div class="comment mb-5">
    #           &lt;!&ndash; TODO: Show all the comments on a post &ndash;&gt;
    #           <ul class="commentList">
    #             {% for comment in comments %}
    #             <li>
    #               <div class="commenterImage">
    #                 <img src="{{ comment.comment_author.email | gravatar }}" />
    #               </div>
    #               <div class="commentText">
    #                 <p>{{ comment.text }}</p>
    #                 <span class="date sub-text">{{ comment.comment_author.username }} | {{ comment.time }}</span>
    #               </div>
    #             </li>
    #             {% endfor %}
    #           </ul>
    #         </div>
    #         &lt;!&ndash; TODO: Add a CKEditor for commenting below &ndash;&gt;
    #         {{ render_form(form) }}-->


# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        data = request.form
        send_email(data["name"], data["email"], data["phone"], data["message"])
        return render_template("contact.html", msg_sent=True)
    return render_template("contact.html", msg_sent=False)


def send_email(name, email, phone, message):
    email_message = f"Subject:New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:{message}"
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login("timonriegerx@gmail.com", "gzxi ilon zzir uusv")
        connection.sendmail("timonriegerx@gmail.com", "timonriegerx@gmail.com", email_message)


if __name__ == "__main__":
    app.run(debug=False)
