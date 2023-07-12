# Backend Developer Challenge

_Context: If you're seeing this, it means we'd like to see how you would solve a real-world problem. But to be totally clear, we won't be using your code for anything beyond deciding on moving forward in the hiring process._

## Request statistics exercise

In this exercise you will build a fully functioning Flask application packaged into
a Docker Compose environment.

The Flask app should count every request by URL path and store this metric in Redis.
This will form the basis of a component that has a wide range of uses like
[request limiting](https://developer.close.io/#ratelimits), capacity planning, cost accounting, etc.

It should handle the following three sets of endpoints:
* `GET /api/*` - Simulated API endpoints
* `GET /stats/` - Returns JSON report of URL request statistics
* `POST /test/{number of requests}/` - Starts a test run to generate fake requests

### Spec

1. Record number of requests for every URL handled by the Flask application.  Data shall be stored in Redis.
1. The `/api/*` endpoint should handle URL paths starting with `/api/` and followed by an arbitrary number of path segments.
   Example valid URLs: `/api/one/` or `/api/product/1/`. This is used to emulate what would be real API endpoints.
   For this exercise only consider `GET` requests but assume there would be millions of unique URLs. Ignore querystrings.
1. The `/stats/` endpoint shall return a JSON response that provides the URL request counts ordered from most
    requested to least requested.
1. `/test/{number of requests}/` is a testing endpoint that will simulate real requests:
   1. A `POST` request will start a test of `{number of requests}` `GET` requests to the local web application
   1. Each simulated request uses a random URL composed of:
      1. `/api/` followed by 1 to 6 path segments
      1. Each path segment is a random string pulled from a pool of 3 random strings used by a single test run
      1. Example of URLs in a single test run:
         * `/api/xyz/` (Valid: 1 path segment, 1 random string used so far)
         * `/api/xyz/abc/def/` (Valid: 3 path segments, 3 random strings used so far)
         * `/api/xyz/abc/ghi/` (Invalid: 4 different random strings were used for path segments in this test run)
         * `/api/xyz/xyz/xyz/xyz/xyz/xyz/xyz/` (Invalid: 7 path segments)
1. Package files into a fully functioning `docker-compose` project. To test we should be able to unzip files,
   run `docker-compose up` and point our local browser to `http://localhost:5000/stats/` to get the initial JSON report.

### Grading & Submission

Your solution will be evaluated as if it were a pull request for a feature that would serve customers from production infrastructure. It will be graded on functionality, completeness, documentation, cleanliness, production readiness, and code structure.  If you are unsure of a requirement just make a reasonable assumption and add a comment in your code.

Create a `.zip` of your project and include a README containing an overview of your solution with a self-critique explaining what you would continue iterating on if you had more time.
