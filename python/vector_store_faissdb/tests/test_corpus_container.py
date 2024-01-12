import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest
from langchain.chat_models import ChatOpenAI


@pytest.fixture
def openai_api_key():
    # TODO: need to isolate test fully
    return ''


@pytest.fixture(scope='function', params=[
    'The Earth revolves around the Sun.',
    'The Earth takes 365.25 days to fully orbit the sun.',
    'The Earth has a slightly tilted axis.',
    'The Earth is the third planet from the Sun.',
])
def query(request):
    return request.param


@pytest.skip(reason='feature is disabled')
def test_empty_db(openai_api_key):
    with mock.patch.dict(os.environ, clear=True,
                         CORPUS_DB_PATH='',
                         OPENAI_API_KEY=openai_api_key,
                         ), \
            tempfile.TemporaryDirectory() as dirname:
        from vector_store_faissdb import CorpusContainer

        llm = ChatOpenAI(openai_api_key=openai_api_key, client=None, temperature=0.0)
        cc = CorpusContainer(openai_api_key, llm, Path(dirname))
        assert cc.size_of_corpus() == 0


@pytest.skip(reason='feature is disabled')
def test_first_entry_query(openai_api_key, query):
    with mock.patch.dict(os.environ, clear=True,
                         CORPUS_DB_PATH='',
                         OPENAI_API_KEY=openai_api_key,
                         ), \
            tempfile.TemporaryDirectory() as dirname:
        from vector_store_faissdb import CorpusContainer

        llm = ChatOpenAI(openai_api_key=openai_api_key, client=None, temperature=0.0)
        cc = CorpusContainer(openai_api_key, llm, Path(dirname))
        cc.index([query], save_to_disk=False)
        context = cc.search(query)
        assert context
