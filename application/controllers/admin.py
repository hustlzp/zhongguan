# coding: utf-8
import datetime
from flask import render_template, Blueprint, redirect, request, url_for
from ..utils.permissions import AdminPermission
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
    return render_template('admin/dashboard.html', today_users_count=today_users_count,
                           today_pieces_count=today_pieces_count)


@bp.route('/admin/users')
@AdminPermission()
def users():
    users = User.query.order_by(User.created_at.desc())
    return render_template('admin/users.html', users=users)


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
