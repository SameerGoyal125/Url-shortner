from flask import *
from pandas import *
from random import choice
import pyperclip
from pyqrcode import *
# from pypng import *
import math
import random
import smtplib
login = 0
admin = 0
user = ""
emailid=""
ruser=""
rpass=""
verified=0
gvotp=0
gotp=0
m_url=""
lenq=1
al = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w',
      'x', 'y', 'z']
num = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def login():
    global login, admin, user,m_url
    if admin == 1 and login == 1:
        return redirect('/admin')

    elif admin == 0 and login == 1:
        return redirect('/user')
    message = ""
    m_url=request.base_url
    if request.method == "POST":

        user = request.form['user']
        passw = request.form['password']
        b = read_csv("user.csv")
        q = b["user"].tolist()
        w=b["email"].tolist()
        if user == "admin" and passw == "password":
            login = 1
            admin = 1
            return redirect('/admin')
        elif user in q or user in w:
            if passw == b[b["user"] == user]["password"].to_string(index=False):
                login = 1
                admin = 0
                return redirect('/user')
            elif passw == b[b["email"] == user]["password"].to_string(index=False):
                login = 1
                admin = 0
                user=b[b["email"] == user]["user"].to_string(index=False)
                return redirect('/user')
            else:
                message = "Invalid Credentials"
        else:
            message = "Invalid Credentials"
    return render_template('index.html', message=message)


@app.route('/generate', methods=['GET', 'POST'])
def home():
    global user, login,m_url
    if login == 0:
        return redirect("/")
    elif login == 1:
        if request.method == "POST":
            sht = ""
            taken = 0
            data = pandas.read_csv("urls.csv")
            shrt = data["short"].tolist()
            if request.form['special']:
                if request.form['special'] in shrt:
                    taken = 1
                else:
                    sht = request.form['special']
            else:
                for x in range(0, 2):
                    sht += str(choice(al))
                    sht += str(choice(num))
            if taken == 0:
                shorturl = {
                    'short': [sht],
                    'urls': [request.form['url']],
                    'created_by': [user]
                }
                df = pandas.DataFrame(shorturl)
                df.to_csv('urls.csv', mode='a', index=False, header=False)
                sgh = "Your link is " + m_url + sht
                s=request.form['url']
                urlq = pyqrcode.create(s)
                urlq.svg("myqr.svg", scale=8)
                # urlq.png('myqr.png', scale=6)
                pyperclip.copy(m_url+sht)
            else:
                sgh = request.form['special'] + " is already taken"
            return render_template('generate.html', short=sgh)
    return render_template('generate.html')


@app.route('/signup', methods=['GET', 'POST'])
def sign():
    global ruser,rpass,verified,emailid
    verified = 0
    message=""
    if request.method == "POST":
        ruser = request.form['user']
        emailid=request.form['email']
        rpass = request.form['password']
        a = read_csv('user.csv')
        usr=a["user"].tolist()
        eml=a["email"].tolist()
        if ruser in usr:
            message=ruser+" is already taken."
        elif emailid in eml:
            message = emailid + " is already registered."
        else:
            verified=1
            return redirect("/verify")

    return render_template('signup.html',message=message)


@app.route('/<search>')
def urls(search):
    data = pandas.read_csv("urls.csv")
    shrt = data["short"].tolist()
    if search in shrt:
        return redirect(data[data["short"] == search]["urls"].to_string(index=False))
    else:
        return "Not Found"


@app.route('/delete/<int:i>')
def delete(i):
    global login, user
    if admin == 0 and login == 1:
        a = read_csv("urls.csv")
        sw = a.iloc[i].created_by
        if sw == user:
            a = a.drop(i)
            a.to_csv('urls.csv', index=False)
        else:
            return "You don't have access"
    elif login == 1 and admin == 1:
        a = read_csv("urls.csv")
        a = a.drop(i)
        a.to_csv('urls.csv', index=False)

    return redirect('/')


