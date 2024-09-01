from functools import wraps
from flask_login import current_user
from flask import redirect, flash
from .models import Vendor

def vendor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Vendor):
            flash("Access denied. This page is for vendors only.", category="error")
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function
