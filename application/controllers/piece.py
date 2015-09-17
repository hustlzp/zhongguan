# coding: utf-8
from datetime import timedelta, date, datetime
from flask import render_template, Blueprint, redirect, request, url_for, g, \
    get_template_attribute, json, abort
from ..utils.permissions import UserPermission, PieceAddPermission, PieceEditPermission
from ..utils.helpers import generate_lcs_html
from ..models import db, User, Piece, PieceVote, PieceComment, CollectionPiece, Collection, \
    PieceSource, PieceAuthor, PIECE_EDIT_KIND, PieceEditLog, PieceCommentVote, Notification, \
    NOTIFICATION_KIND, PieceEditLogReport, CollectionEditLog, COLLECTION_EDIT_KIND, Word, Voter
from ..forms import PieceForm, EditPieceForm
from ..utils.decorators import jsonify

bp = Blueprint('piece', __name__)


@bp.route('/piece/<int:uid>')
def view(uid):
    """Single piece page"""
    piece = Piece.query.get_or_404(uid)
    piece.clicks_count += 1
    db.session.add(piece)
    db.session.commit()
    return render_template("piece/view.html", piece=piece)


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
        word = Word.get_word(form.word.data)

        piece = Piece(content=form.content.data, sentence=form.sentence.data, word_id=word.id, user_id=g.user.id)
        db.session.add(piece)
        db.session.commit()

        # 自动vote
        # vote = PieceVote(piece_id=piece.id, user_id=g.user.id)
        # db.session.add(vote)
        # g.user.votes_count += 1
        # piece.votes_count += 1

        # log
        log = PieceEditLog(piece_id=piece.id, user_id=g.user.id, kind=PIECE_EDIT_KIND.CREATE)
        db.session.add(log)

        # Generate QRCode
        piece.make_qrcode()
        db.session.add(piece)

        # # 如果存在title为author的句集，则自动将piece加入到此句集
        # author_collection = Collection.get_by_title(piece.author)
        # if author_collection:
        #     author_collection_piece = CollectionPiece(collection_id=author_collection.id)
        #     piece.collections.append(author_collection_piece)
        #
        # # 如果存在title为source的句集，则自动将piece加入到此句集
        # source_collection = Collection.get_by_title(piece.source)
        # if source_collection:
        #     source_collection_piece = CollectionPiece(collection_id=source_collection.id)
        #     piece.collections.append(source_collection_piece)

        g.user.pieces_count += 1
        db.session.add(g.user)

        Word.add_word(form.word.data)

        db.session.commit()
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
        return redirect(url_for('site.index', piece_id=piece.id))
    return render_template('piece/edit.html', piece=piece, form=form)


@bp.route('/piece/<int:uid>/vote', methods=['POST'])
@UserPermission()
@jsonify
def vote(uid):
    piece = Piece.query.get_or_404(uid)
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

        db.session.commit()
        return {'result': True}
    else:
        return {'result': False}


@bp.route('/piece/<int:uid>/unvote', methods=['POST'])
@UserPermission()
@jsonify
def unvote(uid):
    piece = Piece.query.get_or_404(uid)
    vote = g.user.voted_pieces.filter(PieceVote.piece_id == uid).first()
    if not vote:
        return json.dumps({'result': False})
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

    if root_comment_id:
        noti_receiver_id = target_user_id
        noti_kind = NOTIFICATION_KIND.COMMENT_PIECE_COMMENT
    else:
        noti_receiver_id = piece.user_id
        noti_kind = NOTIFICATION_KIND.COMMENT_PIECE

    # 推送通知
    if noti_receiver_id != g.user.id:
        noti = Notification(sender_id=g.user.id, target=piece.content, content=content,
                            receiver_id=noti_receiver_id, kind=noti_kind,
                            link="%s#comment_%d" % (url_for('piece.view', uid=uid), comment.id))
        db.session.add(noti)
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


