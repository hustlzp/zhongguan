# coding: utf-8
from flask import render_template, Blueprint, redirect, request, url_for, flash, abort, current_app
from ..forms import SigninForm, SignupForm, ResetPasswordForm, ForgotPasswordForm
from ..utils.account import signin_user, signout_user
from ..utils.permissions import VisitorPermission
from ..utils.mail import send_activate_mail, send_reset_password_mail
from ..utils.security import decode
from ..utils.helpers import get_domain_from_email
from ..utils.decorators import jsonify
from ..models import db, User, Piece
from ..utils.geetest import geetest

bp = Blueprint('account', __name__)


@bp.route('/signin', methods=['POST'])
@VisitorPermission()
@jsonify
def do_signin():
    form = SigninForm()
    if form.validate():
        word = request.form.get('word')
        content = request.form.get('content')
        sentence = request.form.get('sentence')

        piece = None
        if word and content:
            piece = Piece.create(word, content, sentence, form.user)

        signin_user(form.user)
        return {'result': True, 'piece_id': piece.id if piece else None}
    else:
        return {'result': False, 'email': _get_first_error(form.email), 'password': _get_first_error(form.password)}


@bp.route('/do_signup', methods=['POST'])
@VisitorPermission()
@jsonify
def do_signup():
    form = SignupForm()
    if form.validate_on_submit():
        captcha_id = current_app.config.get('GEETEST_CAPTCHA_ID')
        private_key = current_app.config.get('GEETEST_PRIVATE_KEY')
        challenge = request.form.get('geetest_challenge')
        validate = request.form.get('geetest_validate')
        seccode = request.form.get('geetest_seccode')
        gt = geetest(captcha_id, private_key)
        if not gt.geetest_validate(challenge, validate, seccode):
            return {'result': False}

        user = User(name=form.name.data, email=form.email.data, password=form.password.data)
        db.session.add(user)

        word = request.form.get('word')
        content = request.form.get('content')
        sentence = request.form.get('sentence')

        piece = None
        if word and content:
            piece = Piece.create(word, content, sentence, user)

        db.session.commit()
        send_activate_mail(user)
        signin_user(user)
        return {'result': True, 'domain': get_domain_from_email(user.email), 'piece_id': piece.id if piece else None}
    else:
        return {'result': False, 'name': _get_first_error(form.name), 'email': _get_first_error(form.email),
                'password': _get_first_error(form.password)}


@bp.route('/activate')
def activate():
    """激活账号"""
    token = request.args.get('token')
    if not token:
        abort(403)

    user_id = decode(token)
    if not user_id:
        abort(403)

    user = User.query.filter(User.id == user_id).first()
    if not user:
        abort(403)

    user.is_active = True
    db.session.add(user)
    db.session.commit()
    signin_user(user)
    flash('账号激活成功，欢迎来到中关村字典。')
    return redirect(url_for('site.pieces'))


@bp.route('/signout')
def signout():
    signout_user()
    return redirect(url_for('site.index'))


@bp.route('/forgot_password', methods=['POST'])
@VisitorPermission()
@jsonify
def forgot_password():
    """忘记密码"""
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter(User.email == form.email.data).first()
        if not user.is_active:
            return {'result': False, 'unactive': True}

        # return {'result': True}
        return {'result': send_reset_password_mail(user)}
    else:
        return {'result': False, 'email': _get_first_error(form.email)}


@bp.route('/reset_password', methods=['POST'])
@VisitorPermission()
@jsonify
def reset_password():
    token = request.form.get('token')
    if not token:
        return {'result': False}

    user_id = decode(token)
    if not user_id:
        return {'result': False}

    user = User.query.filter(User.id == user_id).first()
    if not user or not user.is_active:
        return {'result': False}

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        return {'result': True}
    else:
        return {'result': False, 'password': _get_first_error(form.password)}


def _get_first_error(field):
    """获取field的第一条错误信息"""
    return field.errors[0] if len(field.errors) else ""
