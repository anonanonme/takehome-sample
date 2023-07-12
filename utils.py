import random
import string
from typing import List, Callable, Dict, Union

import aiohttp

from settings import APPLICATION_SERVER_PORT


def generate_test_paths(test_path_amount: int,
                        segment_amount: int = 6,
                        string_pool_amount: int = 3,
                        string_length: int = 3) -> List[str]:
    # function generates a random string of given length
    random_string_generator: Callable[[int], str] = \
        lambda length: ''.join(random.choices(string.ascii_letters, k=length))

    # a pool of randomly generated strings.
    strings = [random_string_generator(string_length) for _ in range(string_pool_amount)]

    # function to create segments of an arbitrary url path as a list of strings
    # each segment is randomly selected from the string pool above
    segment_generator: Callable[[int], List[str]] = lambda length: ["api"] + [
        strings[random.randrange(0, string_pool_amount)] for _ in range(length)]

    # function converts list of segments to path string seperated by "/"
    segments_to_path: Callable[[List[int]], str] = lambda segs: f'/{"/".join(segs)}/'

    # a pool of url paths still in list form of segment strings.
    segments = (segment_generator(random.randint(1, segment_amount)) for _ in range(test_path_amount))

    # the above pool serialized into a proper url path with each segment seperated by "/"
    paths = [segments_to_path(segment) for segment in segments]
    return paths


Json = Union[Dict[str, 'Json'], List['Json'], int, float, str]


async def make_get_request(url: str) -> Json:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


def url_from_path(path: str) -> str:
    return f"http://localhost:{APPLICATION_SERVER_PORT}{path}"
