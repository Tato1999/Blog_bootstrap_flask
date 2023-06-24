from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import datetime


date = datetime.datetime.now().date()



## Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/programing/Desktop/programing/blog_bootstrap/BlogPost/posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'{self.id}'
app.app_context().push()
db.create_all()

##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")




@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
    # for blog_post in posts:
    #     print(blog_post)
    #     if blog_post['id'] == index:
    #         requested_post = blog_post
    requested_post = db.session.query(BlogPost).get(index)
    print(requested_post.title)
    return render_template("post.html", post=requested_post)

@app.route('/edit_post/<post_id>', methods = ["GET","POST"])
def edit_post(post_id):
    requested_post = db.session.query(BlogPost).get(post_id)
    edit_form = CreatePostForm(
        title=requested_post.title,
        subtitle=requested_post.subtitle,
        img_url=requested_post.img_url,
        author=requested_post.author,
        body=requested_post.body
    )
    if request.method == "POST":
        if edit_form.validate_on_submit():
            requested_post.title = edit_form.data['title']
            requested_post.subtitle = edit_form.data['subtitle']
            requested_post.img_url = edit_form.data['img_url']
            requested_post.author = edit_form.data['author']
            requested_post.body = edit_form.data['body']
            db.session.commit()
            return redirect(url_for('get_all_posts'))
    return render_template("edit.html", form=edit_form)

@app.route('/create/post', methods=["POST","GET"])
def create():
    form = CreatePostForm()
    if request.method == "POST":
        if form.validate_on_submit():
            print("True")
            print(form.data['title'])
            body_first = form.data['body'].replace('<p>','')
            body_sec = body_first.replace('</p>','')
            new_post = BlogPost(author = form.data['author'], title = form.data['title'], date = date, body = body_sec, img_url = form.data['img_url'], subtitle = form.data['subtitle'])
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form = form)

@app.route('/delete/<n>')
def delete_post(n):
    post = db.session.query(BlogPost).get(n)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route("/about")
def about():
    return render_template("about.html")



@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5000)