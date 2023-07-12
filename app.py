import asyncio
from quart_redis import RedisHandler, get_redis
from settings import URL_PATH_COUNT_DATA_STRUCTURE, REDIS_URI, REDIS_URI_KEY, APPLICATION_SERVER_PORT
from utils import generate_test_paths, make_get_request, url_from_path

# Quart is a library completely isomorphic to flask when used with async functions. It is a drop in replacement.
# Quart is more efficient than flask with async await. Flask official documentation recommends Quart for async await.
# See here for more information: https://flask.palletsprojects.com/en/2.3.x/async-await/
from quart import Quart as Flask

app = Flask(__name__)
app.config[REDIS_URI_KEY] = REDIS_URI
redis_handler = RedisHandler(app)


@app.route('/api/<path:path>/', methods=['GET'])
async def api(path: str):
    redis = get_redis()

    # - pipeline insures that the zincrby and zrank call happen atomically and prevents race conditions.
    # - zincrby increments the score on the string, zrank fetches the new score
    pipeline = redis.pipeline()
    pipeline.zincrby(URL_PATH_COUNT_DATA_STRUCTURE, 1, path)
    pipeline.zrank(URL_PATH_COUNT_DATA_STRUCTURE, path, )

    data = await pipeline.execute()

    # returns the path and current count that was just made.
    return {"path": path, "count": int(data[0])}


@app.route("/test/<int:count>/", methods=['POST'])
async def test(count: int):
    paths = generate_test_paths(count)

    # gather executes all these functions concurrently then joins on the result.
    result = await asyncio.gather(
        *[make_get_request(url_from_path(path)) for path in paths])
    # result contains the result of each test request.
    return result


@app.route("/stats/", methods=['GET'])
async def stats():
    redis = get_redis()

    # returns entire sorted set of strings with scores ordered descending
    response = await redis.zrevrange(name=URL_PATH_COUNT_DATA_STRUCTURE,
                                     start=0,
                                     end=-1,
                                     withscores=True,
                                     # scores in redis are floats by default.
                                     # score_cast_func automatically converts to int.
                                     score_cast_func=lambda x: int(x))

    # returns in sorted order by count, the counts of each uri path that was made.
    return [{"path": path.decode('utf-8'), "count": count} for path, count in response]


if __name__ == '__main__':
    app.run(port=APPLICATION_SERVER_PORT)
