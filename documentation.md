# Backend Developer Challenge

## Note:

This project uses Quart which is has an api identical to Flask. If needed one can easily switch back to flask by running
this command:

```bash
poetry remove quart
poetry add flask
```

Then editing this line the app.py file:

```python
from quart import Quart as Flask
```

to this:

```python
from flask import Flask
```

Quart is better suited for async await syntax according to flask documentation:
https://flask.palletsprojects.com/en/2.3.x/async-await/

Otherwise, all the syntax, library functions and methods in Quart are the same as Flask.

## Summary

Project is divided into three python files:

1. `app.py` contains all the relevant routes and http handlers for the application
    - api, test, stats
2. `utils.py` contains two utility functions.
    - `generate_test_paths` generates random uri paths for the test route.
    - `make_get_request` is an async function that makes get requests for the test route.
    - `url_from_path` takes a path string and returns the full url.
3. `settings.py` contains various global constants.

The project utilizes redis sorted sets as documented here: https://redis.io/docs/data-types/sorted-sets/

This data structure is essentially a collection of unique strings sorted by an associated score. This data structure is
the most efficient data structure according to the given requirements of returning all the data in sorted order and
quickly incrementing the counts per route. Inserts are O(log(n)) and retrieval does not require any additional
processing as elements are already sorted. This data structure was used as opposed to a regular hash map to keep
potentially blocking sorting operations off of the application server.

async await is used to fully utilize threads efficiently as threads can switch to handle other requests while awaiting
IO calls.

## Instructions

1. Make sure you have `docker` and `docker-compose` on your system
2. Run `docker-compose up --build`
    - This should spawn two dockerized processes.
        - One `redis` instance, running on port `6379`.
        - One python `Hypercorn` server using `app.py` with the `Quart/flask` framework on port `5000`
3. Test commands:
    1. `docker exec -it redis redis-cli FLUSHALL` (clears all redis data)
    2. `docker exec -it flask poetry run http localhost:5000/api/hello/world/`
    3. `docker exec -it flask poetry run http localhost:5000/stats/`
    3. `docker exec -it flask poetry run http POST localhost:5000/test/1000/` (use 500 if this fails, addressed in
       criticisms)
    4. `docker exec -it flask poetry run http localhost:5000/stats/`

## Self Criticism

### or things I would've done if I had more time.

- **testing**: No unit tests or integration tests were written. Most of this was tested manually. The code was also not
  fully organized for testing. Pure logic is segregated into utils.py for easier testing, but `generate_test_paths`
  needs to segregate the random number generation in order to be deterministic and unit testable.

  Additionally, since most critical operations happen on redis, to make this application more testable one should wrap
  all redis specific IO operations into associated functions so that these functions can be used in integration tests or
  essentially "unit tests" that occur within the context of "redis"
  \
  &nbsp;
- **configuration** certain things like ports and hostnames are hardcoded in several places. Ideally there should be a
  single source of truth. The application needs to read one file and get all of this information along with the
  configuration files that reference the same data. I went as far as creating a single source of truth for the python
  app via the `settings.py` file, but this settings file needs to gather things from more universal areas that the
  Docker files should also reference.
  \
  &nbsp;
- **security** redis should be pass coded, there should be authentication and security layers wrapping the application
  and the infrastructure.
  \
  &nbsp;
- **persistence** redis supports snapshots, There should be periodic snapshots of the data (or just use save `stats`) in
  case it fails. Right now the all data is lost permanently if the redis service fails. (On proper shutdown this redis
  docker instance automatically persists data but it does not save periodically)
  \
  &nbsp;
- **benchmarking** did not benchmark performance. Is async with Quart really better or is Flask with threads better?
  Redis is single threaded with serial operations anyway so it's not necessarily clear how much better Quart is. Quart
  is newer and it may not be as compatible with other libraries nor may it be as robust as Flask ( I don't know as I
  haven't used Quart extensively)
  \
  &nbsp;
- **inserts slow** It may be worth it to speed up inserts by counting the strings unsorted in a hashmap. Sorting can
  happen on the client side as the operation is only done once anyway. I chose the option to use a sorted set because
  sorted results was a requirement but realistically this is easily a cheap client side operation.
  \
  &nbsp;
- **analytics** One can easily persist all this data as events in real time by appending to a file(s). Or one can send
  the data to a analytics database as well. This allows dimensions of information to be embedded with the url like the
  User, country of origin, date of access, etc. This enables different metrics across different dimensions like uri-path
  access per month, per day, per user. The current methodology of pre-aggregating all events into counts per uri-path is
  limited.

  Yes, this will increase the time for the `stats` because on every request there needs to be an aggregation across all
  events. But if you think about it but over time the proportions of all these counts of each routes approaches a
  singular distribution which is most likely the normal distribution. So it's not as if someone needs to know this info
  every second as they can call `stats` after they have a good enough sample size and that distribution should remain
  relatively accurate for a long time. Thus you may only need to call `stats` once a month, and in that case a huge
  aggregation time for gathering internal metrics is acceptable and you can model the rest of the system just based off
  of metrics you gather once a month.
  \
  &nbsp;
- **batch test requests** You can run `test/5000/` and it could crash the server with too many simultaneous requests.
  The solution here is to batch the tests in async calls of 500 or some other number based off of metrics.

### length of time for project:

I would say around four hours. Around 3 hours for the coding itself and around 1 hour for the README.md and clarifying
comments into the code. 
