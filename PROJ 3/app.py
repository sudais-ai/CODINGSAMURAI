from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'blog_project_2024_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'
login_manager.login_message_category = 'warning'

class UserAccount(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email_address = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    account_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_posts = db.relationship('BlogPost', backref='post_author', lazy=True)

    def set_password(self, password_text):
        self.password_hash = generate_password_hash(password_text)

    def verify_password(self, password_text):
        return check_password_hash(self.password_hash, password_text)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String(100), nullable=False)
    post_content = db.Column(db.Text, nullable=False)
    post_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user_account.id'), nullable=False)

@login_manager.user_loader
def load_user_account(user_id):
    return UserAccount.query.get(int(user_id))

@app.route('/')
def home_page():
    all_posts = BlogPost.query.order_by(BlogPost.post_created.desc()).all()
    return render_template('home.html', posts=all_posts)

@app.route('/home')
def home_redirect():
    return redirect(url_for('home_page'))

@app.route('/user/register', methods=['GET', 'POST'])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        user_name = request.form.get('username', '').strip()
        user_email = request.form.get('email', '').strip().lower()
        user_password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not user_name or not user_email or not user_password:
            flash('All fields are required', 'error')
            return redirect(url_for('register_page'))

        if len(user_name) < 3:
            flash('Username must be at least 3 characters', 'error')
            return redirect(url_for('register_page'))
        
        if len(user_password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(url_for('register_page'))
        
        if user_password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register_page'))

        existing_user = UserAccount.query.filter(
            (UserAccount.username == user_name) | (UserAccount.email_address == user_email)
        ).first()

        if existing_user:
            flash('Username or email already registered', 'error')
            return redirect(url_for('register_page'))

        new_user_account = UserAccount(username=user_name, email_address=user_email)
        new_user_account.set_password(user_password)
        
        try:
            db.session.add(new_user_account)
            db.session.commit()
            flash('Account created successfully! Please login', 'success')
            return redirect(url_for('login_page'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again', 'error')
            return redirect(url_for('register_page'))

    return render_template('register.html')

@app.route('/user/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        user_name = request.form.get('username', '')
        user_password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'

        user_account = UserAccount.query.filter_by(username=user_name).first()

        if user_account and user_account.verify_password(user_password):
            login_user(user_account, remember=remember_me)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user_account.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    user_posts = BlogPost.query.filter_by(author_id=current_user.id).order_by(BlogPost.post_created.desc()).all()
    return render_template('dashboard.html', posts=user_posts)

@app.route('/posts/create', methods=['GET', 'POST'])
@login_required
def create_post_page():
    if request.method == 'POST':
        post_title = request.form.get('post_title', '').strip()
        post_content = request.form.get('post_content', '').strip()

        if not post_title or not post_content:
            flash('Both title and content are required', 'error')
            return redirect(url_for('create_post_page'))

        new_blog_post = BlogPost(
            post_title=post_title, 
            post_content=post_content, 
            post_author=current_user
        )
        
        try:
            db.session.add(new_blog_post)
            db.session.commit()
            flash('Post published successfully!', 'success')
            return redirect(url_for('user_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to create post. Please try again', 'error')
            return redirect(url_for('create_post_page'))

    return render_template('create_post.html')

@app.route('/posts/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post_page(post_id):
    blog_post = BlogPost.query.get_or_404(post_id)

    if blog_post.post_author != current_user:
        flash('You can only edit your own posts', 'error')
        return redirect(url_for('user_dashboard'))

    if request.method == 'POST':
        post_title = request.form.get('post_title', '').strip()
        post_content = request.form.get('post_content', '').strip()

        if not post_title or not post_content:
            flash('Both title and content are required', 'error')
            return redirect(url_for('edit_post_page', post_id=blog_post.id))

        blog_post.post_title = post_title
        blog_post.post_content = post_content
        
        try:
            db.session.commit()
            flash('Post updated successfully!', 'success')
            return redirect(url_for('user_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update post. Please try again', 'error')
            return redirect(url_for('edit_post_page', post_id=blog_post.id))

    return render_template('edit_post.html', post=blog_post)

@app.route('/posts/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post_action(post_id):
    blog_post = BlogPost.query.get_or_404(post_id)

    if blog_post.post_author != current_user:
        flash('You can only delete your own posts', 'error')
        return redirect(url_for('user_dashboard'))

    try:
        db.session.delete(blog_post)
        db.session.commit()
        flash('Post deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to delete post. Please try again', 'error')
    
    return redirect(url_for('user_dashboard'))

@app.route('/user/logout')
@login_required
def logout_user_action():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('home_page'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)