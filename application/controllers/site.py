# coding: utf-8
from datetime import date, timedelta
from flask import render_template, Blueprint, request
from ..models import db, Piece, Collection, CollectionKind

bp = Blueprint('site', __name__)


@bp.route('/')
def index():
    """Index page."""
    pieces_data = []
    pieces_data_count = 0
    start_date = None
    delta = 0

    while pieces_data_count < 5:
        target_day = date.today() - timedelta(days=delta)
        pieces_count = Piece.query.filter(db.func.date(Piece.created_at) == target_day).count()
        if pieces_count:
            pieces_data.append(Piece.get_pieces_data_by_day(target_day))
            pieces_data_count += 1
            start_date = (target_day - timedelta(days=1)).strftime("%Y-%m-%d")
        elif delta == 0:  # 无论如何，把今天的数据加上去（即使是空）
            pieces_data.append(Piece.get_pieces_data_by_day(target_day))
        delta += 1
    return render_template('site/index.html', pieces_data=pieces_data, start_date=start_date)


@bp.route('/about')
def about():
    """About page."""
    return render_template('site/about.html')


@bp.route('/search')
def search():
    return render_template('site/search.html')


@bp.route('/collections', defaults={'page': 1})
@bp.route('/collections/page/<int:page>')
def collections(page):
    kind_id = request.args.get('kind_id')
    current_kind = CollectionKind.query.get_or_404(kind_id) if kind_id else None
    collection_kinds = CollectionKind.query.order_by(CollectionKind.show_order.asc())
    if kind_id:
        collections = current_kind.collections
    else:
        collections = Collection.query
    collections = collections.order_by(Collection.created_at.desc()).paginate(page, 20)
    return render_template('site/collections.html', collections=collections,
                           collection_kinds=collection_kinds, kind_id=kind_id)


@bp.route('/test')
def test():
    from jinja2 import Markup
    from ..utils.helpers import generate_lcs_html

    return Markup(generate_lcs_html('ABCBDAB', 'BDCABA'))
