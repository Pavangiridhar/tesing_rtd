import gzip
import json
from urllib.parse import urljoin
from connector_definition_runner import Runner as RO


class RunnerOverride(RO):

    def run(self, inputs, action_schema):
        if self.auth_error:
            return self.parse_response(self.auth_error_response, action_schema)
        inputs['data_body'] = inputs['files'][1][1].read()
        inputs.pop('files')
        response = self.session.request(method=self.get_method(inputs,
            action_schema['meta']), url=self._join_url(self.url, self.
            get_endpoint(inputs, action_schema['meta'])), **self.get_kwargs
            (inputs, action_schema['meta']))
        resp = self.parse_response(response, action_schema)
        return resp

    def get_kwargs(self, inputs, action_meta=None):
        self.params.update(inputs.get('parameters', {}))
        if 'headers' in action_meta:
            headers = action_meta['headers']
            self._format_headers(headers, inputs)
            headers.update(inputs.get('headers', {}))
            inputs['headers'] = headers
        return {'params': self.params, 'data': inputs.get('data_body'),
            'headers': inputs.get('headers')}
