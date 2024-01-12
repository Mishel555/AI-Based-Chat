import typing

import requests
from chatbot_cloud_util.base_validator import BaseCorpusContainer
from chatbot_cloud_util.factory import llm, open_ai_key
from langchain.docstore.document import Document
from langchain.vectorstores import VectorStore
from requests.adapters import HTTPAdapter
from vector_store_faissdb import CorpusContainer


class RemoteCorpusContainerProxy(BaseCorpusContainer):
    __default_requests_timeout_sec = 300

    def __init__(self,
                 *args,
                 remote_url: str, requests_max_retries: int = 1, requests_timeout_sec: int = 0,
                 **kwargs):
        self._remote_url = remote_url.rstrip('/')
        self._session = requests.Session()
        self._session.mount(
            self._remote_url,
            HTTPAdapter(max_retries=requests_max_retries),
        )
        self._requests_timeout_sec = int(requests_timeout_sec)
        self._requests_timeout_sec = self._requests_timeout_sec or self.__default_requests_timeout_sec

    def index(self, texts: typing.List[str], save_to_disk: bool = True):
        raise RuntimeError('Proxy supports only read operations')

    def _get_json(self, rel_url, **kwargs):
        res = self._session.get(
            f'{self._remote_url}{rel_url}',
            timeout=self._requests_timeout_sec or self.__default_requests_timeout_sec,
            **kwargs
        )
        res.raise_for_status()
        return res.json()

    def size_of_corpus(self):
        res = self._get_json('/size')
        return res['size']

    def search(self, query: str, maximum_nearest_neighbors: int = 20, *args, params: dict = None, **kwargs):
        p = params or {}
        p.setdefault('query', query)
        p.setdefault('maximum_nearest_neighbors', maximum_nearest_neighbors)
        return self._get_json('/similarity_search', params=p, **kwargs)


class CompatibleRemoteCorpusContainerProxy(RemoteCorpusContainerProxy, VectorStore):
    def add_texts(self, *args, **kwargs):
        raise

    def similarity_search(self, *args, **kwargs):
        raise

    @classmethod
    def from_texts(cls, *args, **kwargs):
        raise

    @property
    def index_to_docstore_id(self):
        return [1] * self.size_of_corpus()

    def similarity_search_with_score(self, assertion: str, k: int):
        return self.search(assertion, k)

    def get_corpus(self):
        return self

    def search(self, *args, **kwargs):
        res = super().search(*args, **kwargs)
        return [(Document(page_content=c['content'], metadata=c['metadata']), c['score']) for c in res]


class CompatibleLocalCorpusContainerProxy(CorpusContainer, VectorStore):
    def add_texts(self, *args, **kwargs):
        raise

    def similarity_search(self, *args, **kwargs):
        raise

    @classmethod
    def from_texts(cls, *args, **kwargs):
        raise

    def __init__(self, llm_name: str, openai_secret_key_name: str, **kwargs):
        super().__init__(
            open_ai_key(openai_secret_key_name),
            llm(llm_name, openai_secret_key_name=openai_secret_key_name, **kwargs),
            local_path=None,
            **kwargs
        )

    @property
    def index_to_docstore_id(self):
        return [1] * self.size_of_corpus()

    def similarity_search_with_score(self, assertion: str, k: int):
        return self.search(assertion, k)

    def get_corpus(self):
        return self
