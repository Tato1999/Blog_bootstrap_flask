from flask import Flask, render_template, request
import smtplib
import requests

end_point = requests.get('https://api.npoint.io/3c3dd32fec7a2d357262')

my_mail = "****************"
password = "**************"


app = Flask(__name__)
def send_mail(name,mail,msg):
   
    with smtplib.SMTP("smtp.gmail.com",587) as connection:
        connection.starttls()
        connection.login(user=my_mail, password=password)
        connection.sendmail(
            from_addr=my_mail, 
            to_addrs="***************",
            msg=f"Subject: {name}\n\n {mail} \n contact:{msg}"
        )
@app.route('/')
def home():
    print(end_point.json())
    return render_template('index.html', posts = end_point.json())

@app.route('/post/<n>')
def post(n):
    post = None
    print(type(n))
    for i in end_point.json():
        if i['id'] == int(n):
            post = i
        print(i['id'])
    return render_template('post.html', m = post)
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact',methods=["GET","POST"])
def contact():
    if request.method == "POST":
        data = request.form
        print(data["name"])
        print(data["email"])
        print(data["phone"])
        send_mail(data["name"], data["msg"], data["email"])
        # return render_template("contact.html", msg_sent=True)
    return render_template("contact.html", msg_sent=False)

if __name__ == '__main__':
    app.run(debug=True)
