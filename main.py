from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import datetime
import smtplib
from sqlalchemy.orm import relationship
from functools import wraps
from flask import abort
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import random
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base() 

corp_mail = "tato.tabatadze.1999@gmail.com"
corp_mail_password = "pxiiksgjywzcxite"


global user_info, user_mail, login_bool

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

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)
##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/programing/Desktop/programing/blog_bootstrap/BlogPost/posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE TABLE
class BlogUser(UserMixin, db.Model, Base):
    __tablename__ = 'blog_user'
    id = db.Column(db.Integer, primary_key = True)
    permission = db.Column(db.Integer)
    name = db.Column(db.String(100), nullable = False)
    second_name = db.Column(db.String(100), nullable = False)
    mail = db.Column(db.String(100), nullable = False, unique = True)
    password = db.Column(db.String(100))
    posts = relationship('BlogPost', backref='aut')
    # blog = relationship('BlogPost', backref='author')
    

    def __repr__(self):
        return f'{self.id}'
app.app_context().push()
db.create_all()

class BlogPost(db.Model, Base):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, ForeignKey('blog_user.id'))
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




login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return BlogUser.query.get(user_id)
##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


#### after denied permission return home page
# def admin_test_only(x):
#     @wraps(x)
#     def dec(*args, **kwargs):
#         if current_user.permission != 2:
#             return redirect(url_for('get_all_posts'))
#     return dec

#### after denied permission return 403 error
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.permission != 2:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)        
    return decorated_function

@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)

@app.route('/login', methods = ["POST","GET"])
def login():
    if request.method == "POST":
        data = request.form
        mail = data['mail']
        password = data['password']
        get_info = db.session.query(BlogUser).filter(BlogUser.mail == mail).first()
        if get_info:
            if get_info.password and check_password_hash(pwhash=get_info.password, password=password):
                print('yep')
                login_user(get_info)
                return redirect(url_for("get_all_posts"))
            else:
                return render_template('login.html', txt='Password is Wrong')
        else:
            return render_template('login.html', txt='Email Is Incorrect')
    return render_template('login.html', txt='')

@app.route('/register', methods = ["GET", "POST"])
def register():
    txt = ''
    global user_info, user_mail
    if request.method == "POST":
        name = request.form['name']
        lastName = request.form['lastName']
        mail = request.form['mail']
        password = request.form['password']
        gen_hash = generate_password_hash(password, salt_length=8, method="pbkdf2:sha256")
        user_info = BlogUser(permission = 2, name = name, second_name = lastName, mail = mail, password = gen_hash)
        user_mail = mail
        base_mail = db.session.query(BlogUser).filter(BlogUser.mail == mail).first()
        print(base_mail)
        if base_mail and str(base_mail.mail) == str(mail):
             print('error')
             txt = 'This Mail is Already Used'
        else:
            check_mail()
            return render_template('check.html', txt = "We Send Mail")
     
    return render_template('register.html', txt=txt)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))

@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
    requested_post = db.session.query(BlogPost).get(index)
    print(requested_post.title)
    return render_template("post.html", post=requested_post)

@app.route('/edit_post/<post_id>', methods = ["GET","POST"])
@login_required
@admin_only
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
@login_required
@admin_only
def create():
    form = CreatePostForm()
    if request.method == "POST":
        if form.validate_on_submit():
            print("True")
            print(form.data['title'])
            body_first = form.data['body'].replace('<p>','')
            body_sec = body_first.replace('</p>','')
            new_post = BlogPost(author = form.data['author'],author_id = current_user.id, title = form.data['title'], date = date, body = body_sec, img_url = form.data['img_url'], subtitle = form.data['subtitle'])
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form = form)

@app.route('/delete/<n>')
@login_required
@admin_only
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


def check_mail():
    global rand_num
    rand_num = random.randint(999, 10000)
    with smtplib.SMTP("smtp.gmail.com",587) as connection:
        connection.starttls()
        connection.login(user=corp_mail, password=corp_mail_password)
        connection.sendmail(
            from_addr=corp_mail, 
            to_addrs=user_mail,
            msg=f"""Subject: information about: Registration'\n\n {rand_num}"""
        )
    # if request.args == "Authentication":    
    #     if request.form['number'] == str(rand_num):
            
                
    return render_template('check.html', txt = "Wrong Number")

@app.route('/Authentication', methods = ["POST","GET"])
def check_val():
    global rand_num, user_info
    try:
        if str(request.form['number']) == str(rand_num):
            db.session.add(user_info)
            db.session.commit()
            return render_template('register.html')
        else:
            return render_template('check.html', txt = "Wrong Number")
    except NameError:
        rand_num = 0
    
    return render_template("check.html", txt = "Maybe Somthing Went Wrong Try Send Mail Again")

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5000)