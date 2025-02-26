from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///photogram.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
db = SQLAlchemy(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255), nullable=False)
    likes = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('image')
        caption = request.form.get('caption')
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            new_post = Post(image=file.filename, caption=caption)
            db.session.add(new_post)
            db.session.commit()
            flash('Post created successfully!', 'success')
            return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/create', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        return redirect(url_for('upload'))
    return render_template('upload.html')

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        username = request.form.get('username')
        comment_text = request.form.get('comment')
        if username and comment_text:
            new_comment = Comment(post_id=post_id, username=username, text=comment_text)
            db.session.add(new_comment)
            db.session.commit()
            flash('Comment added!', 'success')
        return redirect(url_for('post_detail', post_id=post_id))
    return render_template('post_detail.html', post=post)

@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return redirect(url_for('index'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}

if __name__ == '__main__':
    app.run(debug=True)
