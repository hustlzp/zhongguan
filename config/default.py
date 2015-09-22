# coding: utf-8
import os


class Config(object):
    """配置基类"""
    # Flask app config
    DEBUG = False
    TESTING = False
    SECRET_KEY = "\xb5\xb3}#\xb7A\xcac\x9d0\xb6\x0f\x80z\x97\x00\x1e\xc0\xb8+\xe9)\xf0}"
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 7
    SESSION_COOKIE_NAME = '1jingdian_session'

    # Root path of project
    PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Site domain
    SITE_TITLE = "1jingdian"
    SITE_DOMAIN = "http://localhost:5000"

    # SQLAlchemy config
    # See:
    # https://pythonhosted.org/Flask-SQLAlchemy/config.html#connection-uri-format
    # http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html#database-urls
    SQLALCHEMY_DATABASE_URI = "mysql://user:password@host/database"

    # Uploadsets config
    UPLOADS_DEFAULT_DEST = "%s/uploads" % PROJECT_PATH  # 上传文件存储路径
    UPLOADS_DEFAULT_URL = "%s/uploads/" % SITE_DOMAIN  # 上传文件访问URL

    # Flask-DebugToolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # Sentry config
    SENTRY_DSN = ''

    # SendCloud config
    SC_FROM = ''
    SC_API_USER = ''
    SC_API_KEY = ''

    # Geetest
    GEETEST_BASE_URL = "api.geetest.com/get.php?gt="
    GEETEST_CAPTCHA_id = ""
    GEETEST_PRIVATE_KEY = ""

    # Host string, used by fabric
    HOST_STRING = ""
