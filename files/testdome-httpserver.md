# TestDome - React题 - Http Server

- https://www.testdome.com/library?page=1&skillArea=47&questionId=75834
- https://github.com/liweinan/TestDomeHttpServerExample

The provided Node.js code sets up two HTTP servers: one on port 4513 (for API handling) and one on port 4514 (for web handling). However, the code contains syntax issues (e.g., missing closing braces `}`, semicolons `;`, and likely a typo where `reg` should be `req` for the request object). For analysis, I'll assume the intended corrected structure is as follows (with fixes for readability and functionality):

```javascript
let http = require("http");

let commonResponse = function(response) {
  response.writeHead(200, { "Content-Type": "text/html" });
  response.write("Request Completed");
};

let handleApi = function(req, res) {
  if (req.method == "POST") {
    commonResponse(res);
    res.end();
  }
  // Note: No handling for non-POST requests
};

let handleWeb = function(req, res) {
  commonResponse(res);
  res.end();
};

http.createServer(handleApi).listen(4513);
http.createServer(handleWeb).listen(4514);
```

- The `commonResponse` function sets a 200 status code and writes "Request Completed" to the response body.
- The API server (port 4513) only responds to POST requests; other methods (e.g., GET) are ignored, leading to hanging requests.
- The web server (port 4514) responds to all request methods with the common response.

Now, evaluating each statement:

1. **The handleWeb callback will write "Request Completed" to the response on HTTP POST, PUT, and GET requests.**  
   **Correct.** The `handleWeb` function (on port 4514) unconditionally calls `commonResponse(res)` followed by `res.end()`, regardless of the HTTP method. This means it will write the header and "Request Completed" for POST, PUT, GET, or any other method.

2. **Navigating the browser to port 4513 will return HTTP status code 200.**  
   **Incorrect.** Browsing to port 4513 typically sends a GET request. The `handleApi` function only processes POST requests (calling `commonResponse` and `res.end()`). For GET, nothing happens—no headers are set, no body is written, and `res.end()` isn't called. The request will hang and eventually time out (e.g., with a 504 or no response), not return 200.

3. **A call to res.end() is recommended but not required inside each createServer callback.**  
   **Incorrect.** In Node.js HTTP servers, calling `res.end()` (or equivalent like `res.send()`) is required to complete the response. Without it, the connection remains open, causing the request to hang indefinitely until timeout. It's not just "recommended"—it's essential for proper server behavior. In `handleApi`, non-POST requests demonstrate this issue.

4. **The handleApi callback will write "Request Completed" to the response for an HTTP POST request.**  
   **Correct.** For POST requests on port 4513, the `if` condition triggers `commonResponse(res)`, which writes the 200 header and "Request Completed", followed by `res.end()` to send the response.

5. **Inside the handleWeb callback, it is possible to get a query string of the HTTP request.**  
   **Correct.** The callback receives the `req` object, which includes `req.url` (containing the path and query string). You can parse the query string using Node's built-in `url` module (e.g., `const url = require('url'); const query = url.parse(req.url, true).query;`). The code doesn't do this currently, but it's possible to add such logic inside the function.