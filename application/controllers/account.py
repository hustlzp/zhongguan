# coding: utf-8
from flask import render_template, Blueprint, redirect, request, url_for, flash
from ..forms import SigninForm, SignupForm, ResetPasswordForm, ForgotPasswordForm
from ..utils.account import signin_user, signout_user
from ..utils.permissions import VisitorPermission
from ..utils.mail import send_activate_mail, send_reset_password_mail
from ..utils.security import decode
from ..utils.helpers import get_domain_from_email
from ..models import db, User, InvitationCode

bp = Blueprint('account', __name__)


@bp.route('/signin', methods=['GET', 'POST'])
@VisitorPermission()
def signin():
    """Signin"""
    form = SigninForm()
    referer = request.form.get('referer')
    if form.validate_on_submit():
        signin_user(form.user)
        return redirect(referer or url_for('site.index'))
    return render_template('account/signin.html', form=form)


@bp.route('/signup', methods=['GET', 'POST'])
@VisitorPermission()
def signup():
    """Signup"""
    form = SignupForm()
    code_string = request.args.get('code')
    if code_string:
        form.code.data = code_string
        code = InvitationCode.query.filter(InvitationCode.code == code_string).first()
        if code and code.email:
            form.email.data = code.email

    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()

        code = InvitationCode.query.filter(InvitationCode.code == form.code.data).first_or_404()
        code.used = True
        code.user_id = user.id
        db.session.add(code)
        db.session.commit()

        # 若用户填写的邮箱和code中的邮箱相同，则无需填写
        if user.email == code.email:
            user.is_active = True
            db.session.add(user)
            db.session.commit()
            signin_user(user)
            flash('注册成功，欢迎来到中关村字典。')
            return redirect(url_for('site.index'))
        else:
            send_activate_mail(user)
            email_domain = get_domain_from_email(user.email)
            if email_domain:
                message = "请 <a href='%s' target='_blank'>登录邮箱</a> 激活账号" % email_domain
            else:
                message = "请登录邮箱激活账号"
            return render_template('site/message.html', title='注册成功', message=message)
    return render_template('account/signup.html', form=form)


@bp.route('/activate')
def activate():
    """激活账号"""
    token = request.args.get('token')
    if not token:
        return render_template('site/message.html', title="账号激活失败", message='无效的激活链接')

    user_id = decode(token)
    if not user_id:
        return render_template('site/message.html', title="账号激活失败", message='无效的激活链接')

    user = User.query.filter(User.id == user_id).first()
    if not user:
        return render_template('site/message.html', title="账号激活失败", message='无效的账号')

    user.is_active = True
    db.session.add(user)
    db.session.commit()
    signin_user(user)
    flash('账号激活成功，欢迎来到中关村字典。')
    return redirect(url_for('site.index'))


@bp.route('/signout')
def signout():
    """Signout"""
    signout_user()
    return redirect(request.referrer or url_for('site.index'))


@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """忘记密码"""
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter(User.email == form.email.data).first()

        if not user.is_active:
            return render_template('site/message.html', title="提示", message='请先完成账号激活')
        send_reset_password_mail(user)

        email_domain = get_domain_from_email(user.email)
        if email_domain:
            message = "请 <a href='%s' target='_blank'>登录邮箱</a> 完成密码重置" % email_domain
        else:
            message = "请登录邮箱完成密码重置"
        return render_template('site/message.html',
                               title="发送成功",
                               message=message)
    return render_template('account/forgot_password.html', form=form)


@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    token = request.args.get('token')
    if not token:
        return render_template('site/message.html', title="密码重置失败", message='无效的密码重置链接')

    user_id = decode(token)
    if not user_id:
        return render_template('site/message.html', title="密码重置失败", message='无效的密码重置链接')

    user = User.query.filter(User.id == user_id).first()
    if not user or not user.is_active:
        return render_template('site/message.html', title="密码重置失败", message='无效的用户')

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.new_password.data
        db.session.add(user)
        db.session.commit()
        flash('密码重置成功，请使用新密码登录账户')
        return redirect(url_for('.signin'))
    return render_template('account/reset_password.html', form=form)
