from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Crop, Interest, Notification
from models import Crop

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Mysql@localhost/farmer_marketplace'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        notifications_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    else:
        notifications_count = 0
    return dict(notifications_count=notifications_count)

@app.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.role == 'buyer':
            return redirect(url_for('buyer_dashboard'))
        if current_user.role == 'seller':
            return redirect(url_for('seller_dashboard'))
    return render_template("home.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']

        user = User(name=name, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully! Login now.", "success")
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Logged in successfully!", "success")
            if user.role=='seller':
                return redirect(url_for('seller_dashboard'))
            else:
                return redirect(url_for('buyer_dashboard'))
        else:
            flash("Invalid Credentials", "danger")
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for('home'))

# ---------------- Dashboards ----------------
@app.route('/seller_dashboard')
@login_required
def seller_dashboard():
    return render_template("seller_dashboard.html")


@app.route("/buyer_dashboard")
@login_required
def buyer_dashboard():
    crops = Crop.query.all()   # Get all crops
    return render_template("buyer_dashboard.html", crops=crops)

# @app.route('/buyer_dashboard')
# @login_required
# def buyer_dashboard():
#     return render_template("buyer_dashboard.html")

# ---------------- Add Crop ----------------
@app.route('/add_crop', methods=['GET','POST'])
@login_required
def add_crop():
    if request.method=='POST':
        crop = Crop(
            seller_id=current_user.id,
            crop_name=request.form['crop_name'],
            land_area=request.form['land_area'],
            quantity=request.form['quantity'],
            unit=request.form['unit'],
            rate=request.form['rate'],
            harvest_date=request.form['harvest_date'],
            description=request.form['description']
        )
        db.session.add(crop)
        db.session.commit()
        flash("Crop added successfully!", "success")
        return redirect(url_for('seller_dashboard'))
    return render_template("add_crops.html")

# ---------------- View Crops for Buyer ----------------
@app.route('/view_crops')
@login_required
def view_crops():
    crops = Crop.query.all()
    return render_template("view_crops.html", crops=crops)

# ---------------- Show Interest ----------------
@app.route('/show_interest/<int:crop_id>')
@login_required
def show_interest(crop_id):
    crop = Crop.query.get_or_404(crop_id)
    existing = Interest.query.filter_by(buyer_id=current_user.id, crop_id=crop_id).first()
    if existing:
        flash("Already shown interest!", "warning")
        return redirect(url_for('view_crops'))
    interest = Interest(crop_id=crop_id, buyer_id=current_user.id)
    db.session.add(interest)
    db.session.commit()
    # Notification for seller
    notification = Notification(user_id=crop.seller_id,
                                message=f"{current_user.name} is interested in your crop {crop.crop_name}!")
    db.session.add(notification)
    db.session.commit()
    flash("Interest sent to seller!", "success")
    return redirect(url_for('view_crops'))

# ---------------- Seller Requests ----------------
@app.route('/seller_requests')
@login_required
def seller_requests():
    interests = Interest.query.join(Crop).filter(Crop.seller_id==current_user.id).all()
    return render_template("seller_request.html", interests=interests)

# ---------------- Update Request (accept/reject) ----------------
@app.route('/update_request/<int:interest_id>/<action>')
@login_required
def update_request(interest_id, action):
    interest = Interest.query.get_or_404(interest_id)
    crop = Crop.query.get(interest.crop_id)

    if action=='accept':
        interest.status='accepted'
        msg = f"Your interest in {crop.crop_name} has been accepted!"
    elif action=='reject':
        interest.status='rejected'
        msg = f"Your interest in {crop.crop_name} has been rejected!"
    else:
        flash("Invalid action!", "warning")
        return redirect(url_for('seller_requests'))

    notification = Notification(user_id=interest.buyer_id, message=msg)
    db.session.add(notification)
    db.session.commit()
    flash("Request updated!", "success")
    return redirect(url_for('seller_requests'))

# ---------------- Notifications ----------------
@app.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template("notifications.html", notifications=notifications)

if __name__ == '__main__':
    app.run(debug=True)
