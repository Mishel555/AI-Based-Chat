import abc
import typing


class BaseCorpusContainer(abc.ABC):
    @abc.abstractmethod
    def index(self, texts: typing.List[str], save_to_disk: bool = True):
        pass

    @abc.abstractmethod
    def size_of_corpus(self):
        pass

    @abc.abstractmethod
    def search(self, query: str, maximum_nearest_neighbors: int):
        pass
