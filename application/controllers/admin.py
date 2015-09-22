# coding: utf-8
import datetime
from werkzeug.security import gen_salt
from flask import render_template, Blueprint, redirect, request, url_for, flash, g
from ..utils.permissions import AdminPermission
from ..utils.mail import send_invitation_mail
from ..forms import SendInvitationCodeForm
from ..models import db, Feedback, User, Piece

bp = Blueprint('admin', __name__)


@bp.route('/admin/dashboard')
@AdminPermission()
def dashboard():
    today = datetime.date.today()
    today_users_count = User.query.filter(
        db.func.date(User.created_at) == today).count()
    today_pieces_count = Piece.query.filter(
        db.func.date(Piece.created_at) == today).count()
    today_collections_count = Collection.query.filter(
        db.func.date(Collection.created_at) == today).count()
    return render_template('admin/dashboard.html', today_users_count=today_users_count,
                           today_pieces_count=today_pieces_count,
                           today_collections_count=today_collections_count)


@bp.route('/admin/users')
@AdminPermission()
def users():
    users = User.query.order_by(User.created_at.desc())
    return render_template('admin/users.html', users=users)


@bp.route('/admin/report_piece_logs', methods=['GET', 'POST'])
@AdminPermission()
def piece_log_reports():
    """管理句子恶意编辑举报"""
    reports = PieceEditLogReport.query
    return render_template('admin/piece_log_reports.html', reports=reports)


@bp.route('/admin/piece_log_report/<int:uid>/process')
@AdminPermission()
def process_piece_log_report(uid):
    """处理句子恶意编辑举报"""
    report = PieceEditLogReport.query.get_or_404(uid)
    report.processed = True
    db.session.add(report)
    db.session.commit()
    return redirect(request.referrer or url_for('.piece_log_reports'))


@bp.route('/admin/report_collection_logs', methods=['GET', 'POST'])
@AdminPermission()
def collection_log_reports():
    """管理句集恶意编辑举报"""
    reports = CollectionEditLogReport.query
    return render_template('admin/collection_log_reports.html', reports=reports)


@bp.route('/admin/collection_log_report/<int:uid>/process')
@AdminPermission()
def process_collection_log_report(uid):
    """处理句集恶意编辑举报"""
    report = CollectionEditLogReport.query.get_or_404(uid)
    report.processed = True
    db.session.add(report)
    db.session.commit()
    return redirect(request.referrer or url_for('.collection_log_reports'))


@bp.route('/admin/feedback', methods=['GET', 'POST'])
@AdminPermission()
def feedback():
    """管理意见反馈"""
    feedbacks = Feedback.query
    return render_template('admin/feedback.html', feedbacks=feedbacks)


@bp.route('/admin/feedback/<int:uid>/process')
@AdminPermission()
def process_feedback(uid):
    """处理这一条意见反馈"""
    feedback = Feedback.query.get_or_404(uid)
    feedback.processed = True
    db.session.add(feedback)
    db.session.commit()
    return redirect(request.referrer or url_for('.feedback'))


@bp.route('/invitation', defaults={'page': 1}, methods=['GET', 'POST'])
@bp.route('/invitation/page/<int:page>', methods=['GET', 'POST'])
@AdminPermission()
def invitation(page):
    """注册码管理"""
    codes = InvitationCode.query.order_by(InvitationCode.created_at.desc()).paginate(page, 15)
    return render_template('admin/invitation.html', codes=codes)


@bp.route('/generate_invitation_codes')
@AdminPermission()
def generate_invitation_codes():
    """生成注册码"""
    for i in xrange(0, 10):
        code = InvitationCode(code=gen_salt(16))
        db.session.add(code)
    db.session.commit()
    return redirect(request.referrer)


@bp.route('/invitation_code/<int:uid>/send', methods=['GET', 'POST'])
@AdminPermission()
def send_invitation_code(uid):
    """向用户邮箱发送邀请码"""
    invitation_code = InvitationCode.query.get_or_404(uid)
    if invitation_code.email or invitation_code.used:
        flash('该邀请码无法使用')
        return redirect(url_for('.invitation'))

    form = SendInvitationCodeForm(code=invitation_code.code)
    if form.validate_on_submit():
        if send_invitation_mail(form.email.data, invitation_code.code):
            invitation_code.email = form.email.data
            invitation_code.sended_at = datetime.datetime.now()
            invitation_code.sender_id = g.user.id
            db.session.add(invitation_code)
            db.session.commit()
            flash('发送成功')
        else:
            flash('发送失败')
        return redirect(url_for('.invitation'))
    return render_template('admin/send_invitation_code.html', form=form,
                           invitation_code=invitation_code)
