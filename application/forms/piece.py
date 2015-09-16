# coding: utf-8
import re
import math
from flask_wtf import Form
from wtforms import StringField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, URL, Optional
from ._helper import check_url, trim, remove_book_tilte_mark
from ..models import Piece


class PieceForm(Form):
    word = StringField('词', validators=[DataRequired('词不能为空'), trim])
    content = TextAreaField('解释', validators=[DataRequired('解释不能为空'), trim])
    sentence = TextAreaField('例句', validators=[Optional(), trim], description='选填')

    # def validate_content(self, field):
    #     content = self.content.data
    #     content = content.strip()  # 去除首尾的空格
    #     content = re.sub('\r\n', '', content)  # 去掉换行符
    #     content = re.sub('\s+', ' ', content)  # 将多个空格替换为单个空格
    #     self.content.data = content
    #
    #     content_length = Piece.calculate_content_length(self.content.data)
    #     if content_length > 200:
    #         raise ValueError('不超过200字')


class EditPieceForm(Form):
    content = TextAreaField('解释', validators=[DataRequired('解释不能为空'), trim])
    sentence = TextAreaField('例句', validators=[Optional(), trim], description='选填')


class PieceCommentForm(Form):
    content = TextAreaField('评论',
                            validators=[DataRequired('评论内容不能为空')],
                            description='评论内容')
