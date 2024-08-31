from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from replit import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Trh@ckn0n'

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

class User(UserMixin):
    def __init__(self, username, email, password, id, is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.is_admin = is_admin

    @staticmethod
    def get_user(user_id):
        users = db.get("users", [])
        for user in users:
            if user["id"] == user_id:
                return User(user["username"], user["email"], user["password"], user["id"], user.get("is_admin", False))
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get_user(int(user_id))

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        users = db.get("users", [])
        if any(user["username"] == username.data for user in users):
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        users = db.get("users", [])
        if any(user["email"] == email.data for user in users):
            raise ValidationError('That email is already in use. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    is_admin = BooleanField('Admin')
    submit = SubmitField('Save Changes')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user_id = len(db.get("users", [])) + 1
        new_user = {
            "id": user_id,
            "username": form.username.data,
            "email": form.email.data,
            "password": hashed_password,
            "is_admin": False  
        }
        users = db.get("users", [])
        users.append(new_user)
        db["users"] = users
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        users = db.get("users", [])
        user = next((u for u in users if u["email"] == form.email.data), None)
        if user and bcrypt.check_password_hash(user["password"], form.password.data):
            user_obj = User(user["username"], user["email"], user["password"], user["id"], user.get("is_admin", False))
            login_user(user_obj, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
    loverooms = db.get("loverooms", [])
    return render_template('index.html', loverooms=loverooms)

@app.route('/loveroom/<int:id>')
@login_required
def loveroom_detail(id):
    loverooms = db.get("loverooms", [])
    loveroom = next((lr for lr in loverooms if lr["id"] == id), None)
    if loveroom is None:
        flash('Loveroom not found', 'danger')
        return redirect(url_for('index'))
    return render_template('loveroom_detail.html', loveroom=loveroom)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        loveroom_name = request.form.get('name')
        if loveroom_name:
            loverooms = db.get("loverooms", [])
            loveroom_id = len(loverooms) + 1
            new_loveroom = {"id": loveroom_id, "name": loveroom_name}
            loverooms.append(new_loveroom)
            db["loverooms"] = loverooms
            flash('Loveroom added successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Please provide a name for the loveroom.', 'danger')

    return render_template('add.html')
@app.route('/users')
@login_required
def users():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    users = db.get('users', [])
    return render_template('users.html', users=users)

@app.route('/user/<int:id>', methods=['GET', 'POST'])
@login_required
def user_detail(id):
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    users = db.get('users', [])
    user = next((u for u in users if u["id"] == id), None)
    if user is None:
        flash('User not found', 'danger')
        return redirect(url_for('users'))

    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        user["username"] = form.username.data
        user["email"] = form.email.data
        user["is_admin"] = form.is_admin.data
        db["users"] = users
        flash('User updated successfully!', 'success')
        return redirect(url_for('users'))

    return render_template('user_detail.html', form=form, user=user)

@app.route('/delete_user/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    users = db.get('users', [])
    users = [user for user in users if user["id"] != id]
    db["users"] = users
    flash('User has been deleted.', 'success')
    return redirect(url_for('users'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)