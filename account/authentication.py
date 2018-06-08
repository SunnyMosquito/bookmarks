from django.contrib.auth.models import User
from urllib import parse, request
import json

class OAuthGithub(object):
    def __init__(self, client_id, client_key, redirect_uri):
        self.client_id = client_id
        self.client_key = client_key
        self.redirect_uri = redirect_uri

    def get_auth_url(self):
        """获取授权页面的网址"""
        params = {'client_id': self.client_id,
                  'response_type': 'code',
                  'redirect_uri': self.redirect_uri,
                  'scope': 'get_user_info',
                  'state': 1}
        url = 'https://github.com/login/oauth/authorize?{}'.format(
            parse.urlencode(params))
        return url

    def get_access_token(self, code):
        """根据code获取access_token"""
        params = {'grant_type': 'authorization_code',
                  'client_id': self.client_id,
                  'client_secret': self.client_key,
                  'code': code,
                  'redirect_uri': self.redirect_uri}    # 回调地址
        url = 'https://github.com/login/oauth/access_token?{}'.format(
            parse.urlencode(params))

        # 访问该网址，获取access_token
        response = request.urlopen(url).read().decode()
        result = parse.parse_qs(response, True)
        access_token = str(result['access_token'][0])
        self.access_token = access_token
        return access_token


    def get_github_info(self):
        """获取用户的资料信息"""
        params = {'access_token': self.access_token}
        url = 'https://api.github.com/user?{}'.format(parse.urlencode(params))

        response = request.urlopen(url).read()
        return json.loads(response)


class EmailAuthBackend(object):
    """
    Authenticate using e-mail account.
    """

    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
            return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

