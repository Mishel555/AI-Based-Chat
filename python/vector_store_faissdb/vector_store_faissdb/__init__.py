import os
import typing
from pathlib import Path

from fastapi import FastAPI, HTTPException
from langchain.chat_models import ChatOpenAI
from loguru import logger
from pydantic import BaseModel
from vector_store_faissdb.corpus_container import CorpusContainer

app = FastAPI()
_corpus_container: CorpusContainer = None


class InitializationException(Exception):
    pass


def corpus_container() -> CorpusContainer:
    global _corpus_container

    store_path = Path(os.environ['CORPUS_DB_PATH'])
    openai_api_key = os.environ['OPENAI_API_KEY']

    if not _corpus_container:

        logger.info(f'Initializing corpus container with FaissDB at: {str(store_path)}')
        try:
            # _llm = llm(os.environ['LLM_NAME'])
            _llm = ChatOpenAI(openai_api_key=os.environ['OPENAI_API_KEY'], client=None, temperature=0.0, )
            _corpus_container = CorpusContainer(
                openai_api_key=openai_api_key,
                llm=_llm,
                local_path=store_path,
            )
        except Exception as e:
            raise InitializationException(str(e))

    return _corpus_container


# Eager load - we do not want this in production, deployment will be delayed or even stuck
# corpus_container()

class Status(BaseModel):
    status_code: int
    detail: str


class CorpusSize(BaseModel):
    size: int


class SearchResult(BaseModel):
    content: str
    metadata: typing.Dict[str, str]
    score: float


status = Status(status_code=200, detail='ok')


@app.get("/health")
async def health():
    global status
    if status.status_code == 200:
        return status
    raise HTTPException(**status.dict())


@app.post("/index")
async def index(texts: typing.List[str]):
    # TODO: maybe expose indexing through API as well
    pass


@app.get("/size")
async def size():
    global status
    try:
        cc = corpus_container()
        return CorpusSize(size=cc.size_of_corpus())
    except InitializationException as e:
        logger.exception('Unable to initialize corpus container')
        status = Status(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception('Unable to query through corpus container')
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/similarity_search")
async def similarity_search(query: str, maximum_nearest_neighbors: int = 20):
    global status
    try:
        cc = corpus_container()
        logger.debug(f'Querying for: {query}')
        context = cc.search(query, min(maximum_nearest_neighbors, cc.size_of_corpus()))
        return [SearchResult(content=c[0].page_content, metadata=c[0].metadata, score=c[1]) for c in context]
    except InitializationException as e:
        logger.exception('Unable to initialize corpus container')
        status = Status(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception('Unable to query through corpus container')
        raise HTTPException(status_code=500, detail=str(e))
