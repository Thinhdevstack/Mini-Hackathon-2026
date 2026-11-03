"""Exercise transport failure paths without starting embeddings or an LLM."""
import ast
import unittest
from pathlib import Path
from unittest.mock import Mock
import requests
from fastapi import HTTPException

class TransportTest(unittest.TestCase):
    def setUp(self):
        tree = ast.parse(Path(__file__).with_name('main.py').read_text())
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'call_ollama')
        self.post = Mock()
        transport = Mock(exceptions=requests.exceptions, post=self.post)
        scope = dict(requests=transport, HTTPException=HTTPException,
                     SYSTEM_INSTRUCTION='Mentor', OLLAMA_MODEL_NAME='StrictMentor', OLLAMA_API_URL='http://test/api/generate')
        exec(compile(ast.Module(body=[fn], type_ignores=[]), 'main.py', 'exec'), scope)
        self.call = scope['call_ollama']

    def test_answer_and_bounded_request(self):
        self.post.return_value.json.return_value = {'response': ' Xin chào '}
        self.assertEqual(self.call('test'), 'Xin chào')
        options = self.post.call_args.kwargs
        self.assertFalse(options['json']['think'])
        self.assertEqual(options['json']['options']['num_predict'], 512)
        self.assertEqual(options['timeout'], (5, 60))

    def test_timeout_and_connection(self):
        for error, status in [(requests.exceptions.ReadTimeout(), 504), (requests.exceptions.ConnectionError(), 503)]:
            self.post.side_effect = error
            with self.assertRaises(HTTPException) as caught:
                self.call('test')
            self.assertEqual(caught.exception.status_code, status)

    def test_empty_response_is_not_success(self):
        self.post.return_value.json.return_value = {'response': '', 'thinking': 'internal'}
        with self.assertRaises(HTTPException) as caught:
            self.call('test')
        self.assertEqual(caught.exception.status_code, 502)

if __name__ == '__main__':
    unittest.main()
