from click import confirm
from flask import Blueprint, render_template, request, flash, redirect
from werkzeug.security import generate_password_hash,check_password_hash
from .models import User, Vendor
from website import db
from flask_login import login_user,login_required,logout_user,current_user

auth = Blueprint('admin',__name__)


@auth.route("/login",methods=['GET','POST'])
def log():
    if request.method == 'POST':
        email = request.form.get("login_email")
        password = request.form.get("login_password")
        if not email or not password:
            flash("Email and password are required!", category="error")
            return redirect('/login')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password,password):
                login_user(user,remember=True)
                flash("Logged in Successfully!",category="success")
                return redirect('/')
            else:
                flash("Wrong Password!", category="error")
        else:
            flash("User does not exist !", category="error")

    return render_template("login.html",user = current_user)

@auth.route("/vendor_login", methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        email = request.form.get("vendor_email")  # Match this with the form field name
        password = request.form.get("vendor_password")  # Match this with the form field name
        if not email or not password:
            flash("Email and password are required!", category="error")
            return redirect('/vendor_login')  # Redirect back to vendor login page
        vendor = Vendor.query.filter_by(email=email).first()
        if vendor:
            if check_password_hash(vendor.password, password):
                login_user(vendor, remember=True)
                flash("Vendor Logged in Successfully!", category="success")
                return redirect('/vendor_home')
            else:
                flash("Wrong Password!", category="error")
        else:
            flash("Vendor does not exist!", category="error")

    return render_template("vendor_login.html", user=current_user)



@auth.route("/signup",methods=['GET','POST'])
def sign():
    if request.method == 'POST':
        email = request.form.get("email")
        name = request.form.get("name")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists!", category="error")
        elif password != confirm_password:
            flash("Passwords do not match!", category="error")
        elif len(password) < 8:
            flash("Password is too short!", category="error")
        else:
            new_user = User(email=email,password=generate_password_hash(password,method='pbkdf2:sha256'),name=name)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created successfully!",category="success")
            return redirect('/')

    return render_template("signup.html",user=current_user)

@auth.route("/vendor_signup", methods=['GET', 'POST'])
def vendor_signup():
    if request.method == 'POST':
        email = request.form.get("vendor_email")  # Match this with the form field name
        name = request.form.get("vendor_name")  # Match this with the form field name
        password = request.form.get("vendor_password")  # Match this with the form field name
        confirm_password = request.form.get("vendor_confirm_password")  # Match this with the form field name
        vendor = Vendor.query.filter_by(email=email).first()
        if vendor:
            flash("Email already exists!", category="error")
        elif password != confirm_password:
            flash("Passwords do not match!", category="error")
        elif len(password) < 8:
            flash("Password is too short!", category="error")
        else:
            new_vendor = Vendor(email=email, password=generate_password_hash(password, method='pbkdf2:sha256'), name=name)
            db.session.add(new_vendor)
            db.session.commit()
            login_user(new_vendor, remember=True)
            flash("Vendor Account created successfully!", category="success")
            return redirect('/vendor_home')

    return render_template("vendor_signup.html", user=current_user)



@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged Out in Successfully!", category="success")
    return redirect("/")