import os

from yarl import URL

AUTH0_URL = URL(os.environ['AUTH0_URL'])
AUTH0_CLIENT_ID = os.environ['CLIENT_ID']
AUTH0_APPLICATION_ID = os.environ.get('AUTH0_APPLICATION_ID', 'default')
AUTH0_TOKEN_URL_PATH = os.environ.get(
    'TOKEN_URL_PATH', f'/oauth2/{AUTH0_APPLICATION_ID}/v1/token'
)
AUTH0_USER_DATA_URL_PATH = os.environ.get(
    'USER_DATA_URL_PATH', f'/oauth2/{AUTH0_APPLICATION_ID}/v1/userinfo'
)
AUTH0_CALLBACK_PATH = os.environ.get('AUTH0_CALLBACK', 'auth/login_callback')
AUTH0_REVOCATION_PATH = '/oauth2/v1/revoke'

LOGOUT_REDIRECT_PATH = os.environ.get('LOGOUT_REDIRECT_PATH', '/')
REDIRECT_EXTRA_PATH = os.environ.get('REDIRECT_EXTRA_PATH')
SUCCESS_LOGIN_REDIRECT_PATH = os.environ.get('SUCCESS_LOGIN_REDIRECT_PATH', '')
SESSION_RECORD_LIFETIME = int(os.environ.get('SESSION_RECORD_LIFETIME', 3600 * 24 * 7))
