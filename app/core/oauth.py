from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from app.core.config import settings

config = Config()

oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',

    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',

    client_kwargs={
        'scope': 'openid email profile'
    }
)

oauth.register(
    name='github',
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,

        # У GitHub нет server_metadata_url, поэтому прописываем пути вручную:
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    api_base_url='https://api.github.com/',

    client_kwargs={
        'scope': 'user:email read:user',  # Запрашиваем доступ к почте и профилю
    }
)