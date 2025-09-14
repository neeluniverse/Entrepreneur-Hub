import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Post, Like, Comment, Follow, Message
from forms import SignupForm, LoginForm, PostForm, EditProfileForm
from sqlalchemy import or_
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    # In production, you'd normally use migrations (Alembic), but for simplicity we're using create_all().
    db.create_all()

@app.route('/')
def home():
    if current_user.is_authenticated:
        # Get posts from followed users and own posts
        followed_ids = [f.followed_id for f in current_user.following]
        posts = Post.query.filter(
            (Post.user_id.in_(followed_ids)) | (Post.user_id == current_user.id)
        ).order_by(Post.created_at.desc()).all()
        return render_template('home.html', posts=posts)
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = SignupForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            bio=form.bio.data,
            skills=form.skills.data,
            avatar_url=form.avatar_url.data or 'https://via.placeholder.com/150'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()
    is_following = False
    if current_user.is_authenticated:
        is_following = Follow.query.filter_by(
            follower_id=current_user.id, followed_id=user_id
        ).first() is not None
    return render_template('profile.html', user=user, posts=posts, is_following=is_following)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.bio = form.bio.data
        current_user.skills = form.skills.data
        current_user.avatar_url = form.avatar_url.data or 'https://via.placeholder.com/150'
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile', user_id=current_user.id))
    return render_template('edit_profile.html', form=form)

@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            content=form.content.data,
            image_url=form.image_url.data,
            user_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('new_post.html', form=form)

@app.route('/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'liked': False, 'likes_count': len(post.likes)})
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        return jsonify({'liked': True, 'likes_count': len(post.likes)})

@app.route('/comment_post/<int:post_id>', methods=['POST'])
@login_required
def comment_post(post_id):
    content = request.json.get('content')
    if not content:
        return jsonify({'error': 'Comment content required'}), 400
    comment = Comment(
        user_id=current_user.id,
        post_id=post_id,
        content=content
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({
        'comment': {
            'content': comment.content,
            'author_name': comment.author.name,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
        }
    })

@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow(user_id):
    user = User.query.get_or_404(user_id)
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot follow yourself'}), 400
    follow = Follow.query.filter_by(
        follower_id=current_user.id, followed_id=user_id
    ).first()
    if follow:
        db.session.delete(follow)
        db.session.commit()
        return jsonify({'followed': False, 'followers_count': len(user.followers)})
    else:
        follow = Follow(follower_id=current_user.id, followed_id=user_id)
        db.session.add(follow)
        db.session.commit()
        return jsonify({'followed': True, 'followers_count': len(user.followers)})

@app.route('/messages')
@login_required
def messages():
    # Get all users that the current user has messaged or received messages from
    sent_to = db.session.query(Message.recipient_id).filter(Message.sender_id == current_user.id).distinct()
    received_from = db.session.query(Message.sender_id).filter(Message.recipient_id == current_user.id).distinct()
    user_ids = set([id for (id,) in sent_to] + [id for (id,) in received_from])
    
    contacts = User.query.filter(User.id.in_(user_ids)).all()
    return render_template('messages.html', contacts=contacts)

@app.route('/messages/<int:user_id>')
@login_required
def conversation(user_id):
    other_user = User.query.get_or_404(user_id)
    messages = Message.query.filter(
        or_(
            (Message.sender_id == current_user.id) & (Message.recipient_id == user_id),
            (Message.sender_id == user_id) & (Message.recipient_id == current_user.id)
        )
    ).order_by(Message.created_at.asc()).all()
    
    # Mark messages as read
    unread_messages = Message.query.filter_by(
        sender_id=user_id, recipient_id=current_user.id, read=False
    ).all()
    for msg in unread_messages:
        msg.read = True
    db.session.commit()
    
    return jsonify({
        'messages': [{
            'id': msg.id,
            'sender_id': msg.sender_id,
            'content': msg.content,
            'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_sent': msg.sender_id == current_user.id
        } for msg in messages]
    })

@app.route('/send_message/<int:recipient_id>', methods=['POST'])
@login_required
def send_message(recipient_id):
    content = request.json.get('content')
    if not content:
        return jsonify({'error': 'Message content required'}), 400
    message = Message(
        sender_id=current_user.id,
        recipient_id=recipient_id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    return jsonify({
        'message': {
            'id': message.id,
            'sender_id': message.sender_id,
            'content': message.content,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_sent': True
        }
    })

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return render_template('search.html')
    
    users = User.query.filter(
        or_(
            User.name.ilike(f'%{query}%'),
            User.skills.ilike(f'%{query}%')
        )
    ).all()
    
    posts = Post.query.filter(Post.content.ilike(f'%{query}%')).all()
    
    return render_template('search.html', users=users, posts=posts, query=query)

@app.context_processor
def inject_unread_count():
    if current_user.is_authenticated:
        unread_count = Message.query.filter_by(recipient_id=current_user.id, read=False).count()
        return dict(unread_count=unread_count)
    return dict(unread_count=0)

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', False))
