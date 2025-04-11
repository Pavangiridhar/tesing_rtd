from connector_definition_runner import Runner


class RunnerOverride(Runner):

    def __init__(self, asset, asset_schema, http_proxy):
        super().__init__(asset, asset_schema, http_proxy)
        self.asset = asset
        self.username = self.asset['username']
        self.password = self.asset['password']
        self.url = self._join_url(self.url, '/jsonrpc')
        headers = {'Content-Type': 'application/json'}
        json_data = {'method': 'exec', 'params': [{'url': '/sys/login/user',
            'user': self.username, 'passwd': self.password}], 'id': 1,
            'ver': self.asset.get('jsonrpc')}
        response = self.session.post(self.url, headers=headers, json=
            json_data, verify=False)
        response.raise_for_status()
        json_response = response.json()
        self.session_id = json_response.get('session', '')
        self.session.headers.update({'Authorization:': 'Bearer ' + self.
            session_id})

    def run(self, inputs, action_schema):
        if self.auth_error:
            return self.parse_response(self.auth_error_response, action_schema)
        json_data = {'session': self.session_id}
        if inputs.get('json_body'):
            inputs['json_body'].update(json_data)
        else:
            inputs['json_body'] = json_data
        return super().run(inputs, action_schema)