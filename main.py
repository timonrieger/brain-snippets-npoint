from datetime import date
import requests, json, pyperclip
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from forms import CreatePostForm
import smtplib, os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(20)

ckeditor = CKEditor(app)
Bootstrap5(app)

EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")

class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///blog.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)

blog_data = requests.get("https://api.npoint.io/55ec3c86cd78032d2742").json()[::-1]

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()

@app.route('/')
def get_all_posts():
    page = int(request.args.get("page", 1))
    start = (page - 1) * 10
    end = page * 10
    posts = blog_data[start:end]
    if not posts:
        page = 1
        start = 0
        end = 10
        posts = blog_data[start:end]
    return render_template("index.html", all_posts=posts, page=page)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = [post for post in blog_data if post["id"] == post_id]

    return render_template("post.html", post=requested_post[0])

@app.route("/new-post", methods=["GET", "POST"])
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            date=date.today().strftime("%B %d, %Y"),
            author=form.author.data
        )

        new_post_data = {
            "id": new_post.id,
            "title": form.title.data,
            "subtitle": form.subtitle.data,
            "body": form.body.data,
            "date": date.today().strftime("%B %d, %Y"),
            "author": form.author.data,
            "image_url": form.img_url.data
        }
        # Convert the dictionary to a JSON string
        json_data = json.dumps(new_post_data, indent=2)

        # Copy the JSON data to the clipboard
        pyperclip.copy(json_data)
        flash("Post copied to clipboard. Paste here: https://www.npoint.io/docs/55ec3c86cd78032d2742")

        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:npoint_id>", methods=["GET", "POST"])
def edit_post(npoint_id):
    post = db.session.execute(db.Select(BlogPost).where(BlogPost.id == 1)).scalar()
    print(BlogPost.query.all())
    if post:
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
            post.body = edit_form.body.data
            post.author = edit_form.author.data
            db.session.commit()

            new_post_data = {
                "id": npoint_id,
                "title": post.title,
                "subtitle": post.subtitle,
                "body": post.body,
                "date": post.date,
                "author": post.author,
                "image_url": post.img_url
            }
            # Convert the dictionary to a JSON string
            json_data = json.dumps(new_post_data, indent=2)

            # Copy the JSON data to the clipboard
            pyperclip.copy(json_data)
            flash("Post copied to clipboard. Paste here: https://www.npoint.io/docs/55ec3c86cd78032d2742")

            return redirect(url_for("get_all_posts"))
        return render_template("make-post.html", form=edit_form, is_edit=True)
    else:
        flash("You cannot update this post anymore. Update the npoint: https://www.npoint.io/docs/55ec3c86cd78032d2742 or delete and rewrite this post.")
        return redirect(url_for("get_all_posts"))


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
    email_message = f"Subject:Blog Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}"
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(EMAIL, PASSWORD)
        connection.sendmail(EMAIL, EMAIL, email_message)


if __name__ == "__main__":
    app.run(debug=False)


