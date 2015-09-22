# coding: utf-8
from datetime import timedelta, date, datetime
from flask import render_template, Blueprint, redirect, request, url_for, g, \
    get_template_attribute, json, abort
from ..utils.permissions import UserPermission, PieceAddPermission, PieceEditPermission
from ..utils.helpers import generate_lcs_html
from ..models import db, User, Piece, PieceVote, PieceComment, PieceCommentVote, Notification, \
    NOTIFICATION_KIND, Word, Voter
from ..forms import PieceForm, EditPieceForm
from ..utils.decorators import jsonify

bp = Blueprint('piece', __name__)


@bp.route('/piece/<int:uid>/h5')
def h5(uid):
    piece = Piece.query.get_or_404(uid)
    piece.clicks_count += 1
    db.session.add(piece)
    db.session.commit()
    return render_template("piece/h5.html", piece=piece)


@bp.route('/pieces/json', methods=['POST'])
def pieces_by_date():
    """获取从指定date开始的指定天数的pieces"""
    start = request.form.get('start')
    if start:
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
    else:
        start_date = date.today() - timedelta(days=2)

    days = request.form.get('days', 2, type=int)
    html = ""
    pieces_wap_macro = get_template_attribute('macros/_piece.html', 'render_pieces_by_date')

    data_count = 0
    delta = 1
    next_start_date = None

    while data_count < days:
        target_day = start_date - timedelta(days=delta)
        pieces_count = Piece.query.filter(db.func.date(Piece.created_at) == target_day).count()
        if pieces_count:
            pieces_data = Piece.get_pieces_data_by_day(target_day)
            html += pieces_wap_macro(pieces_data, show_modal=False)
            next_start_date = (target_day - timedelta(days=1)).strftime("%Y-%m-%d")
            data_count += 1
        delta += 1
    return json.dumps({
        'html': html,
        'start': next_start_date
    })


@bp.route('/piece/<int:uid>/click', methods=['POST'])
def click(uid):
    piece = Piece.query.get_or_404(uid)
    piece.clicks_count += 1
    db.session.add(piece)
    db.session.commit()
    return json.dumps({'result': True})


@bp.route('/piece/<int:uid>/modal')
def modal(uid):
    piece = Piece.query.get_or_404(uid)
    piece.clicks_count += 1
    db.session.add(piece)
    db.session.commit()
    modal = get_template_attribute('macros/_piece.html', 'render_piece_details_wap')
    return modal(piece)


@bp.route('/piece/add', methods=['GET', 'POST'])
@UserPermission()
@jsonify
def add():
    form = PieceForm()
    if form.validate_on_submit():
        piece = Piece.create(form.word.data, form.content.data, form.sentence.data, g.user)
        return {'result': True, 'piece_id': piece.id}
    else:
        return {'result': False}


@bp.route('/piece/<int:uid>/remove', methods=['POST'])
@UserPermission()
@jsonify
def remove(uid):
    piece = Piece.query.get_or_404(uid)
    if g.user.id != piece.user_id:
        abort(403)
    db.session.delete(piece)
    db.session.commit()
    return {'result': True}


@bp.route('/piece/<int:uid>/edit', methods=['GET', 'POST'])
@UserPermission()
def edit(uid):
    piece = Piece.query.get_or_404(uid)
    if g.user.id != piece.user_id:
        abort(403)

    form = EditPieceForm(obj=piece)
    if form.validate_on_submit():
        form.populate_obj(piece)
        db.session.add(piece)
        db.session.commit()
        return redirect(url_for('site.pieces', piece_id=piece.id))
    return render_template('piece/edit.html', piece=piece, form=form)


