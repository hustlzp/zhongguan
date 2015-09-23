# coding: utf-8
import string
from datetime import date, timedelta
from flask import render_template, Blueprint, request, redirect, url_for, g, current_app
from ..models import db, Piece, Word
from ..utils.geetest import geetest

bp = Blueprint('site', __name__)


@bp.route('/')
def index():
    if g.user:
        return redirect(url_for('.pieces'))
    piece = Piece.query.order_by(db.func.random()).first()

    base_url = current_app.config.get('GEETEST_BASE_URL')
    captcha_id = current_app.config.get('GEETEST_CAPTCHA_ID')
    private_key = current_app.config.get('GEETEST_PRIVATE_KEY')
    gt = geetest(captcha_id, private_key)
    url = ""
    httpsurl = ""
    product = "float"
    try:
        challenge = gt.geetest_register()
    except Exception as e:
        challenge = ""
    if len(challenge) == 32:
        url = "http://%s%s&challenge=%s&product=%s" % (base_url, captcha_id, challenge, product)
    return render_template('site/index.html', piece=piece, url=url)


@bp.route('/pieces')
def pieces():
    pieces_data = []
    pieces_data_count = 0
    start_date = None
    delta = 0

    while pieces_data_count < 5 and delta < 5:
        target_day = date.today() - timedelta(days=delta)
        pieces_count = Piece.query.filter(db.func.date(Piece.created_at) == target_day).count()
        if pieces_count:
            pieces_data.append(Piece.get_pieces_data_by_day(target_day))
            pieces_data_count += 1
            start_date = (target_day - timedelta(days=1)).strftime("%Y-%m-%d")
        elif delta == 0:  # 无论如何，把今天的数据加上去（即使是空）
            pieces_data.append(Piece.get_pieces_data_by_day(target_day))
        delta += 1

    piece_id = request.args.get('piece_id', type=int)
    piece = None
    if piece_id:
        piece = Piece.query.get(piece_id)

    word_id = request.args.get('word_id', type=int)
    word = None
    if word_id:
        word = Word.query.get(word_id)

    return render_template('site/pieces.html', pieces_data=pieces_data, start_date=start_date, piece=piece, word=word)


@bp.route('/about')
def about():
    """About page."""
    return render_template('site/about.html')


@bp.route('/search')
def search():
    return render_template('site/search.html')


@bp.route('/collections')
def collections():
    """浏览字典"""
    first_letter = request.args.get('first_letter')
    words = Word.query
    if first_letter:
        words = words.filter(Word.first_letter == first_letter)

    letters = []
    for letter in string.ascii_lowercase:
        if Word.query.filter(Word.first_letter == letter).count() > 0:
            letters.append(letter)

    return render_template('site/collections.html', words=words, letters=letters, first_letter=first_letter)


@bp.route('/test')
def test():
    from jinja2 import Markup
    from ..utils.helpers import generate_lcs_html

    return Markup(generate_lcs_html('ABCBDAB', 'BDCABA'))
