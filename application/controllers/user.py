# coding: utf-8
from datetime import datetime
from flask import render_template, Blueprint, redirect, request, url_for, flash, g, json, abort
from ..utils.permissions import UserPermission
from ..utils.uploadsets import avatars, process_avatar
from ..models import db, User, Notification
from ..utils.decorators import jsonify

bp = Blueprint('user', __name__)


@bp.route('/people/<int:uid>', defaults={'page': 1})
@bp.route('/people/<int:uid>/page/<int:page>')
def profile(uid, page):
    user = User.query.get_or_404(uid)
    votes = user.voted_pieces.paginate(page, 20)
    return render_template('user/profile.html', user=user, votes=votes)


@bp.route('/people/<int:uid>/shares', defaults={'page': 1})
@bp.route('/people/<int:uid>/shares/page/<int:page>')
def shares(uid, page):
    user = User.query.get_or_404(uid)
    pieces = user.pieces.paginate(page, 20)
    return render_template('user/shares.html', user=user, pieces=pieces)


@bp.route('/people/<int:uid>/voters', defaults={'page': 1})
@bp.route('/people/<int:uid>/voters/page/<int:page>')
def voters(uid, page):
    user = User.query.get_or_404(uid)
    return render_template('user/voters.html', user=user)


# @bp.route('/people/<int:uid>/likes', defaults={'page': 1})
# @bp.route('/people/<int:uid>/likes/page/<int:page>')
# def likes(uid, page):
#     user = User.query.get_or_404(uid)
#     collections = user.liked_collections.paginate(page, 20)
#     return render_template('user/collections.html', user=user, collections=collections)


@bp.route('/my/settings')
@UserPermission()
def settings():
    """个人设置"""
    return render_template('user/settings.html')


@bp.route('/my/toggle_setting', methods=['POST'])
@UserPermission()
@jsonify
def toggle_setting():
    """切换设置"""
    key = request.args.get('key')
    if not key or not hasattr(g.user, key):
        abort(404)

    setattr(g.user, key, not getattr(g.user, key))
    db.session.add(g.user)
    db.session.commit()

    return {
        'result': True,
        'setting_result': getattr(g.user, key)
    }


@bp.route('/my/update_name', methods=['POST'])
@UserPermission()
@jsonify
def update_name():
    """更新描述"""
    name = request.form.get('name')
    g.user.name = name
    db.session.add(g.user)
    db.session.commit()
    return {'result': True}


@bp.route('/my/update_motto', methods=['POST'])
@UserPermission()
@jsonify
def update_motto():
    """更新描述"""
    motto = request.form.get('motto')
    g.user.motto = motto
    db.session.add(g.user)
    db.session.commit()
    return {'result': True}


@bp.route('/my/upload_avatar', methods=['POST'])
@UserPermission()
@jsonify
def upload_avatar():
    try:
        filename, (w, h) = process_avatar(request.files['file'], avatars)
    except Exception, e:
        return json.dumps({'result': False, 'error': e.__repr__()})
    else:
        g.user.avatar = filename
        db.session.add(g.user)
        db.session.commit()
        return {'result': True, 'url': avatars.url(filename)}


@bp.route('/my/notifications', defaults={'page': 1})
@bp.route('/my/notifications/page/<int:page>')
@UserPermission()
def notifications(page):
    notifications = g.user.notifications.paginate(page, 15)
    return render_template('user/notifications.html', notifications=notifications)


@bp.route('/my/notifications/check', methods=['POST'])
@UserPermission()
@jsonify
def check_all_notifications():
    notifications = g.user.notifications.filter(~Notification.checked)
    for notification in notifications:
        notification.checked = True
        notification.checked_at = datetime.now()
        db.session.add(notification)
    db.session.commit()
    return {'result': True}