@bp.route('/piece/<int:uid>/vote', methods=['POST'])
@UserPermission()
@jsonify
def vote(uid):
    piece = Piece.query.get_or_404(uid)
    if g.user.id == piece.user_id:
        return {'result': False}

    vote = g.user.voted_pieces.filter(PieceVote.piece_id == uid).first()

    if not vote:
        vote = PieceVote(piece_id=uid)
        g.user.voted_pieces.append(vote)
        g.user.votes_count += 1
        piece.votes_count += 1
        db.session.add(g.user)
        db.session.add(piece)

        # Update voter
        voter = Voter.query.filter(Voter.voter_id == g.user.id, Voter.user_id == piece.user_id).first()
        if not voter:
            voter = Voter(voter_id=g.user.id, user_id=piece.user_id)
        else:
            voter.count += 1
        db.session.add(voter)

        piece.user.update_voters_count()
        db.session.add(piece.user)

        Notification.upvote_piece(g.user, piece)

        db.session.commit()
        return {'result': True}
    else:
        return {'result': False}


@bp.route('/piece/<int:uid>/unvote', methods=['POST'])
@UserPermission()
@jsonify
def unvote(uid):
    piece = Piece.query.get_or_404(uid)
    if g.user.id == piece.user_id:
        return {'result': False}

    vote = g.user.voted_pieces.filter(PieceVote.piece_id == uid).first()
    if not vote:
        return {'result': False}
    else:
        db.session.delete(vote)
        if g.user.votes_count > 0:
            g.user.votes_count -= 1
        if piece.votes_count > 0:
            piece.votes_count -= 1
        db.session.add(g.user)
        db.session.add(piece)

        # Update voter
        voter = Voter.query.filter(Voter.voter_id == g.user.id, Voter.user_id == piece.user_id).first()
        if voter:
            voter.count -= 1
            if voter.count < 0:
                voter.count = 0
            db.session.add(voter)

            piece.user.update_voters_count()
            db.session.add(piece.user)

        db.session.commit()
        return {'result': True}


@bp.route('/piece/<int:uid>/comment', methods=['POST'])
@UserPermission()
def comment(uid):
    """评论"""
    piece = Piece.query.get_or_404(uid)
    content = request.form.get('comment')
    root_comment_id = request.form.get('root_comment_id', type=int)
    target_user_id = request.form.get('target_user_id', type=int)

    if not content:
        abort(500)

    comment = PieceComment(content=content.strip(), piece_id=uid, user_id=g.user.id)
    if root_comment_id:  # 若该评论为sub comment
        root_comment = PieceComment.query.get_or_404(root_comment_id)
        target_user = User.query.get_or_404(target_user_id)
        comment.root_comment_id = root_comment_id
        comment.target_user_id = target_user_id
    db.session.add(comment)
    db.session.commit()

    # 通知
    if root_comment_id:
        Notification.comment_piece_comment(g.user, comment)
    else:
        Notification.comment_piece(g.user, comment)
    db.session.commit()

    # 返回comment HTML
    comment_macro = get_template_attribute('macros/_piece.html', 'render_piece_comment')
    sub_comments_macro = get_template_attribute('macros/_piece.html', 'render_piece_sub_comments')
    comment_html = comment_macro(comment)
    # 若为root comment，则在返回的HTML中加入sub_comments
    if not root_comment_id:
        comment_html += sub_comments_macro(comment)
    return comment_html


@bp.route('/piece/comment/<int:uid>/vote', methods=['POST'])
@UserPermission()
def vote_comment(uid):
    """顶评论"""
    comment = PieceComment.query.get_or_404(uid)
    vote = comment.votes.filter(PieceCommentVote.user_id == g.user.id).first()
    if not vote:
        vote = PieceCommentVote(user_id=g.user.id, piece_comment_id=uid)
        db.session.add(vote)
        db.session.commit()
    return json.dumps({'result': True})


@bp.route('/piece/comment/<int:uid>/unvote', methods=['POST'])
@UserPermission()
def unvote_comment(uid):
    """取消顶评论"""
    comment = PieceComment.query.get_or_404(uid)
    votes = comment.votes.filter(PieceCommentVote.user_id == g.user.id)
    for vote in votes:
        db.session.delete(vote)
    db.session.commit()
    return json.dumps({'result': True})
