import json
import typing
from typing import Dict, List, Tuple

import chatbot_validator.prompts.corpus as prompts
import pandas as pd
from chatbot_validator.base import ChainBaseClass
from chatbot_validator.exceptions import NoRelevantDocumentsFound
from chatbot_validator.tools import ALLOWED_CHAT_MODEL_TYPES, search_oa, urlopen_wrapper
from langchain.chains import LLMChain
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS, VectorStore
from loguru import logger
from vamo.tools import get_openai_api_key, make_chain


class CorpusChain(ChainBaseClass):
    def __init__(self,
                 llm: ALLOWED_CHAT_MODEL_TYPES,
                 max_per_search: int = 100,
                 expand_with_leap: bool = False,
                 extra_oa_fields: typing.Optional[typing.Tuple[str, ...]] = None,
                 **kwargs):
        self.set_default_template(prompts.v1, prompts.structure_output_template)

        prompt = PromptTemplate(input_variables=["human_input"], template=self.default_template,
                                template_format="jinja2")
        self.chain = LLMChain(llm=llm, prompt=prompt, **kwargs)

        self.max_per_search = max_per_search
        self.expand_with_leap = expand_with_leap
        self.extra_oa_fields = extra_oa_fields

    def _postprocess_response(self, out: Dict[str, str]) -> pd.DataFrame:
        search_terms = json.loads(out["text"])

        results = []
        for search_term in search_terms:
            results.extend(search_oa(search_term, max_results=self.max_per_search, extra_fields=self.extra_oa_fields))

        results = list(set(results))

        if not results:
            raise NoRelevantDocumentsFound('No OpelAlex documents found')

        if self.expand_with_leap:
            results = self._expand_with_leap(results)

        results = pd.DataFrame(
            results,
            columns=["openalex_id", "title", "abstract"] + list(self.extra_oa_fields or [])
        )
        results = results.drop_duplicates(subset=["openalex_id"])

        abstract_filter = results["abstract"].apply(lambda x: x is not None and len(x.split()) > 9)
        results = results[abstract_filter]

        return results

    @staticmethod
    def _expand_with_leap(oa_results: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
        oa_ids = list(set([x[0] for x in oa_results]))

        leap_results = []

        for batch in make_chain(oa_ids, size=5):
            leap_url = "http://10.15.4.248:5000/" + ",".join(batch)
            leap_response = urlopen_wrapper(leap_url, "query LEAP", do_not_fail=True)
            if leap_response is None:
                logger.error("Failed to query: " + leap_url)
                continue

            leap_response = json.loads(leap_response)
            oa_dict = leap_response["oa_data"]

            for oa_id, info in oa_dict.items():
                leap_results.append((oa_id, info["Item"]["title"], info["Item"]["abstract"]))

        return oa_results + leap_results


class CorpusCreator:
    def __init__(self, llm, **kwargs):
        self.chain = CorpusChain(llm=llm, **kwargs)
        self.llm = llm

    def set_dataframe(self, human_input: str) -> None:
        self.df = self.chain({"human_input": human_input})

    def get_dataframe(self) -> pd.DataFrame:
        return self.df

    def _get_embeddings(self):
        return OpenAIEmbeddings(client=None, openai_api_key=get_openai_api_key())

    def set_corpus(self, human_input: str) -> None:
        self.set_dataframe(human_input)

        emb = self._get_embeddings()

        docs = []
        for _, row in self.df.iterrows():
            abstract = row["abstract"]
            # Truncate abstract to 15,000 characters
            if len(abstract) > 15_000:
                abstract = abstract[:15_000]
            doc = Document(
                page_content="ID: " + str(row["openalex_id"]) + " TITLE: " + str(row["title"]) + ". ABSTRACT: " + str(
                    abstract)
            )
            docs.append(doc)
        db = FAISS.from_documents(docs, emb)

        self.corpus = db

    def get_corpus(self) -> VectorStore:
        return self.corpus
