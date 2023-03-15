from typing import Optional
from googlesearch import google_search
from duckduckgo_search import ddg as ddg_search
import multiprocessing as mp
from dataclasses import dataclass
from tqdm import tqdm

import json

NUM_PAGE = 3
JSON_PATH = "filtered_users_1.json"  # path to a json file of linkedin profiles.
START_INDEX = 0
OFFSET = 500

total = 0


@dataclass(frozen=True)
class UserProfile:
    first_name: str
    last_name: str
    real_name: str
    title: str
    email: Optional[str]
    image: Optional[str]


def search_profile(
    name: str,
    last_name: str,
    real_name: Optional[str],
    title: str,
    image_uri: Optional[str],
    email: Optional[str],
    engine: str = "duckduckgo",
) -> "list[str]":
    """Search a person's profile.

    search_profile(
        name="Dr",
        last_name="Blah Blah",
        title="Gives happy pills",
        image_uri="",
        real_name=None,
        email=None
    )
    """
    search_string = "linkedin " f"{name} " f"{last_name} " f"{title} "
    if engine == "google":
        search_results = list(google_search(search_string, NUM_PAGE))
    elif engine == "duckduckgo":
        res = ddg_search(search_string)
        if res is not None:
            search_results = [
                d["href"] for d in res if (d is not None and d["href"] is not None)
            ]
        else:
            print("warning")
            search_results = []
    else:
        raise ValueError("Wrong Engine")
    return search_results


def _worker(all_args: tuple) -> "list[str]":
    try:
        results = search_profile(
            all_args[0],
            all_args[1],
            all_args[2],
            all_args[3],
            all_args[4],
            all_args[5],
        )
        return [r for r in results if "linkedin.com/in" in r]
    except Exception as e:
        print(e)
        print(results)
        raise e


def run(json_path: str) -> None:
    with open(json_path, "r") as f:
        data = json.loads(f.read())

    user_profile_data = [UserProfile(**d) for d in data]

    row_args = []
    for user in user_profile_data:
        args = (
            user.first_name,
            user.last_name,
            user.real_name,
            user.title,
            user.image,
            user.email,
        )
        row_args.append(args)

    # NOTE(ih_herzi) Hotfix
    # row_args = row_args[START_INDEX : START_INDEX + OFFSET]
    res = []
    for args in tqdm(row_args, total=len(row_args)):
        try:
            res.append(_worker(args))
        except Exception as e:
            print(e)

    try:
        with mp.Pool(processes=8) as pool:
            search_results = []
            for i, search_result in tqdm(
                enumerate(pool.imap_unordered(_worker, row_args)), total=len(row_args)
            ):
                search_results.append(search_result)
        with open(f"names_{START_INDEX}.txt", "w") as f:
            f.write("\n".join([s[0] for s in search_results if s]))
    except KeyboardInterrupt as ke:
        with open(f"names_{START_INDEX}.txt", "w") as f:
            f.write("\n".join([s[0] for s in search_results if s]))


if __name__ == "__main__":
    run(json_path=JSON_PATH)
