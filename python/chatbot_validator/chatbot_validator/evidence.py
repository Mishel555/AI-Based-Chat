import json
import re
from typing import Optional

import chatbot_validator.prompts.evidence as prompts
from chatbot_validator.base import ChainBaseClass
from chatbot_validator.exceptions import IncompleteDocumentsListFound
from chatbot_validator.tools import (
    ALLOWED_CHAT_MODEL_TYPES,
    get_batch_metadata_from_oa,
    get_metadata_from_oa,
)
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.vectorstores import VectorStore
from loguru import logger


class Evidence(ChainBaseClass):
    def __init__(self, llm: ALLOWED_CHAT_MODEL_TYPES, **kwargs):
        # self.set_default_template(prompts.v0)
        self.set_default_template(prompts.v1, prompts.structure_output_template)
        prompt = PromptTemplate(
            input_variables=["human_input", "context"], template=self.default_template, template_format="jinja2"
        )
        self.chain = load_qa_chain(
            llm=llm,
            chain_type="stuff",
            prompt=prompt,
            # document_prompt=PromptTemplate(
            #     input_variables=['page_content', 'DOI'],
            #     template='{page_content}, DOI: {DOI}'
            # ),
            **kwargs,
        )

    @property
    def template(self):
        return self.chain.llm_chain.prompt.template

    @template.setter
    def template(self, value):
        new_value = value
        # If the value contains the "{structure_output_template}", then we need to replace it with the output template
        # import streamlit as st

        # st.write(value)
        if "{{ structure_output_template }}" in value:
            new_value = value.replace("{{ structure_output_template }}", self.structure_output_template)
        self.chain.llm_chain.prompt.template = new_value


class EvidenceCreator:
    def __init__(self, llm: ALLOWED_CHAT_MODEL_TYPES, **kwargs):
        self.chain = Evidence(llm=llm, **kwargs)
        self.max_tokens = 3900  # For GPT-3.5. We'll have to modify this for other models.
        self.llm = llm

    def shorten_context(self, assertion: str, context: list) -> list:
        # we basically repeatedly calculat the number of tokens until it is okay
        template_tokens = self.llm.get_num_tokens(self.chain.template)
        assertion_tokens = self.llm.get_num_tokens(assertion)
        while True:
            context_tokens = sum([self.llm.get_num_tokens(d.page_content) for d in context])
            total_tokens = template_tokens + assertion_tokens + context_tokens
            if total_tokens <= self.max_tokens:
                break
            else:
                # find the index of the document with the most tokens
                max_index = max(range(len(context)), key=lambda i: self.llm.get_num_tokens(context[i].page_content))
                # remove 10% of the text of that document?
                page_length = len(context[max_index].page_content)
                context[max_index].page_content = context[max_index].page_content[: int(page_length * 0.9)]
        return context
    
    def _get_evidence_to_oa_url_mapping(self) -> dict:
        evidence = self.get_evidence()
        return {key: value['ID'] for key, value in evidence.items() if isinstance(value, dict)}
    
    def set_evidence(
            self,
            assertion: str,
            corpus: VectorStore,
            number_of_nearest_neighbors: int = 6,
            maximum_nearest_neighbors: int = 20,
            recency_vs_similarity: float = 0.5,
            get_metadata: bool = False,
            log_steps: bool = False,
            save_oa_urls: bool = False,  # store openalex urls in self._evidence_to_oa_url
    ) -> None:
        # Start with a large context to get a sense of statistics
        self.assertion = assertion
        size_of_corpus = len(corpus.index_to_docstore_id)
        context = corpus.similarity_search_with_score(assertion, k=min(maximum_nearest_neighbors, size_of_corpus))
        openalex_ids = [c[0].page_content.split(" TITLE")[0].split(("ID: "))[-1] for c in context]
        metadata = get_batch_metadata_from_oa(openalex_ids)
        years = [int(m[-1]) for m in metadata]
        # Min-max normalize the years
        year_min = min(years)
        year_max = max(years)
        try:
            years = [(y - year_min) / (year_max - year_min) for y in years]
        except Exception:
            years = [0.5 for y in years]
        # Normalize the scores
        scores = [c[1] for c in context]
        score_min = min(scores)
        score_max = max(scores)
        scores = [(s - score_min) / (score_max - score_min) for s in scores]
        # Combine the scores and years
        alpha = recency_vs_similarity
        scaled_scores = [alpha * score + (1 - alpha) * year for score, year in zip(scores, years)]
        # Sort the context by the scaled scores
        context = [c[0] for s, c in sorted(zip(scaled_scores, context), reverse=True, key=lambda pair: pair[0])]
        # Take the top k
        context = context[:number_of_nearest_neighbors]

        # If the context is too long, brute force chop it.
        context = self.shorten_context(self.assertion, context)

        evidence = self.chain(
            {"human_input": assertion, "input_documents": context},
            return_only_outputs=True
        )["output_text"]
        
        if save_oa_urls:
            self.evidence = evidence
            self._evidence_to_oa_url = self._get_evidence_to_oa_url_mapping()
        
        if get_metadata:
            # Use a regex to get all strings of the form "W###...#" from the evidence.
            evidence = evidence.replace("https://openalex.org/", "")
            ids_in_text = re.findall(r"W\d+", evidence)
            for work in ids_in_text:
                old_text = f"{work}"
                new_text, _ = get_metadata_from_oa(work.replace("[", "").replace("]", "").replace(";", ""))
                evidence = evidence.replace(old_text, new_text)

        self.evidence = evidence
        if log_steps:
            logger.info(f"truncated {context=}")
            logger.info(f"{evidence=}")
            
    def get_oa_urls(self) -> dict:
        return self._evidence_to_oa_url

    def get_evidence(self) -> "dict | str":
        if isinstance(self.evidence, dict):
            return self.evidence

        try:
            return json.loads(self.evidence)
        except json.decoder.JSONDecodeError:
            raise IncompleteDocumentsListFound('Unable to parse list of evidences')

    def get_assertion_and_evidence(self, assertion_index: Optional[int] = None) -> dict:
        evidence_result = self.get_evidence()
        if assertion_index is not None:
            evidence_result.update({f"Assertion {assertion_index}": self.assertion})
        else:
            evidence_result.update({"Assertion": self.assertion})
        return evidence_result

# Maybe it's useful to wrap the evidence in classes rather than keep as raw dictionaries?
# class EvidenceInstance:
#     def __init__(self, input_dict: dict):
#         self.input_dict = input_dict
#         self.set_attributes()

#     def set_attributes(self):
#         # Save every key-value pair in the input dict as an attribute
#         for key, value in self.input_dict.items():
#             clean_key = key.replace(" ", "_").lower()
#             setattr(self, clean_key, value)


# class EvidenceResult:
#     def __init__(self, input_dict: dict):
#         self.input_dict = input_dict
#         self.set_attributes()

#     def set_attributes(self):
#         # Save every key-value pair in the input dict as an attribute
#         for key, value in self.input_dict.items():
#             clean_key = key.replace(" ", "_").lower()
#             # If the key is not "evidence", save it as an attribute
#             if not clean_key.startswith("evidence_"):
#                 setattr(self, clean_key, value)
#             # If the key is "evidence", save each key-value pair in the value as an attribute
#             else:
#                 setattr(self, clean_key, EvidenceInstance(value))
