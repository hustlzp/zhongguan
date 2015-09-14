# coding: utf-8
from flask import Blueprint, render_template, request
from ..models import Word
from ..utils.decorators import jsonify
from ..utils.permissions import UserPermission

bp = Blueprint('word', __name__)


@bp.route('/word/query', methods=['POST'])
@UserPermission()
@jsonify
def query():
    """查询词"""
    q = request.form.get('q')
    if q:
        words = Word.query.filter(Word.word.like("%%%s%%" % q))
        return [{'value': word.word, 'id': word.id} for word in words]
    else:
        return {}
