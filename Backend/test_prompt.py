"""Offline regression test of the real chat endpoint, without loading LLM weights."""
import ast
import os
import unittest
from pathlib import Path
from types import SimpleNamespace

class PromptTest(unittest.TestCase):
    def test_context_history_and_sources(self):
        source = ast.parse(Path(__file__).with_name('main.py').read_text())
        endpoint = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'chat_endpoint')
        endpoint.decorator_list = []
        captured = []
        class HTTPException(Exception):
            def __init__(self, **kwargs):
                self.status_code = kwargs['status_code']
        scope = dict(os=os, ChatRequest=object, HTTPException=HTTPException,
                     vector_db=SimpleNamespace(similarity_search=lambda *a, **k: []),
                     SYSTEM_INSTRUCTION='Socratic mentor', is_local_mode=lambda: True,
                     call_ollama=lambda prompt: captured.append(prompt) or 'Gợi ý')
        exec(compile(ast.Module(body=[endpoint], type_ignores=[]), 'main.py', 'exec'), scope)
        req = SimpleNamespace(message='Còn trường hợp thứ hai?', user_message=None,
                              task_context=SimpleNamespace(title='Nhiệm vụ A', description='Mô tả A'),
                              history=[SimpleNamespace(role='user', content=f'Lượt {i}') for i in range(6)])
        result = scope['chat_endpoint'](req)
        self.assertEqual(result, {'reply': 'Gợi ý', 'docs': []})
        for value in ['Nhiệm vụ A', 'Mô tả A', 'Lượt 2', 'Lượt 5', req.message, 'Socratic mentor']:
            self.assertIn(value, captured[0])
        self.assertNotIn('Lượt 0', captured[0])
        req.message = ' '
        with self.assertRaises(HTTPException) as caught:
            scope['chat_endpoint'](req)
        self.assertEqual(caught.exception.status_code, 400)

if __name__ == '__main__':
    unittest.main()
