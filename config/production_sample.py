# coding: utf-8
from .default import Config


class ProductionConfig(Config):
    # App config
    SECRET_KEY = "\xb5\xb3}#\xb7A\xcac\x9d0\xb6\x0f\x80z\x97\x00\x1e\xc0\xb8+\xe9)\xf0}"
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 7
    SESSION_COOKIE_NAME = '1jingdian_session'

    # Site domain
    SITE_DOMAIN = "http://www.1jingdian.com"

    # Db config
    SQLALCHEMY_DATABASE_URI = "mysql://root:password@host/1jingdian"

    # Upload set config
    UPLOADS_DEFAULT_URL = "%s/uploads/" % SITE_DOMAIN

    # Sentry
    SENTRY_DSN = ''

    # SendCloud config
    SC_FROM = ''
    SC_API_USER = ''
    SC_API_KEY = ''

    # Geetest
    GEETEST_BASE_URL = "api.geetest.com/get.php?gt="
    GEETEST_CAPTCHA_id = ""
    GEETEST_PRIVATE_KEY = ""
