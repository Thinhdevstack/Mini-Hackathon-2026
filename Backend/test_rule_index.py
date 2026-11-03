"""Verify authoritative docs replace legacy rules in the RAG input."""
import ast
import hashlib
import unittest
from pathlib import Path
from types import SimpleNamespace

class RuleIndexTest(unittest.TestCase):
    def test_docs_override_and_refresh_collection(self):
        base = Path(__file__).resolve().parent
        tree = ast.parse((base / 'main.py').read_text())
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'get_or_create_vectorstore')
        loaded, stores = [], []
        class Loader:
            def __init__(self, path, **kwargs): self.path = Path(path)
            def load(self):
                loaded.append(self.path)
                return [self.path.read_text()]
        class Store:
            def __init__(self, **kwargs):
                self.options = kwargs
                stores.append(self)
            def get(self): return {'ids': []}
            def add_documents(self, docs, ids): self.documents = docs
        scope = dict(Path=Path, hashlib=hashlib, BASE_DIR=base, DATA_DIR=base/'data',
                     DOCS_DIR=base.parent/'docs', CHROMA_PERSIST_DIR='unused', embedding_model=None,
                     Chroma=Store, TextLoader=Loader,
                     RecursiveCharacterTextSplitter=lambda **k: SimpleNamespace(split_documents=lambda docs: docs))
        exec(compile(ast.Module(body=[fn], type_ignores=[]), 'main.py', 'exec'), scope)
        scope['get_or_create_vectorstore']()
        self.assertIn(base.parent/'docs/cpp_rule.md', loaded)
        self.assertIn(base.parent/'docs/project_structure.md', loaded)
        self.assertNotIn(base/'data/cpp_rule.md', loaded)
        self.assertIn(base/'data/onboarding.md', loaded)
        self.assertEqual(len(loaded), len(set(p.name for p in loaded)))
        self.assertTrue(stores[0].options['collection_name'].startswith('interna-'))

if __name__ == '__main__': unittest.main()