@bp.route('/piece/<int:uid>/add_to_collection', methods=['POST'])
@UserPermission()
def add_to_collection(uid):
    piece = Piece.query.get_or_404(uid)
    title = request.form.get('title')
    collection_id = request.form.get('collection_id')

    collection = None
    if title:
        collection = Collection.get_by_title(title, create_if_not_exist=True)
    elif collection_id:
        collection = Collection.query.get_or_404(collection_id)

    if not collection:
        abort(404)

    # 若该句集尚未收录此句子，则收录
    collection_piece = CollectionPiece.query.filter(
        CollectionPiece.collection_id == collection.id,
        CollectionPiece.piece_id == uid).first()
    if not collection_piece:
        collection_piece = CollectionPiece(collection_id=collection.id, piece_id=uid)
        # log
        log = PieceEditLog(piece_id=uid, user_id=g.user.id,
                           after=collection.title, after_id=collection.id,
                           kind=PIECE_EDIT_KIND.ADD_TO_COLLECTION)
        db.session.add(collection_piece)
        db.session.add(log)
        db.session.commit()
    macro = get_template_attribute('macros/_collection.html', 'render_collection_tag_wap')
    return json.dumps({'result': True,
                       'id': collection.id,
                       'html': macro(collection)})


@bp.route('/piece/<int:uid>/remove_from_collection/<int:collection_id>', methods=['POST'])
@UserPermission()
def remove_from_collection(uid, collection_id):
    """将某句子从某句集中移除"""
    piece = Piece.query.get_or_404(uid)
    collection = Collection.query.get_or_404(collection_id)
    collection_pieces = CollectionPiece.query.filter(
        CollectionPiece.collection_id == collection_id,
        CollectionPiece.piece_id == uid)
    for collection_piece in collection_pieces:
        db.session.delete(collection_piece)
        # log
        log = PieceEditLog(piece_id=uid, user_id=g.user.id,
                           before=collection.title, before_id=collection_id,
                           kind=PIECE_EDIT_KIND.REMOVE_FROM_COLLECTION)
        db.session.add(log)
    db.session.commit()
    return json.dumps({'result': True})


@bp.route('/piece/meet')
def meet():
    return render_template('piece/meet.html')


@bp.route('/piece/random', methods=['POST'])
def random():
    collection_id = request.form.get('collection_id', type=int)
    if collection_id:
        collection = Collection.query.get_or_404(collection_id)
        if collection.pieces.count() == 0:
            abort(404)
        collection_piece = collection.pieces.order_by(db.func.random()).first()
        piece = collection_piece.piece
    else:
        piece = Piece.query.order_by(db.func.random()).first_or_404()

    return json.dumps({
        'id': piece.id,
        'content': piece.content,
        'content_length': piece.content_length,
        'source': piece.source_string
    })


@bp.route('/piece/log/<int:uid>/report', methods=['POST'])
@UserPermission()
def report_log(uid):
    """举报恶意编辑"""
    log = PieceEditLog.query.get_or_404(uid)
    report = log.reports.filter(PieceEditLog.user_id == g.user.id).first()
    if not report:
        report = PieceEditLogReport(log_id=uid, user_id=g.user.id)
        db.session.add(report)
        db.session.commit()
    return json.dumps({'result': True})


@bp.route('/piece/query_author', methods=['POST'])
@UserPermission()
def query_author():
    q = request.form.get('q')
    if q:
        authors = PieceAuthor.query.filter(PieceAuthor.name.like("%%%s%%" % q))
        return json.dumps([{'value': author.name} for author in authors])
    else:
        return json.dumps({})


@bp.route('/piece/query_source', methods=['POST'])
@UserPermission()
def query_source():
    q = request.form.get('q')
    if q:
        sources = PieceSource.query.filter(PieceSource.name.like("%%%s%%" % q))
        return json.dumps([{'value': source.name} for source in sources])
    else:
        return json.dumps({})


def _save_piece_source(source):
    """存储Piece来源，若存在，则count加1"""
    piece_source = PieceSource.query.filter(PieceSource.name == source).first()
    if piece_source:
        piece_source.count += 1
    else:
        piece_source = PieceSource(name=source)
        db.session.add(piece_source)
        db.session.commit()
    return piece_source.id


def _save_piece_author(author):
    """存储Piece原作者，若存在，则count加1"""
    piece_author = PieceAuthor.query.filter(PieceAuthor.name == author).first()
    if piece_author:
        piece_author.count += 1
    else:
        piece_author = PieceAuthor(name=author)
        db.session.add(piece_author)
        db.session.commit()
    return piece_author.id
