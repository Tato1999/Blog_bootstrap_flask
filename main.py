from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import datetime
import smtplib


corp_mail = "tato.tabatadze.1999@gmail.com"
corp_mail_password = "pxiiksgjywzcxite"


date = datetime.datetime.now().date()

def send_mail(s,n,m,b):
    with smtplib.SMTP("smtp.gmail.com",587) as connection:
        connection.starttls()
        connection.login(user=corp_mail, password=corp_mail_password)
        connection.sendmail(
            from_addr=corp_mail, 
            to_addrs=corp_mail,
            msg=f"""Subject: information about: {s}'\n\ncontact:\nNumber: {n}\nEmail: {m}\n
            {b}"""
        )

# def send_confirm_mail(m):
#     with smtplib.SMTP('stmp.gmail.com',587) as connection:
#         connection.starttls()
#         connection.login(user=corp_mail,password=corp_mail_password)
#         connection.sendmail(
#             from_addr=corp_mail, 
#             to_addrs=m,
#             msg=f"""Mail Successful Recived"""
#         )
### code need fixing//have socket error, need client to wait when script connect right port

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



@app.route("/contact", methods = ["GET","POST"])
def contact():
    print('name')
    if request.method == 'POST':
        name = request.form['name']
        mail = request.form['mail']
        tel = request.form['tel']
        msg = request.form['msg']
        print(type(mail))
        print(mail)
        if mail == '' :
            return render_template('contact.html', MSG = "Fail:First fill Email Address Graph")
        else:
            if name == '':
                return render_template('contact.html', MSG = "Fail:First fill Name Graph")
            else:
                if tel == '':
                    return render_template('contact.html', MSG = "Fail:First fill Number Graph")
                else:
                    send_mail(name,tel,mail,msg)
                    print(mail)
                    return render_template('contact.html', MSG = "Success")
                    

    return render_template("contact.html", MSG = 'Want to get in touch? Fill out the form below to send me a message and I will get back to you as soon as possible!')


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5000)