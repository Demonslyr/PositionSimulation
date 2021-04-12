from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import requests
import json


class WarcraftLogsClient:
  api_base_url = 'https://www.warcraftlogs.com'
  api_base_path = '/api/v2'

  def __init__(self, client_id, client_secret):
    self.token = None
    self.client_id = client_id
    self.client_secret = client_secret
    self.client_authority = 'https://www.warcraftlogs.com/oauth'
    self.client_scopes = ''
    # Todo: See if requests.Session() requires any cleanup
    self.session = requests.Session()
    self.refreshToken()

  def getToken(self):
    if self.token is None:
      self.refreshToken()
    return self.token

  def refreshToken(self):
    # contrary to the name, this probably won't use the refresh token... it'll just nab a new one
    # Additionally, this is just a form post with 3 params... is a lib actually needed to make a post and get a json object?
    client = BackendApplicationClient(client_id=self.client_id)
    oauth = OAuth2Session(client=client)
    self.token = oauth.fetch_token(token_url=f'{self.client_authority}/token',
                                   client_id=self.client_id,
                                   client_secret=self.client_secret)
    # Turns out these tokens are 30 day tokens. Should probably save the token response to the user directory and check
    # for it and it's freshness on startup

  def queryWclV2Api(self, query):
    payload = json.dumps(query)
    default_headers = {
      'Content-Type': "application/json"
    }
    token_dict = self.getToken()
    default_headers.Authorization = f'Bearer {token_dict["access_token"]}'

    response = self.session.post(url=f'{self.api_base_url}{self.api_base_path}',
                                 json=payload,
                                 headers=default_headers)
    if response.status_code < 200 or response.status_code > 299:
      # Todo: the response was bad, handle it
      raise ValueError('Response was not a 2xx status code')
    return json.loads(response.json())
