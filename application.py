import os
from flask import Flask, flash, render_template, redirect, request, url_for,session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import login_required, error, timestampformat

# Configure application
app = Flask(__name__)

# Configure database
engine = create_engine(os.getenv("DATABASE"))
db = scoped_session(sessionmaker(bind=engine))

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure secret key for session encryption
app.secret_key = os.urandom(20)

# Custom filter
app.jinja_env.filters["timestampformat"] = timestampformat

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """ Show home page """

    if session.get("user_id") is None:
        return render_template("index.html")
    all_posts = db.execute("SELECT * FROM users, post WHERE post.post_publisher = users.user_id ORDER BY post.post_timestamp DESC").fetchall()
    return render_template("home.html",all_posts=all_posts)


@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register a new User """
    
    # Forget any user_id
    session.pop("user_id",None)

    # user reached the route via POST (as by submitting the form)
    if request.method == 'POST':
        # return an error message if the fullname field is empty
        if not request.form.get("fullname"):
            return error(message="Missing Fullname")
        # return an error message if the username field is empty
        elif not request.form.get("username"):
            return error(message="Missing Username")
        # return an error message if the email field is empty
        elif not request.form.get("email"):
            return error(message="Missing Email")
        # return an error message if the password field is empty
        elif not request.form.get("password"):
            return error(message="Missing Password")
        # return an error message if the confirm password field is empty or passwords don't match
        elif not request.form.get("confirmpassword") or request.form.get("password") != request.form.get("confirmpassword"):
            return error(message="Must Confirm Password")
        # return an error message if the phone field is empty
        elif not request.form.get("phone"):
            return error(message="Missing Phone Number")
        else:
            # check the availability of the username
            usernames = (user["username"] for user in db.execute("SELECT username FROM users").fetchall())
            if request.form.get("username") in usernames:
                return error(message="Username already exists")
            # check the availability of the email
            emails = (user["email"] for user in db.execute("SELECT email FROM users").fetchall())
            if request.form.get("email") in emails:
                return error(message="Email already exists")
            # check the availability of the username
            phones = (user["phone"] for user in db.execute("SELECT phone FROM users").fetchall())
            if request.form.get("phone") in phones:
                return error(message="Phone Number already exists")
            # hash the password
            pass_hash = generate_password_hash(request.form.get("password"),'pbkdf2:sha256',8)
            # try insert the user
            ins_user = db.execute("INSERT INTO users (username,fullname,email,password_hash,phone) VALUES (:username,:fullname,:email,:password_hash,:phone)", 
                        {"username":request.form.get("username"),"fullname":request.form.get("fullname"),"email":request.form.get("email"),"password_hash":pass_hash,"phone":request.form.get("phone")})
            if not ins_user:
                return error(message="Register Error")
            # commit changes
            db.commit()
            # query database to get user id
            user_id = db.execute("SELECT user_id,username FROM users WHERE username=:username AND email=:email AND phone=:phone",
                                {"username": request.form.get("username"),"email": request.form.get("email"), "phone": request.form.get("phone")}).fetchone()
            # Log the user in
            session["user_id"] = user_id["user_id"]
            flash("Welcome, " + user_id["username"])
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
            return error(message="Missing Username or Email")
        # return an error message if password field is empty
        if not request.form.get("password"):
            return error(message="Missing Password")
        
        # query the database to check if the username or email is correct
        tmp_user = db.execute("SELECT * FROM users WHERE username = :username or email = :email",{"username":request.form.get("userlogin"),"email":request.form.get("userlogin")}).fetchone()

        # return an error if the userlogin does not exist or the password isn't correct
        if not tmp_user or not check_password_hash(tmp_user["password_hash"],request.form.get("password")):
            return error(message="Login info or Password are wrong")

        # log in the user
        session["user_id"] = tmp_user["user_id"]
        flash("Welcome Back, " + tmp_user["username"])
        return redirect(url_for('index'))
    
    # user reached the route via GET
    return render_template("login.html")

@app.route("/logout")
def logout():
    """ Log out the user """

    # Forget any user_id
    session.pop("user_id",None)
    return redirect(url_for('index'))

@app.route("/users")
@login_required
def users():
    """ Show list of users """

    users = db.execute("SELECT * FROM users").fetchall()
    return render_template("users.html",users=users)

@app.route("/users/<username>")
def userprofile(username):
    """ Show posts posted by a specified user """

    # query database to see posts by the specified username
    user_posts = db.execute("SELECT * FROM users,post WHERE users.user_id = post.post_publisher AND users.username = :usr_name", {"usr_name": username}).fetchall()
    # check query success
    if not user_posts:
        # check if the username specified exists
        check_username = db.execute("SELECT * FROM users WHERE username = :usr_name", {"usr_name": username}).fetchone()
        if not check_username:
            return error(message="Username does not exists")
        # if username exists and the the query throwed an error this means that the user has no posts
        return render_template("userposts.html",posts=None,username=username)
    # return the posts and the username
    return render_template("userposts.html",posts=user_posts,username=username)

@app.route("/publish",methods=["GET","POST"])
@login_required
def publish():
    """ Publish a new post """

    # user reached the route via POST
    if request.method == "POST":
        # return an error message if post title field is empty
        if not request.form.get("posttitle"):
            return error(message="Missing Post Title")
        # return an error message if post content field is empty
        if not request.form.get("postcontent"):
            return error(message="Missing Post Content")
        db.execute("INSERT INTO post (post_title,post_content,post_publisher) VALUES (:post_title,:post_content,:post_publisher)", {"post_title":request.form.get("posttitle"),"post_content":request.form.get("postcontent"),"post_publisher":session["user_id"]})
        db.commit()
        return redirect(url_for('myactivity'))
    # user reached the route via GET
    return render_template("publish.html")

@app.route("/posts/<postid>",methods=["GET","POST"])
def posts(postid):
    """ Show a post content or submit a comment """

    # user reached the route via POST (by submitting the comment form)
    if request.method == "POST":
        # if the user is not logged in redirect him to login page
        if session.get("user_id") is None:
            return redirect(url_for('login'))
        # if the user is logged in, we try to submit the content
        comment = db.execute("INSERT INTO comment (comment_content,comment_post,comment_writer) VALUES (:content,:postid,:userid)", {"content":request.form.get("mycomment"),"postid":postid,"userid":session["user_id"]})
        # if there is an error inserting the comment, return an error
        if not comment:
            return error(message="Error inserting the comment")
        # else, commit the query
        db.commit()

    # user reached the route via GET
    # query database to get post detail
    post_detail = db.execute("SELECT * FROM users,post WHERE users.user_id = post.post_publisher AND post.post_id=:postid", {"postid":postid}).fetchone()
    if not post_detail:
        # return an error
        return error(message="This Post dosen't exist")
    # query database to get the post's comments if any
    comments = db.execute("SELECT * FROM users,comment WHERE users.user_id = comment.comment_writer AND comment_post = :post_id", {"post_id": postid}).fetchall()
    if not comments:
        # render template without comments if there is no comments
        return render_template("posts.html",thepost=post_detail,comments=None)
    
    # render template with post detail and its comments
    return render_template("posts.html",thepost=post_detail,comments=comments)

@app.route("/myactivity",methods=["GET","POST"])
@login_required
def myactivity():
    """ Show posts published by the user logged in """

    posts = db.execute("SELECT * FROM users, post WHERE post.post_publisher = users.user_id AND post.post_publisher=:current_user ORDER BY post.post_timestamp DESC",{"current_user":session["user_id"]}).fetchall()
    return render_template("myactivity.html",posts=posts)

@app.route("/delete/<postid>")
@login_required
def delete(postid):
    """ Delete a post """

    # ensure that the logged in user is the post publisher
    check_user = db.execute("SELECT * FROM post WHERE post_id = :postid", {"postid": postid}).fetchone()
    if not check_user or check_user["post_publisher"] != session["user_id"]:
        return error(message="You can't delete this post")

    # try to delete the post
    delete_post = db.execute("DELETE FROM post WHERE post_id = :postid", {"postid": postid})
    if not delete_post:
        return error(message="Error Deleting the post")
    
    # commit changes
    db.commit()
    return redirect(url_for('index'))

@app.route("/changepassword",methods=["GET","POST"])
@login_required
def changepassword():
    """ Change a password """

    # user reached the route via POST
    if request.method == "POST":
        # return an error message if currentpassword field is empty
        if not request.form.get("currentpassword"):
            return error(message="Must Provide Your Current Password")
        # return an error message if newpassword field is empty
        elif not request.form.get("newpassword"):
            return error(message="Must Provide Your New Password")
        # return an error message if confirmpassword field is empty
        elif not request.form.get("confirmpassword"):
            return error(message="Must Confirm Your New Password")
        # return an error message if new password dosen't match
        elif request.form.get("newpassword") != request.form.get("confirmpassword"):
            return error(message="Password Don't Match")
        else:
            # query database to verify current password
            password = db.execute("SELECT * FROM users WHERE user_id = :user_id", {"user_id": session["user_id"]}).fetchone()
            if not check_password_hash(password["password_hash"],request.form.get("currentpassword")):
                return error(message="Current Password is Wrong")

            # update user's password
            query = db.execute("UPDATE users SET password_hash = :password_hash WHERE user_id = :user_id", {"password_hash": generate_password_hash(request.form.get("newpassword"),'pbkdf2:sha256',8), "user_id":session["user_id"]})
            if not query:
                return error(message="Can't Update password")
            else:
                # commit changes
                db.commit()
                flash("Password Changed Successfully")
                return redirect(url_for('login'))
    # user reached the route via GET
    return render_template("changepassword.html")

@app.route("/terms")
def terms():
    """ Show Terms of service page """
    return render_template("terms.html")

@app.route("/about")
def about():
    """ Show about page """
    return render_template("about.html")

@app.route("/posts")
@login_required
def all_posts():
    """ Show all post by redirecting to index """
    return redirect(url_for("index"))

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return error(code="500")

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)