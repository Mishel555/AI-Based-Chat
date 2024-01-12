import time
import typing
import urllib
import urllib.error
import urllib.request
from typing import List, Tuple

from langchain.chat_models import ChatOpenAI
from loguru import logger
from pyalex import Works

ALLOWED_CHAT_MODEL_TYPES = ChatOpenAI  # Used in other files


def parse_bullet_response(response: str) -> List[str]:
    # split response by newline, then remove the first dash
    return [x.lstrip("-").strip() for x in response.split("\n") if x.strip()]


def openalex_ids_to_fields(openalex_ids: List[str], fields: List[str]) -> List[tuple]:
    # cannot get more than 50 at a time - will be fine once we switch to internal DB
    openalex_ids = openalex_ids[:50]
    works = Works().filter(openalex_id="|".join(openalex_ids)).get(per_page=min(len(openalex_ids) + 5, 200))
    return [tuple(work[field] for field in fields) for work in works]


def search_oa(search_term: str, max_results: int = 0,
              extra_fields: typing.Optional[typing.Tuple[str, ...]] = None) -> List[Tuple[str, str, str]]:
    logger.info(f"Searching OpenAlex for '{search_term}'")

    results = Works().search(search_term).get(per_page=200)

    if max_results > 0:
        results = sorted(results, key=lambda w: w["publication_date"], reverse=True)
        results = results[:max_results]

    fields = ["id", "title", "abstract"] + list(extra_fields or [])
    return [tuple(work[field] for field in fields) for work in results]


def urlopen_wrapper(url: str, task: str, delay: int = 2, n_retries: int = 5, do_not_fail: bool = False):
    for _ in range(n_retries):
        try:
            return urllib.request.urlopen(url).read()
        except urllib.error.HTTPError as e:
            logger.warning(f"Failed to {task}, retrying in {delay} seconds. {repr(e)}. {url}")
            time.sleep(delay)
    else:
        if do_not_fail:
            return None
        else:
            raise RuntimeError(f"Failed to {task} after {n_retries} retries")


def _get_oa_location(work: Works) -> str:
    oa_location = ""
    if work["primary_location"]:
        if work["primary_location"]["is_oa"]:
            oa_location = work["primary_location"]["landing_page_url"]
    if "arxiv" not in oa_location:
        possible_locations = [location["pdf_url"] for location in work["locations"] if location["pdf_url"]]
        if possible_locations:
            oa_location = possible_locations[0]
    oa_location = str(oa_location)
    return oa_location


def _make_hyperlink(url: str, text: str) -> str:
    return f"[{text}]({url})"


def _metadata_extractor(work: Works) -> Tuple[str, int]:
    doi = work["doi"]
    publication_year = str(work["publication_year"])
    oa_location = _get_oa_location(work)

    paper_desc = "'" + work["title"] + f"' ({publication_year}) ("
    paper_desc += _make_hyperlink(doi, "DOI")
    if oa_location not in ("", doi):
        paper_desc += " - " + _make_hyperlink(oa_location, "Full text") + ""
    paper_desc += ")"

    return paper_desc, publication_year


def get_metadata_from_oa(openalex_id: str) -> Tuple[str, int]:
    work = Works()[openalex_id]
    out = _metadata_extractor(work)
    return out


def get_batch_metadata_from_oa(openalex_ids: List[str]) -> List[Tuple[str, int]]:
    collect = []
    works = Works().filter(openalex_id="|".join(openalex_ids)).get()
    for work in works:
        collect.append(_metadata_extractor(work))
    return collect

# def get_abstract_from_oa(openalex_id: str) -> Tuple[str, str]:
#     work = OpenAlexWork()
#     work.set_from_api(openalex_id)
#     return work["title"], work["abstract"]


# def get_metadata_from_oa(openalex_id: str) -> Tuple[str, str, str]:
#     work = OpenAlexWork()
#     work.set_from_api(openalex_id)
#     out = _metadata_extractor(work)
#     return out


# def get_year_from_oa(openalex_id: str) -> str:
#     work = OpenAlexWork()
#     work.set_from_api(openalex_id)
#     publication_year = str(work["publication_year"])
#     return publication_year


# def parse_leap_csv(csv_path: str, expand: bool = False) -> pd.DataFrame:
#     column_remap = {"OpenAlex ID": "openalex_id", "Paper Title": "title", "Cluster Number": "cluster"}
#     df = pd.read_csv(csv_path).rename(columns=column_remap)
#     df = df[list(column_remap.values())]
#
#     # if expand:
#     #     # get more papers using the input as a seed
#     #     oaids = ','.join(df['openalex_id'])
#
#     df[["title", "abstract"]] = df["openalex_id"].apply(get_abstract_from_oa).to_list()
#
#     abstract_len = df["abstract"].apply(lambda x: len(x.split()))
#     df = df[abstract_len > 9]
#
#     return df

# def get_work_oa(work_id: str) -> Tuple[str, str, str]:
#     work = OpenAlexWork()
#     work.set_from_api(work_id)
#     return parse_oa_work(work)
