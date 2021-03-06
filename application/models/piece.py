# coding: utf-8
import qrcode
import math
from flask import g
from urlparse import urlparse
from datetime import datetime, date, timedelta
from pypinyin import pinyin, lazy_pinyin
from ._base import db
from ..utils.uploadsets import qrcodes, save_image
from ..utils.helpers import absolute_url_for


class Word(db.Model):
    """词"""
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now)
    first_letter = db.Column(db.String(1))

    def __setattr__(self, name, value):
        """首字母"""
        if name == 'word' and value != '':
            super(Word, self).__setattr__('first_letter', lazy_pinyin(value)[0][0])
        super(Word, self).__setattr__(name, value)

    @staticmethod
    def get_word(word_content):
        word = Word.query.filter(Word.word == word_content).first()
        if not word:
            word = Word(word=word_content)
            db.session.add(word)
            db.session.commit()
        return word


class Piece(db.Model):
    """Model for text piece"""
    id = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(db.Text)  # 例句
    content = db.Column(db.Text)
    content_length = db.Column(db.Integer, default=0)
    original = db.Column(db.Boolean, default=False)
    author = db.Column(db.String(100))
    source = db.Column(db.String(100))
    source_link = db.Column(db.String(200))
    source_link_title = db.Column(db.String(200))
    clicks_count = db.Column(db.Integer, default=0)
    votes_count = db.Column(db.Integer, default=0)
    qrcode = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('pieces',
                                                      lazy='dynamic',
                                                      order_by='desc(Piece.created_at)'))

    word_id = db.Column(db.Integer, db.ForeignKey('word.id'))
    word = db.relationship('Word', backref=db.backref('pieces',
                                                      lazy='dynamic',
                                                      order_by='desc(Piece.created_at)'))

    def __setattr__(self, name, value):
        # Hash password when set it.
        if name == 'content':
            super(Piece, self).__setattr__('content_length', Piece.calculate_content_length(value))
        super(Piece, self).__setattr__(name, value)

    @staticmethod
    def create(word, content, sentence, user):
        word = Word.get_word(word)
        piece = Piece(content=content, sentence=sentence, word=word, user=user)
        db.session.add(piece)
        db.session.commit()

        piece.make_qrcode()
        db.session.add(piece)

        if not user.pieces_count:
            user.pieces_count = 1
        else:
            user.pieces_count += 1

        db.session.add(user)
        db.session.commit()

        return piece

    @property
    def friendly_content(self):
        return '<br>'.join(self.content.splitlines())

    @property
    def friendly_sentence(self):
        return '<br>'.join(self.sentence.splitlines())

    @property
    def source_link_favicon(self):
        result = urlparse(self.source_link)
        host = "%s://%s" % (result.scheme or "http", result.netloc)
        return "http://g.soz.im/%s" % host

    @property
    def qrcode_url(self):
        return qrcodes.url(self.qrcode) if self.qrcode else ""

    @property
    def source_string(self):
        if self.original:
            return ""
        result_str = ""
        if self.author:
            result_str += self.author
        if self.source:
            result_str += "《%s》" % self.source
        return result_str

    @property
    def weibo_share_url(self):
        template = "http://service.weibo.com/share/share.php?searchPic=false&title=%s&url=%s"
        title = self.content
        if self.source_string:
            title += " —— %s" % self.source_string
        url = absolute_url_for('piece.view', uid=self.id)
        return template % (title, url)

    @property
    def root_comments(self):
        return self.comments.filter(PieceComment.root_comment_id == None)

    @staticmethod
    def get_by_word(word):
        return Piece.query.filter(Piece.word == word)

    @staticmethod
    def calculate_content_length(content):
        cn_length = (len(bytes(content)) - len(content)) / 2
        en_length = len(content) - cn_length
        return cn_length + int(math.ceil(en_length / 2.0))

    def voted_by_user(self):
        if not g.user:
            return False
        return g.user.voted_pieces.filter(PieceVote.piece_id == self.id).count() > 0

    def make_qrcode(self):
        qr = qrcode.QRCode(box_size=10, border=0)
        qr.add_data(absolute_url_for('piece.h5', uid=self.id))
        qr.make(fit=True)
        img = qr.make_image()
        self.qrcode = save_image(img, qrcodes, 'png')

    @staticmethod
    def get_pieces_data_by_day(day):
        """获取某天的pieces"""
        SHOW_PIECES_COUNT = 20
        pieces_count = Piece.query.filter(db.func.date(Piece.created_at) == day).count()
        hide_pieces_count = pieces_count - SHOW_PIECES_COUNT if pieces_count > SHOW_PIECES_COUNT \
            else 0
        if hide_pieces_count:
            hide_pieces = pieces = Piece.query.filter(
                db.func.date(Piece.created_at) == day).order_by(
                Piece.votes_count.desc()).offset(SHOW_PIECES_COUNT)
        else:
            hide_pieces = None
        pieces = Piece.query.filter(db.func.date(Piece.created_at) == day). \
            order_by(Piece.votes_count.desc()). \
            order_by(Piece.created_at.desc()). \
            limit(SHOW_PIECES_COUNT)
        if day == date.today():
            date_string = '今天'
        elif day == date.today() - timedelta(days=1):
            date_string = '昨天'
        else:
            date_string = "%s年%s月%s日" % (day.year, day.month, day.day)

        return {
            'date': day,
            'pieces': pieces,
            'hide_pieces': hide_pieces,
            'hide_pieces_count': hide_pieces_count
        }


class PieceVote(db.Model):
    """每日文字的投票（顶）"""
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('voted_pieces',
                                                      lazy='dynamic',
                                                      order_by='desc(PieceVote.created_at)'))

    piece_id = db.Column(db.Integer, db.ForeignKey('piece.id'))
    piece = db.relationship('Piece', backref=db.backref('voters',
                                                        lazy='dynamic',
                                                        cascade="all, delete, delete-orphan",
                                                        order_by='asc(PieceVote.created_at)'))


class PieceComment(db.Model):
    """文字评论"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    votes_count = db.Column(db.Integer, default=0)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
                           foreign_keys=[user_id],
                           backref=db.backref('piece_comments',
                                              lazy='dynamic',
                                              order_by='desc(PieceComment.created_at)'))

    target_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    target_user = db.relationship('User', foreign_keys=[target_user_id])

    root_comment_id = db.Column(db.Integer, db.ForeignKey('piece_comment.id'))
    root_comment = db.relationship('PieceComment',
                                   remote_side=[id],
                                   backref=db.backref('sub_comments',
                                                      lazy='dynamic',
                                                      order_by='asc(PieceComment.created_at)'))

    piece_id = db.Column(db.Integer, db.ForeignKey('piece.id'))
    piece = db.relationship('Piece', backref=db.backref('comments',
                                                        lazy='dynamic',
                                                        cascade="all, delete, delete-orphan",
                                                        order_by='asc(PieceComment.created_at)'))

    def voted_by_user(self):
        return g.user and g.user.voted_piece_comments.filter(
            PieceCommentVote.piece_comment_id == self.id).count() > 0


class PieceCommentVote(db.Model):
    """针对文字评论的赞"""
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('voted_piece_comments',
                                                      lazy='dynamic',
                                                      order_by='desc(PieceCommentVote.created_at)'))

    piece_comment_id = db.Column(db.Integer, db.ForeignKey('piece_comment.id'))
    piece_comment = db.relationship('PieceComment',
                                    backref=db.backref('votes',
                                                       lazy='dynamic',
                                                       cascade="all, delete, delete-orphan",
                                                       order_by='asc(PieceCommentVote.created_at)'))
