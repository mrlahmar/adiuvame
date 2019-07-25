import os
from flask import Flask, flash, render_template, redirect, request, url_for,session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import login_required

# Configure application
app = Flask(__name__)

# Configure database
engine = create_engine(os.getenv("DATABASE"))
db = scoped_session(sessionmaker(bind=engine))

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure secret key for session encryption
app.secret_key = os.urandom(20)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register a new User """
    
    # Forget any user_id
    session.pop("user_id",None)

    # user reached the route via POST (as by submitting the form)
    if request.method == 'POST':
        # return an error message if the fullname field is empty
        if not request.form.get("fullname"):
            return "<h1>MISSING FULLNAME</h1>"
        # return an error message if the username field is empty
        elif not request.form.get("username"):
            return "<h1>MISSING USERNAME</h1>"
        # return an error message if the email field is empty
        elif not request.form.get("email"):
            return "<h1>MISSING EMAIL</h1>"
        # return an error message if the password field is empty
        elif not request.form.get("password"):
            return "<h1>MISSING PASSWORD</h1>"
        # return an error message if the confirm password field is empty or passwords don't match
        elif not request.form.get("confirmpassword") or request.form.get("password") != request.form.get("confirmpassword"):
            return "<h1>MUST CONFIRM PASSWORD</h1>"
        # return an error message if the phone field is empty
        elif not request.form.get("phone"):
            return "<h1>PHONE NOT PROVIDED</h1>"
        # return an error message if the account type field is not correct
        elif not request.form.get("account_type") or request.form.get("account_type") != 'D' and request.form.get("account_type") != 'H':
            return "<h1>MUST CHOOSE A CORRECT ACCOUNT TYPE</h1>"
        else:
            # check the availability of the username
            usernames = (user["username"] for user in db.execute("SELECT username FROM users").fetchall())
            if request.form.get("username") in usernames:
                return "EXISTING USERNAME"
            # check the availability of the email
            emails = (user["email"] for user in db.execute("SELECT email FROM users").fetchall())
            if request.form.get("email") in emails:
                return "EXISTING EMAIL"
            # check the availability of the username
            phones = (user["phone"] for user in db.execute("SELECT phone FROM users").fetchall())
            if request.form.get("phone") in phones:
                return "EXISTING PHONE"
            # hash the password
            pass_hash = generate_password_hash(request.form.get("password"),'pbkdf2:sha256',8)
            # insert the user
            db.execute("INSERT INTO users (username,fullname,email,password_hash,phone,account_type) VALUES (:username,:fullname,:email,:password_hash,:phone,:account_type)", 
                        {"username":request.form.get("username"),"fullname":request.form.get("fullname"),"email":request.form.get("email"),"password_hash":pass_hash,"phone":request.form.get("phone"),"account_type":request.form.get("account_type")})
            db.commit()
            # query database to get user id
            user_id = db.execute("SELECT user_id FROM users WHERE username=:username AND email=:email AND phone=:phone",
                                {"username": request.form.get("username"),"email": request.form.get("email"), "phone": request.form.get("phone")}).fetchone()
            # Log the user in
            session["user_id"] = user_id["user_id"]
            return redirect(url_for('users'))
    
    # user reached the route via GET
    return render_template("register.html")


@app.route("/login",methods=["GET","POST"])
def login():
    """ Log in the User """
    
    # Forget any user_id
    session.pop("user_id",None)

    # user reached the route via POST (as by submitting the form)
    if request.method == 'POST':
        # return an error message if userlogin field is empty
        if not request.form.get("userlogin"):
            return "<h1>USERNAME NOT PROVIDED</h1>"
        # return an error message if password field is empty
        if not request.form.get("password"):
            return "<h1>PASSWORD NOT PROVIDED</h1>"
        
        # query the database to check if the username or email is correct
        tmp_user = db.execute("SELECT * FROM users WHERE username = :username or email = :email",{"username":request.form.get("userlogin"),"email":request.form.get("userlogin")}).fetchone()

        # return an error if the userlogin does not exist or the password isn't correct
        if not tmp_user or not check_password_hash(tmp_user["password_hash"],request.form.get("password")):
            return "<h1>ERROR</h1>"

        # log in the user
        session["user_id"] = tmp_user["user_id"]
        return redirect(url_for('index'))
    
    # user reached the route via GET
    return render_template("login.html")

@app.route("/logout")
def logout():
    # Forget any user_id
    session.pop("user_id",None)
    return redirect(url_for('index'))

@app.route("/users")
def users():
    users = db.execute("SELECT * FROM users").fetchall()
    return render_template("users.html",users=users)

@app.route("/publish",methods=["GET","POST"])
@login_required
def publish():
    # user reached the route via POST
    if request.method == "POST":
        # return an error message if post title field is empty
        if not request.form.get("posttitle"):
            return "<h1>MISSING POST TITLE</h1>"
        # return an error message if post content field is empty
        if not request.form.get("postcontent"):
            return "<h1>MISSING POST CONTENT</h1>"
        db.execute("INSERT INTO post (post_title,post_content,post_publisher) VALUES (:post_title,:post_content,:post_publisher)", {"post_title":request.form.get("posttitle"),"post_content":request.form.get("postcontent"),"post_publisher":session["user_id"]})
        db.commit()
        return redirect(url_for('myactivity'))
    # user reached the route via GET
    return render_template("publish.html")

@app.route("/posts/<postid>",methods=["GET","POST"])
def posts(postid):
    post_detail = db.execute("SELECT * FROM post WHERE post_id=:postid", {"postid":postid}).fetchone()
    if not post_detail:
        return "ERROR DB"
    return render_template("posts.html",thepost=post_detail)

@app.route("/myactivity",methods=["GET","POST"])
@login_required
def myactivity():
    posts = db.execute("SELECT * FROM post WHERE post_publisher=:current_user",{"current_user":session["user_id"]}).fetchall()
    return render_template("myactivity.html",posts=posts)

@app.route("/settings",methods=["GET","POST"])
@login_required
def settings():
    return render_template("settings.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return "ERROR"

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)