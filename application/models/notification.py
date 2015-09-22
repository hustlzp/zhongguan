# coding: utf-8
from flask import json
from datetime import datetime
from ._base import db


class NOTIFICATION_KIND(object):
    COMMENT_PIECE = 1
    COMMENT_PIECE_COMMENT = 2
    UPVOTE_PIECE = 3


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.Integer, nullable=False)
    checked = db.Column(db.Boolean, nullable=False, default=False)
    checked_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)

    senders_list = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic',
                                                      order_by="desc(Notification.created_at)",
                                                      cascade="all, delete, delete-orphan"),
                           foreign_keys=[user_id])

    piece_id = db.Column(db.Integer, db.ForeignKey('piece.id'))
    piece = db.relationship('Piece')

    piece_comment_id = db.Column(db.Integer, db.ForeignKey('piece_comment.id'))
    piece_comment = db.relationship('PieceComment')

    def add_sender(self, sender_id):
        """添加发起者"""
        senders_list = set(json.loads(self.senders_list or "[]"))
        senders_list.add(sender_id)
        self.senders_list = json.dumps(list(senders_list))

    @property
    def senders(self):
        """该消息的全部发起者"""
        from .user import User
        if not self.senders_list:
            return None
        senders_id_list = json.loads(self.senders_list)
        return User.query.filter(User.id.in_(senders_id_list))

    @staticmethod
    def upvote_piece(user, piece):
        """赞同piece"""
        noti = Notification.query.filter(
            Notification.user_id == piece.user_id,
            Notification.kind == NOTIFICATION_KIND.UPVOTE_PIECE,
            ~Notification.checked,
            Notification.piece_id == piece.id).first()
        if noti:
            noti.add_sender(user.id)
            db.session.add(noti)
        else:
            noti = Notification(kind=NOTIFICATION_KIND.UPVOTE_PIECE, senders_list=json.dumps([user.id]),
                                piece_id=piece.id, user_id=piece.user.id)
            db.session.add(noti)

    @staticmethod
    def comment_piece(user, piece_comment):
        """评论piece"""

        noti = Notification(kind=NOTIFICATION_KIND.COMMENT_PIECE, senders_list=json.dumps([user.id]),
                            piece_comment_id=piece_comment.id, user_id=piece_comment.piece.user_id)
        db.session.add(noti)

    @staticmethod
    def comment_piece_comment(user, piece_comment):
        """回复piece comment"""
        noti = Notification(kind=NOTIFICATION_KIND.COMMENT_PIECE_COMMENT, senders_list=json.dumps([user.id]),
                            piece_comment_id=piece_comment.id, user_id=piece_comment.target_user_id)
        db.session.add(noti)
