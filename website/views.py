from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from website import db
from .models import Products, Vendor, Orders, User

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

views = Blueprint('views', __name__)


@views.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@views.route("/")
def home():
    products = db.session.query(Products, Vendor).join(Vendor).all()
    return render_template("home.html", user=current_user, products=products)


@views.route("/vendor_home")
@login_required
def vendor_home():
    products = Products.query.filter_by(vendor_id=current_user.id).all()
    return render_template("vendor_home.html", user=current_user, products=products)


@views.route("/create_product", methods=['GET', 'POST'])
@login_required
def create_product():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        quantity = request.form.get('quantity')
        file = request.files['image']

        if not name or not description or not price or not quantity or not file:
            flash("All fields are required!", category="error")
            return redirect(url_for('views.create_product'))



        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            relative_path = os.path.join('uploads', filename)
            new_product = Products(
                name=name,
                description=description,
                price=float(price),
                quantity=int(quantity),
                image=relative_path,  # Store as 'uploads/filename.ext'
                vendor_id=current_user.id
            )
            db.session.add(new_product)
            db.session.commit()

            flash("Product created successfully!", category="success")
            return redirect(url_for('views.vendor_home'))


        else:
            flash("Invalid image format. Allowed formats are: png, jpg, jpeg, gif.", category="error")
            return redirect(url_for('views.create_product'))

    return render_template("create_product.html", user=current_user)


@views.route("/delete_product/<int:product_id>", methods=['POST'])
@login_required
def delete_product(product_id):
    product = Products.query.get_or_404(product_id)

    if product.vendor_id != current_user.id:
        flash("You are not authorized to delete this product.", category="error")
        return redirect(url_for('views.vendor_home'))

    if os.path.exists(os.path.join(UPLOAD_FOLDER, product.image)):
        os.remove(os.path.join(UPLOAD_FOLDER, product.image))

    db.session.delete(product)
    db.session.commit()

    flash("Product deleted successfully!", category="success")
    return redirect(url_for('views.vendor_home'))


@views.route("/order_summary/<int:product_id>", methods=['GET', 'POST'])
def order_summary(product_id):
    if not current_user.is_authenticated:
        flash("You must be logged in to place orders.", category="error")
        return redirect(url_for('views.home'))

    product = Products.query.get_or_404(product_id)

    if request.method == 'POST':
        if product.quantity <= 0:
            flash("Sorry, this product is out of stock.", category="error")
            return redirect(url_for('views.order_summary', product_id=product.id))

        default_status = "pending"

        new_order = Orders(
            product_id=product.id,
            user_id=current_user.id,
            quantity=1,
            status=default_status
        )
        db.session.add(new_order)

        product.quantity -= 1
        db.session.commit()

        flash('Order placed successfully!', category='success')
        return redirect(url_for('views.orders'))

    return render_template('order_summary.html', product=product, user=current_user)


@views.route('/orders')
def orders():
    if not current_user.is_authenticated:  # Check if the user is authenticated
        flash("You must be logged in to view your orders.", category="error")
        return redirect(url_for('views.home'))  # Redirect to the home page

    user_orders = Orders.query.filter_by(user_id=current_user.id).all()
    return render_template('orders.html', orders=user_orders, user=current_user)

@views.route("/cancel_order/<int:order_id>", methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Orders.query.get_or_404(order_id)

    # Ensure the current user is the owner of the order
    if order.user_id != current_user.id:
        flash("You are not authorized to cancel this order.", category="error")
        return redirect(url_for('views.orders'))

    # Update the order status to "cancelled" or similar
    order.status = 'cancelled'
    db.session.commit()

    flash("Order cancelled successfully!", category="success")
    return redirect(url_for('views.orders'))