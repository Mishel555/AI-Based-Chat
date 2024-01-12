import json
from typing import Dict, List

import chatbot_validator.prompts.assertions as prompts
from chatbot_validator.base import ChainBaseClass
from chatbot_validator.tools import ALLOWED_CHAT_MODEL_TYPES
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from loguru import logger


class AssertionChain(ChainBaseClass):
    def __init__(self, llm: ALLOWED_CHAT_MODEL_TYPES, **kwargs):
        self.set_default_template(prompts.v1, prompts.structure_output_template)
        self.llm = llm
        self.prompt = PromptTemplate(input_variables=["human_input"], template=self.default_template,
                                     template_format="jinja2")
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt, **kwargs)

    def _postprocess_response(self, out: Dict[str, str]) -> List[str]:
        return json.loads(out["text"])


class AssertionValidatorChain(ChainBaseClass):
    def __init__(self, llm: ALLOWED_CHAT_MODEL_TYPES, **kwargs):
        self.set_default_template(prompts.v0_validator)

        prompt = PromptTemplate(input_variables=["assertion"], template=self.default_template, template_format="jinja2")
        self.chain = LLMChain(llm=llm, prompt=prompt, **kwargs)


class AssertionCreator:
    def __init__(self, llm: ALLOWED_CHAT_MODEL_TYPES, **kwargs):
        self.chain = AssertionChain(llm=llm, **kwargs)

    def set_assertions(self, human_input: str):
        logger.info(f"Human Input: {human_input}")
        self.assertions = self.chain({"human_input": human_input})
        logger.info(f"Assertions: {self.assertions}")
        return self

    def get_assertions(self) -> List[str]:
        return self.assertions


class AssertionValidator:
    def __init__(self, llm: ALLOWED_CHAT_MODEL_TYPES, **kwargs):
        self.assertion_chain = AssertionValidatorChain(llm=llm, **kwargs)

    def validate(self, assertion: str) -> dict:
        validation = self.assertion_chain({"assertion": assertion})
        logger.info(f"Assertion Validation: {validation}")
        return validation
