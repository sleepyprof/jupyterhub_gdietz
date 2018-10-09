import os
import urllib

from tornado import gen

from oauthenticator.generic import GenericEnvMixin, GenericLoginHandler, GenericOAuthenticator

from tornado.httpclient import HTTPRequest, AsyncHTTPClient

from jupyterhub.handlers.login import LogoutHandler

from jupyterhub.utils import url_path_join

from traitlets import Unicode


class OAuth2WithLogoutMixin(GenericEnvMixin):
    _OAUTH_SINGLE_LOGOUT_URL = os.environ.get('OAUTH2_SINGLE_LOGOUT_URL', '')


class OAuthenticatorWithLogoutLoginHandler(GenericLoginHandler, OAuth2WithLogoutMixin):
    pass


class OAuthenticatorWithLogoutLogoutHandler(LogoutHandler):
    def get(self):
        user = self.current_user
        if user:
            self.log.info("User logged out: %s", user.name)
            self.authenticator.single_logout(user)
            self.clear_login_cookie()
            self.statsd.incr('logout')
        self.redirect(self.settings['login_url'], permanent=False)


class OAuthenticatorWithLogout(GenericOAuthenticator):
    
    single_logout_url = Unicode(
        os.environ.get('OAUTH2_SINGLE_LOGOUT_URL', ''),
        config=True,
        help="Single logout endpoint URL"
    )

    login_handler = OAuthenticatorWithLogoutLoginHandler
    logout_handler = OAuthenticatorWithLogoutLogoutHandler
    
    @gen.coroutine
    def single_logout(self, user):
        if self.single_logout_url:
            auth_state = yield user.get_auth_state()
            if auth_state:
                self.log.info("Single logout: %s", user.name)

                http_client = AsyncHTTPClient()
                url = self.single_logout_url

                refresh_token = auth_state.get('refresh_token')

                headers = {
                    "Accept": "application/json",
                    "User-Agent": "JupyterHub",
                }
                params = dict(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    refresh_token=refresh_token,
                )
                req = HTTPRequest(url,
                    method="POST",
                    headers=headers,
                    validate_cert=self.tls_verify,
                    body=urllib.parse.urlencode(params),
                )
                yield http_client.fetch(req)

    def get_handlers(self, app):
        return [
            (r'/logout', self.logout_handler),
        ] + super().get_handlers(app)