@app.route('/user')
def user():
    global login
    global user,lenq
    if login == 0 and admin == 0:
        return redirect('/')
    elif login == 1 and admin == 0:
        b = read_csv('urls.csv')
        a = b[b["created_by"] == user]
        Action = []
        for i in range(0, len(a.index)):
            Action.append(
                f'''<button type="button" class="buttom"name="button" onclick="window.location.href = '/delete/{a.index[i]}'">Delete</button>''')
        a['Action'] = Action
        indexes = []
        for i in range(1, len(a.index) + 1):
            indexes.append(i)
        a.index = indexes
        colors={
            'selector':'body',
            'props': 'background-color: black; color: white;'
        }

        a = a.drop('created_by', 1)
        a=a.style.set_table_styles([colors])
        html_file='''<!DOCTYPE html>
        <html lang="en" dir="ltr">
        <head>
        <meta charset="utf-8">
        <title>User History</title>
        <link rel="stylesheet" href="{{ url_for('static',filename='table.css') }}">
        
        </head>
        <body>
    <div class="main">
      <div class="butn">
        <button onclick="window.location.href = '/generate'">Generate</button>
      <button onclick="window.location.href = '/signout'">Sign Out</button>
      </div>
      <div class="tcover">
      <div class="table">
        <h1>Your History</h1>'''+a.to_html()+'''</div>
    </div>
  </div>
  </body>
</html>'''

        html = open("templates/userh.html", "w")
        html.write(html_file)
        if len(a.index) == 0:
            lenq=0
        else:
            lenq=1
        return redirect('/user/history')
    return redirect("/")


@app.route('/user/history')
def history():
    global login, admin,lenq
    if login == 1 and admin == 0:
        if lenq==0:
            return render_template('empty.html')
        else:
            return render_template('userh.html')
    else:
        return redirect("/")
    return redirect("/")


@app.route('/admin')
def admin():
    global login, admin, user
    if admin == 0:
        return redirect('/')
    elif admin == 1:
        a = read_csv("urls.csv")
        Action = []

        for i in range(0, len(a.index)):
            Action.append(
                f'''<button type="button" class="buttom"name="button" onclick="window.location.href = '/delete/{a.index[i]}'">Delete</button>''')
        a['Action'] = Action
        a.index += 1
        colors = {
            'selector': 'body',
            'props': 'background-color: black; color: white;'
        }
        a = a.style.set_table_styles([colors])
        html_file = '''<!DOCTYPE html>
                <html lang="en" dir="ltr">
                <head>
                <meta charset="utf-8">
                <title>User History</title>
                <link rel="stylesheet" href="{{ url_for('static',filename='table.css') }}">
                </head>
                <body>
            <div class="main">
              <div class="butn">
                <button onclick="window.location.href = '/generate'">Generate</button>
              <button onclick="window.location.href = '/signout'">Sign Out</button>
              </div>
              <div class="tcover">
              <div class="table">
                <h1>All History</h1>''' + a.to_html() + '''</div>
            </div>
          </div>
          </body>
        </html>'''
        html = open("templates/table.html", "w")
        html.write(html_file)

        return render_template('table.html')
    return redirect('/')


@app.route('/signout')
def signout():
    global login, admin,user,ruser,rpass
    login = 0
    admin = 0
    user=""
    return redirect("/")

@app.route('/verify',methods=['GET', 'POST'])
def verify():
    global emailid,gotp,gvotp,gotp,verified
    rotp=""

    message=""
    if verified==0:
        return redirect("/signup")
    else:
        OTP = gotp
        if gvotp==0:
            digits = "0123456789"
            OTP = ""

            for i in range(6):
                OTP += digits[math.floor(random.random() * 10)]
            otp = "Subject:Otp \n\n"+ OTP + " is your OTP"
            gvotp=1

            OTP=int(OTP)
            gotp=OTP
            msg = otp
            s = smtplib.SMTP("smtp.mail.yahoo.com",587)
            s.starttls()
            s.login(user="short.it@yahoo.com", password="qneiztmlgiruotzq")
            s.sendmail(from_addr='short.it@yahoo.com',to_addrs=emailid, msg=msg)
            s.close()
        if request.method=="POST":
            rotp=request.form["otp"]
            rotp=int(rotp)
        if rotp:
            if rotp==OTP:
                reg_user = {
                    'email':emailid,
                    'user': [ruser],
                    'password': [rpass]
                }
                a = pandas.DataFrame(reg_user)
                a.to_csv('user.csv', mode='a', index=False, header=False)
                gvotp == 0
                verified = 0
                return redirect("/")
            else:
                message="Wrong Otp"
    return render_template("otp.html",message=message)

if __name__ == '__main__':
    app.run(port=8000,debug=True)
