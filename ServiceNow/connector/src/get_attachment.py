import gzip
import json
from urllib.parse import urljoin
from connector_definition_runner import Runner as RO


class RunnerOverride(RO):

    def run(self, inputs, action_schema):
        if self.auth_error:
            return self.parse_response(self.auth_error_response, action_schema)
        response = self.session.request(method=self.get_method(inputs,
            action_schema['meta']), url=urljoin(self.url, self.get_endpoint
            (inputs, action_schema['meta'])), **self.get_kwargs(inputs,
            action_schema['meta']))
        resp = self.parse_response(response, action_schema)
        if response.status_code == 200:
            filename = json.loads(resp['response_headers'][
                'x-attachment-metadata'])['file_name']
            data = response._content
            if response.headers.get('Content-Encoding') == 'gzip':
                try:
                    data = gzip.decompress(data)
                except:
                    pass
            resp['file'] = [{'filename': filename, 'file_data': data}]
            resp.pop('response_text', '')
        return resp
