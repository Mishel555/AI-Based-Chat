import threading
import typing
from pathlib import Path

from chatbot_cloud_util.base_validator import BaseCorpusContainer
from chatbot_validator.corpus import CorpusChain
from chatbot_validator.exceptions import NoRelevantDocumentsFound, ValidatorError
from langchain.chat_models.base import BaseChatModel
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from loguru import logger


class CorpusContainer(BaseCorpusContainer):
    # extra_oa_fields = ('doi',)
    extra_oa_fields = ()

    def __init__(self, openai_api_key: str, llm: BaseChatModel, local_path: Path = None, **kwargs):
        self.chain = CorpusChain(llm=llm, extra_oa_fields=self.extra_oa_fields)
        self._local_path = local_path
        self._emb = OpenAIEmbeddings(client=None, openai_api_key=openai_api_key)
        self._db = None
        self._db_lock = threading.Lock()

    @property
    def emb(self):
        return self._emb

    def index(self, texts: typing.List[str], save_to_disk: bool = False):
        assert not save_to_disk or self._local_path

        docs = []
        for text in texts:
            try:
                df = self.chain({'human_input': text})
                for _, row in df.iterrows():
                    abstract = row['abstract']
                    abstract = abstract[:15_000] if len(abstract) > 15_000 else abstract
                    doc = Document(
                        page_content=' '.join(
                            [
                                f'ID: {str(row["openalex_id"])}',
                                f'TITLE: {str(row["title"])}.',
                                f'ABSTRACT: {str(abstract)}'
                            ]
                        ),
                        metadata={f.upper(): str(row[f]) for f in self.extra_oa_fields},
                    )
                    docs.append(doc)
            except ValidatorError:
                logger.warning(f'No documents found for search term: {text[:100]}')

        if not docs:
            raise NoRelevantDocumentsFound('No relevant documents found')

        self._add_docs_to_db(docs, save_to_disk)

    def size_of_corpus(self):
        self._db_lock.acquire()
        try:
            return len(self._db.index_to_docstore_id) if self._db else 0
        finally:
            self._db_lock.release()

    def search(self, query: str, maximum_nearest_neighbors: int = 20):
        return self._db.similarity_search_with_score(query, k=min(maximum_nearest_neighbors, self.size_of_corpus()))

    def _add_docs_to_db(self, docs, save_to_disk):
        if save_to_disk and not self._local_path.exists():
            self._local_path.mkdir(parents=True, exist_ok=False)

        self._db_lock.acquire()
        try:
            try:
                if save_to_disk and not self._db:
                    next(self._local_path.iterdir())
                    self._db = FAISS.load_local(str(self._local_path), self.emb)
                elif not self._db:
                    raise StopIteration

                self._db.add_documents(docs, embedding=self.emb)
            except StopIteration:
                self._db = FAISS.from_documents(docs, self.emb)

            if save_to_disk:
                self._save()
        finally:
            self._db_lock.release()

    def _save(self):
        self._db.save_local(self._local_path)
