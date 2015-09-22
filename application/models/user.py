# coding: utf-8
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from ._base import db
from ..utils.uploadsets import avatars


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    avatar = db.Column(db.String(200), default='default.png')
    motto = db.Column(db.String(100))
    password = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    votes_count = db.Column(db.Integer, default=0)
    pieces_count = db.Column(db.Integer, default=0)
    voters_count = db.Column(db.Integer, default=0)
    liked_collections_count = db.Column(db.Integer, default=0)

    # 设置
    receive_comments_notification = db.Column(db.Boolean, default=True)
    receive_votes_notification = db.Column(db.Boolean, default=True)

    # 社交媒体
    weibo = db.Column(db.String(100))
    zhihu = db.Column(db.String(100))
    douban = db.Column(db.String(100))
    blog = db.Column(db.String(100))

    def __setattr__(self, name, value):
        # Hash password when set it.
        if name == 'password':
            value = generate_password_hash(value)
        super(User, self).__setattr__(name, value)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def update_voters_count(self):
        self.voters_count = self.voters.filter(Voter.count > 0).count()

    @property
    def avatar_url(self):
        return avatars.url(self.avatar)

    def __repr__(self):
        return '<User %s>' % self.name


class Voter(db.Model):
    """点赞者"""
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), default=None)
    user = db.relationship('User',
                           backref=db.backref('voters',
                                              lazy='dynamic',
                                              cascade="all, delete, delete-orphan"),
                           foreign_keys=[user_id])

    voter_id = db.Column(db.Integer, db.ForeignKey('user.id'), default=None)
    voter = db.relationship('User', foreign_keys=[voter_id])
