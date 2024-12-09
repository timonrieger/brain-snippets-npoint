from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField

# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    body = CKEditorField("Blog Content (Make sure to copy your draft somewhere first)", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

