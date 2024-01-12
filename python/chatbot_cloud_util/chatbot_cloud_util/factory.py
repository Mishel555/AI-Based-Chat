import os
from typing import cast

from chatbot_cloud_util.aws_api import get_secret
from chatbot_validator.assertions import AssertionCreator
from chatbot_validator.evidence import EvidenceCreator
from chatbot_validator.statement import StatementCreator
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel

_ac: AssertionCreator = None
_ec: EvidenceCreator = None
_sc: StatementCreator = None


def get_env(name, cast_type, default_value, fallback_to_default=True):
    try:
        v = os.environ.get(name, default_value) if default_value else os.environ[name]
        return cast(cast_type, v)
    except (KeyError, ValueError):
        if fallback_to_default:
            return default_value
        raise


verbosity = get_env('VERBOSITY', int, 0)


def jwt_key(secret_id: str) -> str:
    if not globals().get('_jwt_key'):
        globals()['_jwt_key'] = get_secret(secret_id)
    return globals()['_jwt_key']


def open_ai_key(secret_id: str) -> str:
    if not globals().get('_open_ai_key'):
        globals()['_open_ai_key'] = get_secret(secret_id)
    return globals()['_open_ai_key']


def llm(llm_name: str, llm_kwargs=None, **kwargs) -> BaseChatModel:
    # TODO: think about better way of injecting extra args to llm factory
    if llm_name == 'chat_openai':
        return ChatOpenAI(
            openai_api_key=open_ai_key(kwargs['openai_secret_key_name']),
            client=None, temperature=0.0, **(llm_kwargs or {})
        )

    raise ValueError(f'Unsupported LLM type {llm_name}')


def get_ac(llm_name, **kwargs) -> AssertionCreator:
    global _ac
    if not _ac:
        loud = verbosity > 10
        ac_llm = llm(llm_name, **kwargs)
        _ac = AssertionCreator(llm=ac_llm, verbose=loud)

    return _ac


def get_ec(llm_name, **kwargs) -> EvidenceCreator:
    global _ec
    if not _ec:
        loud = verbosity > 10
        ec_llm = llm(llm_name, model_name='gpt-4', **kwargs)
        _ec = EvidenceCreator(llm=ec_llm, verbose=loud)

    return _ec


def get_sc(llm_name, **kwargs) -> StatementCreator:
    loud = verbosity > 10
    sc_llm = llm(llm_name, **kwargs)
    return StatementCreator(llm=sc_llm, verbose=loud, memory=kwargs.get('memory'))
