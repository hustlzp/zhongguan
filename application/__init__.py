# coding: utf-8
import sys
import os

# Insert project root path to sys.path
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_path not in sys.path:
    sys.path.insert(0, project_path)

import hashlib
import logging
import time
from flask import Flask, request, url_for, g, render_template
from flask_wtf.csrf import CsrfProtect
from flask.ext.uploads import configure_uploads
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.contrib.fixers import ProxyFix
from .utils.account import get_current_user
from .utils.assets import register_assets
from config import load_config

# convert python's encoding to utf8
reload(sys)
sys.setdefaultencoding('utf8')


def create_app():
    """Create Flask app."""
    app = Flask(__name__)

    config = load_config()
    app.config.from_object(config)

    if not hasattr(app, 'production'):
        app.production = not app.debug and not app.testing

    # Proxy fix
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # CSRF protect
    CsrfProtect(app)

    # Enable Sentry in production mode
    if app.production:
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.ERROR)

        # Enable Sentry
        if app.config.get('SENTRY_DSN'):
            from .utils.sentry import sentry

            sentry.init_app(app, dsn=app.config.get('SENTRY_DSN'))
    else:
        DebugToolbarExtension(app)

        # Serve static files during development
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/uploads': os.path.join(app.config.get('PROJECT_PATH'), 'uploads')
        })

    # Register components
    register_db(app)
    register_routes(app)
    register_jinja(app)
    register_assets(app)
    register_error_handle(app)
    register_uploadsets(app)
    register_hooks(app)

    return app


def register_jinja(app):
    """Register jinja filters, vars, functions."""
    from .utils import filters, permissions, helpers
    from .models import Notification, NOTIFICATION_KIND, PIECE_EDIT_KIND, COLLECTION_EDIT_KIND

    app.jinja_env.filters.update({
        'timesince': filters.timesince,
        'markdown': filters.markdown,
        'date_cn': filters.date_cn,
        'date_number': filters.date_number,
        'weekday_cn': filters.weekday_cn,
        'is_today': filters.is_today
    })

    @app.context_processor
    def inject_vars():
        return dict(
            notifications=g.user.notifications.order_by(Notification.created_at.desc()) if g.user else [],
            notifications_count=g.user.notifications.filter(
                ~Notification.checked).count() if g.user else 0
        )

    def url_for_other_page(page):
        """Generate url for pagination."""
        view_args = request.view_args.copy()
        args = request.args.copy().to_dict()
        combined_args = dict(view_args.items() + args.items())
        combined_args['page'] = page
        return url_for(request.endpoint, **combined_args)

    rules = {}
    for endpoint, _rules in app.url_map._rules_by_endpoint.iteritems():
        if any(item in endpoint for item in ['_debug_toolbar', 'debugtoolbar', 'static']):
            continue
        rules[endpoint] = [{'rule': rule.rule} for rule in _rules]

    app.jinja_env.globals.update({
        'absolute_url_for': helpers.absolute_url_for,
        'url_for_other_page': url_for_other_page,
        'rules': rules,
        'permissions': permissions,
        'NOTIFICATION_KIND': NOTIFICATION_KIND,
        'PIECE_EDIT_KIND': PIECE_EDIT_KIND,
        'COLLECTION_EDIT_KIND': COLLECTION_EDIT_KIND
    })


def register_db(app):
    """Register models."""
    from .models import db

    db.init_app(app)


def register_routes(app):
    """Register routes."""
    from .controllers import site, account, piece, user, collection, feedback, admin, word

    app.register_blueprint(site.bp)
    app.register_blueprint(account.bp)
    app.register_blueprint(piece.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(collection.bp)
    app.register_blueprint(feedback.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(word.bp)


def register_error_handle(app):
    """Register HTTP error pages."""

    @app.errorhandler(403)
    def page_403(error):
        return render_template('site/403.html'), 403

    @app.errorhandler(404)
    def page_404(error):
        return render_template('site/404.html'), 404

    @app.errorhandler(500)
    def page_500(error):
        return render_template('site/500.html'), 500


def register_uploadsets(app):
    """Register UploadSets."""
    from .utils.uploadsets import avatars, collection_covers, qrcodes

    configure_uploads(app, (avatars, collection_covers, qrcodes))


def register_hooks(app):
    """Register hooks."""

    @app.before_request
    def before_request():
        g.user = get_current_user()
        if g.user and g.user.is_admin:
            g._before_request_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(g, '_before_request_time'):
            delta = time.time() - g._before_request_time
            response.headers['X-Render-Time'] = delta * 1000
        return response


def _get_template_name(template_reference):
    """Get current template name."""
    return template_reference._TemplateReference__context.name
