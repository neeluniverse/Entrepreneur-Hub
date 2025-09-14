from app import app, db
from models import User, Post, Follow, Like, Comment, Message
from datetime import datetime, timedelta

def seed_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create users
        users = [
            User(
                name='Alice Johnson',
                email='alice@example.com',
                bio='Tech entrepreneur with 10+ years experience',
                skills='Python, JavaScript, Business Strategy',
                avatar_url='https://images.unsplash.com/photo-1494790108755-2616b612b786?ixlib=rb-1.2.1&auto=format&fit=crop&w=200&q=80'
            ),
            User(
                name='Bob Smith',
                email='bob@example.com',
                bio='Startup founder and angel investor',
                skills='Marketing, Finance, Leadership',
                avatar_url='https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-1.2.1&auto=format&fit=crop&w=200&q=80'
            ),
            User(
                name='Carol Davis',
                email='carol@example.com',
                bio='Digital marketing expert and business coach',
                skills='SEO, Social Media, Content Marketing',
                avatar_url='https://images.unsplash.com/photo-1554151228-14d9def656e4?ixlib=rb-1.2.1&auto=format&fit=crop&w=200&q=80'
            )
        ]
        
        for user in users:
            user.set_password('password123')
        
        db.session.add_all(users)
        db.session.commit()
        
        # Create posts
        posts = [
            Post(
                user_id=1,
                content='Just launched my new startup! Excited to share our journey with everyone.',
                image_url='https://images.unsplash.com/photo-1556761175-5973dc0f32e7?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80',
                created_at=datetime.utcnow() - timedelta(days=2)
            ),
            Post(
                user_id=2,
                content='Looking for co-founders with technical background for an innovative fintech idea.',
                created_at=datetime.utcnow() - timedelta(days=1)
            ),
            Post(
                user_id=3,
                content='Just published a new article about growth hacking strategies. Check it out!',
                image_url='https://images.unsplash.com/photo-1581091226033-d5c48150dbaa?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80',
                created_at=datetime.utcnow() - timedelta(hours=5)
            )
        ]
        
        db.session.add_all(posts)
        db.session.commit()
        
        # Create follows
        follows = [
            Follow(follower_id=1, followed_id=2),
            Follow(follower_id=1, followed_id=3),
            Follow(follower_id=2, followed_id=1),
            Follow(follower_id=3, followed_id=1)
        ]
        
        db.session.add_all(follows)
        db.session.commit()
        
        # Create likes
        likes = [
            Like(user_id=2, post_id=1),
            Like(user_id=3, post_id=1),
            Like(user_id=1, post_id=2),
            Like(user_id=1, post_id=3)
        ]
        
        db.session.add_all(likes)
        db.session.commit()
        
        # Create comments
        comments = [
            Comment(
                user_id=2,
                post_id=1,
                content='Congratulations Alice! Looking forward to seeing your progress.'
            ),
            Comment(
                user_id=3,
                post_id=1,
                content='Amazing news! Would love to learn more about your product.'
            )
        ]
        
        db.session.add_all(comments)
        db.session.commit()
        
        # Create messages
        messages = [
            Message(
                sender_id=1,
                recipient_id=2,
                content='Hey Bob, thanks for connecting! I\'d love to get your thoughts on my new startup.'
            ),
            Message(
                sender_id=2,
                recipient_id=1,
                content='Hi Alice! Sure, I\'d be happy to take a look. When are you available for a call?'
            )
        ]
        
        db.session.add_all(messages)
        db.session.commit()
        
        print('Demo data seeded successfully!')

if __name__ == '__main__':
    seed_data()
