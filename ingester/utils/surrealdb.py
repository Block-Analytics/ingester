import requests

class SurrealDBClient():
    def __init__(self, base_url, username, password, ns, db) -> None:
        self.session = requests.Session()
        self.base_url = base_url
        self.session.auth = (username, password)
        self.ns = ns
        self.db = db
        self.session.headers.update({
            'Accept': 'application/json',
            'NS': ns,
            'DB': db
        })

    def sql(self, req:str): 
        resp = self.session.post(self.base_url + '/sql', data=req).json()
        if resp[0]["status"] != "OK":
            # Place a breakpoint here for trace errors
            # 
            pass
        return resp

