from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import http.client
import json



class WarcraftLogsClient:
  api_base_url = 'www.warcraftlogs.com'
  api_base_path = '/api/v2'
  def __init__(self, client_id, client_secret):
    self.token = None
    self.client_id = client_id
    self.client_secret = client_secret
    self.client_authority = ''
    self.client_scopes = ''
    self.refreshToken()

  def getToken(self):
    return ''

  def refreshToken(self):
    # contrary to the name, this probably won't use the refresh token... it'll just nab a new one
    client = BackendApplicationClient(client_id=self.client_id)
    oauth = OAuth2Session(client=client)
    self.token = oauth.fetch_token(token_url='https://provider.com/oauth2/token', client_id=self.client_id,
                                   client_secret=self.client_secret)

  def getReportPositionData(self,report_key):
    import requests

    session = requests.Session()
    session.get("http://example.com")
    # Connection is re-used
    session.get("http://example.com")



    conn = http.client.HTTPSConnection(self.api_base_url)
    payload = str("{\"query\":\"{\\n  reportData {\\n    report(code: \\\"")+str(report)+str("\\\") {\\n      events(startTime: ")+str(start)+str(", endTime: ")+str(end)+str(", killType: Kills, hostilityType:Enemies, dataType: DamageTaken, limit: 10000, includeResources: true, targetInstanceID: ")+str(local_boss_ID)+str(" \\n      )\\n        {data nextPageTimestamp}\\n    }\\n  }\\n}\\n\"}")
    # Todo: Convert the above payload to an unescaped dictionary and escape it with he json function
    query = {
      "query": f'{{reportData {{report(code: \"{report}\"){{fights(killType:Kills){{name startTime endTime encounterID}}}}}}}}'
    }

    payload = json.dumps(query)
    default_headers = {
      'Content-Type': "application/json"
    }
    access_token = self.getToken()
    default_headers.Authorization = f'Bearer {access_token}'
    headers = default_headers
    conn.request("POST", self.api_base_path, payload, headers)
    res = conn.getresponse()
    data = res.read()