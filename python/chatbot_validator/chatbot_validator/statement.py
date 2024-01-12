from typing import Dict, List, Optional

from chatbot_validator.base import ChainBaseClass
from chatbot_validator.prompts import statement as prompts
from chatbot_validator.tools import ALLOWED_CHAT_MODEL_TYPES
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from loguru import logger


class StatementChain(ChainBaseClass):
    OUTPUT_KEY = "text"
    INPUT_KEY = "human_input"

    def __init__(self, llm: ALLOWED_CHAT_MODEL_TYPES, memory: Optional[ConversationBufferMemory] = None,
                 verbose: bool = False, **kwargs):
        self.set_default_template(prompts.v0)
        self.llm = llm

        input_variables = [self.INPUT_KEY]
        if memory is not None:
            input_variables.append("history")
        self.prompt = PromptTemplate(
            input_variables=input_variables,
            template=self.default_template,
            template_format="jinja2"
        )
        self.chain = ConversationChain(
            llm=self.llm,
            input_key=self.INPUT_KEY,
            prompt=self.prompt,
            verbose=verbose,
            output_key=self.OUTPUT_KEY,
            memory=memory,
        )

    def _postprocess_response(self, out: Dict[str, str]) -> List[str]:
        return out[self.OUTPUT_KEY]


class StatementCreator:
    def __init__(self, llm: ALLOWED_CHAT_MODEL_TYPES, **kwargs):
        self.chain = StatementChain(llm=llm, **kwargs)

    def set_statement(self, human_input: str):
        logger.info(f"Human Input: {human_input}")
        self.statement = self.chain({"human_input": human_input})
        logger.info(f"Statement: {self.statement}")
        return self

    def get_statement(self) -> str:
        return self.statement
