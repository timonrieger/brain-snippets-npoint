from datetime import date
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from forms import CreatePostForm
import os
import requests
import json
import pyperclip
import dotenv

dotenv.load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY_KEY'] = os.getenv("SECRET_KEY")

ckeditor = CKEditor(app)
Bootstrap5(app)

try:
    blog_data = requests.get(f"https://api.npoint.io/{os.getenv("NPOINT")}").json()[::-1]
except Exception:
    with open("static/assets/backup.json", "r") as file:
        blog_data = json.load(file)[::-1]

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


@app.route("/<post_title>", methods=["GET", "POST"])
def show_post(post_title):
    # Convert the post_title to lowercase and replace spaces with dashes
    post_title = post_title.lower().replace(' ', '-')

    # Find the requested post
    requested_post = [post for post in blog_data if
                      post["title"].lower().replace(' ', '-') == post_title]

    return render_template("post.html", post=requested_post[0])

@app.route("/new-post", methods=["GET", "POST"])
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():

        new_post_data = {
            "id": 0,
            "title": form.title.data,
            "subtitle": form.subtitle.data,
            "date": date.today().strftime("%B %d, %Y"),
            "author": form.author.data,
            "image_url": form.img_url.data,
            "body": form.body.data,
        }
        # Convert the dictionary to a JSON string
        json_data = json.dumps(new_post_data, indent=2)

        try:
            # Copy the JSON data to the clipboard
            pyperclip.copy(json_data)
            flash(f"Post copied to clipboard. Paste here: https://www.npoint.io/docs/{os.getenv("NPOINT")}")
        except pyperclip.PyperclipException:
            flash("Failed to copy post to clipboard. Please copy manually.")

        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)

@app.route("/npoint")
def npoint():
    return redirect(f"https://www.npoint.io/docs/{os.getenv("NPOINT")}")


if __name__ == "__main__":
    app.run(debug=False)


