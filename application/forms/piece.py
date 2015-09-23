# coding: utf-8
from flask_wtf import Form
from wtforms import StringField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, URL, Optional
from ._helper import check_url, trim


class PieceForm(Form):
    word = StringField('词', validators=[DataRequired('词不能为空'), trim])
    content = TextAreaField('解释', validators=[DataRequired('解释不能为空'), trim])
    sentence = TextAreaField('例句', validators=[Optional(), trim], description='选填')


class EditPieceForm(Form):
    content = TextAreaField('解释', validators=[DataRequired('解释不能为空'), trim])
    sentence = TextAreaField('例句', validators=[Optional(), trim], description='选填')


class PieceCommentForm(Form):
    content = TextAreaField('评论',
                            validators=[DataRequired('评论内容不能为空')],
                            description='评论内容')
