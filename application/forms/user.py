# coding: utf-8
from flask import g
from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import Optional, URL, DataRequired, EqualTo




class ChangePasswordForm(Form):
    password = PasswordField('当前密码',
                             validators=[DataRequired('当前密码不能为空')])

    new_password = PasswordField('新密码',
                                 validators=[DataRequired('新密码不能为空')])

    def validate_password(self, field):
        if not g.user or not g.user.check_password(self.password.data):
            raise ValueError('密码错误')
