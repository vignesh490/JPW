from flask import Flask, render_template, request, redirect, url_for, session
from database import get_database
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "jobportal_secret"


# HOME PAGE
@app.route("/")
def home():
    return render_template("home.html")


# REGISTER
@app.route("/register", methods=["GET","POST"])
def register():

    db = get_database()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]

        db.execute(
        "INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
        (name,email,password,role))

        db.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


# LOGIN
@app.route("/login", methods=["GET","POST"])
def login():

    db = get_database()

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = db.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)).fetchone()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["role"] = user["role"]

            if user["role"] == "employer":
                return redirect(url_for("employer_dashboard"))
            else:
                return redirect(url_for("jobs"))

    return render_template("login.html")


# JOB LIST
@app.route("/jobs")
def jobs():

    db = get_database()

    jobs = db.execute("SELECT * FROM jobs").fetchall()

    return render_template("job_list.html", jobs=jobs)


# JOB DETAILS
@app.route("/job/<int:id>")
def job_detail(id):

    db = get_database()

    job = db.execute(
    "SELECT * FROM jobs WHERE id=?",
    (id,)).fetchone()

    return render_template("job_detail.html", job=job)


# APPLY JOB
@app.route("/apply/<int:id>")
def apply(id):

    db = get_database()

    db.execute(
    "INSERT INTO applications(job_id,user_id,status) VALUES(?,?,?)",
    (id, session["user_id"], "Applied"))

    db.commit()

    return redirect(url_for("jobs"))


# EMPLOYER DASHBOARD
@app.route("/employer")
def employer_dashboard():

    db = get_database()

    jobs = db.execute(
    "SELECT * FROM jobs WHERE employer_id=?",
    (session["user_id"],)).fetchall()

    return render_template("employer_dashboard.html", jobs=jobs)


# POST JOB
@app.route("/post-job", methods=["GET","POST"])
def post_job():

    db = get_database()

    if request.method == "POST":

        title = request.form["title"]
        company = request.form["company"]
        location = request.form["location"]
        salary = request.form["salary"]
        description = request.form["description"]

        db.execute(
        """INSERT INTO jobs
        (title,company,location,salary,description,employer_id)
        VALUES(?,?,?,?,?,?)""",
        (title,company,location,salary,description,session["user_id"]))

        db.commit()

        return redirect(url_for("employer_dashboard"))

    return render_template("post_job.html")


# VIEW APPLICANTS
@app.route("/applicants/<int:jobid>")
def applicants(jobid):

    db = get_database()

    applicants = db.execute("""
    SELECT users.name, users.email, applications.status
    FROM applications
    JOIN users ON users.id = applications.user_id
    WHERE applications.job_id=?
    """,(jobid,)).fetchall()

    return render_template("applicants.html", applicants=applicants)


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)