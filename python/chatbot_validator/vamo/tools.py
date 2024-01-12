import math
import os
from typing import Iterable, List, Optional


def get_package_root() -> str:
    import vamo

    return vamo.__path__[0]


def get_repo_root() -> str:
    return os.path.abspath(get_package_root() + "/..")


def get_openai_api_key():
    if (openai_api_key := os.getenv("OPENAI_API_KEY")) is not None:
        return openai_api_key

    with open(os.path.join(get_repo_root(), "openai_key.txt"), "r") as f:
        openai_api_key = f.read().strip()
    return openai_api_key


def make_chain(seq: List, size: Optional[int] = None, n: Optional[int] = None) -> Iterable:
    """Turn a single sequence into a sequence of smaller sequences, each of (max) length size.
    Returns an iterator. This is the reverse operation of itertools.chain.from_iterable.

    Args:
        seq (List): Input list
        size (Optional[int], optional): The size of each subsequence. Defaults to None.
        n (Optional[int], optional): The number of subsequences of ~equal size. Defaults to None.

    Returns:
        Iterable:  A sequence of sequences, each of (max) length size, or of total length n
    """

    if (size is None) == (n is None):
        raise RuntimeError("Exactly one of size or n must be specified")

    if size is None:
        size = math.ceil(len(seq) / n)
    else:
        n = math.ceil(len(seq) / size)

    return (seq[i * size: (i + 1) * size] for i in range(n))
    # return (seq[pos:pos + size] for pos in range(0, len(seq), size))
