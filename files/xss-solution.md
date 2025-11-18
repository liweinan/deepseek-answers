# XSS Cross-Domain Issues and Correct Protection Methods

## XSS Cross-Domain Issues Overview

XSS (Cross-Site Scripting) attacks are closely related to cross-domain issues, mainly reflected in the following aspects:

1. **Malicious Script Cross-Domain Execution**: Scripts injected by attackers can run cross-domain in the victim's browser
2. **Cross-Domain Data Theft**: Sensitive data from different origins can be stolen through XSS
3. **Cross-Domain Request Forgery**: Using XSS to initiate cross-domain requests and execute unauthorized operations

## Correct Protection Configuration Methods

### 1. Content Security Policy (CSP)

```http
Content-Security-Policy: 
  default-src 'self';
  script-src 'self' 'unsafe-inline' 'unsafe-eval';
  connect-src 'self';
  img-src 'self' data:;
  style-src 'self' 'unsafe-inline';
  frame-ancestors 'none';
```

**Key Configuration**:
- Restrict scripts to load only from same origin (`'self'`)
- Prohibit inline scripts (`'unsafe-inline'`)
- Disable dynamic code execution (`'unsafe-eval'`)
- Restrict resource loading sources

### 2. Cross-Origin Resource Sharing (CORS) Correct Configuration

```http
Access-Control-Allow-Origin: https://trusted-domain.com
Access-Control-Allow-Methods: GET, POST
Access-Control-Allow-Headers: Content-Type
Access-Control-Allow-Credentials: false  # Keep false unless necessary
```

### 3. Input and Output Processing

**Input Validation**:
```javascript
// Use regular expressions to filter special characters
function sanitizeInput(input) {
  return input.replace(/[<>"'&]/g, '');
}
```

**Output Encoding**:
```javascript
// HTML entity encoding
function htmlEncode(str) {
  return str.replace(/[&<>'"]/g, 
    tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    }[tag]));
}
```

### 4. Cookie Security Settings

```http
Set-Cookie: 
  sessionid=abc123; 
  HttpOnly; 
  Secure; 
  SameSite=Strict;
  Path=/;
  Domain=example.com
```

### 5. Modern Frontend Framework Security Practices

**React**:
```jsx
// React automatically escapes XSS
<div>{userContent}</div>

// Dangerous cases require explicit use of dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{__html: sanitizedContent}} />
```

**Vue**:
```html
<!-- Vue defaults to escaping -->
<div v-html="sanitizedContent"></div>
```

## Advanced Protection Measures

1. **Subresource Integrity (SRI)**
```html
<script 
  src="https://example.com/script.js"
  integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC"
  crossorigin="anonymous">
</script>
```

2. **X-XSS-Protection Header** (Legacy browsers)
```http
X-XSS-Protection: 1; mode=block
```

3. **X-Frame-Options to Prevent Clickjacking**
```http
X-Frame-Options: DENY
```

## Development Considerations

1. Never trust client-side data
2. Use professional libraries to handle XSS:
    - DOMPurify
    - sanitize-html
    - xss-filters
3. Regular security audits and penetration testing
4. Keep all dependency libraries updated

Properly implementing these measures can significantly reduce the risk of XSS and cross-domain attacks, building more secure web applications.

---

Security configuration needs to be implemented **at multiple levels** in coordination, distributed as follows:

---

### **1. Server-Side Configuration (Required)**
**Primary Responsibility**: Set security HTTP headers, input validation, output encoding
- **Configuration Locations**:
    - Web servers (Nginx/Apache)
    - Application frameworks (Node.js/Spring/Django, etc.)

**Key Configuration**:
```nginx
# Nginx example (partial configuration)
add_header Content-Security-Policy "default-src 'self'";
add_header X-Frame-Options "DENY";
add_header X-Content-Type-Options "nosniff";
```

```javascript
// Node.js middleware example
app.use(helmet()); // Use helmet to automatically set security headers
```

---

### **2. Browser-Side (Auxiliary)**
**Primary Responsibility**: Comply with server security policies, execute built-in protection
- **Automatic Activation**:
    - Parse CSP, CORS and other HTTP headers
    - Restrict Cookie access based on `HttpOnly`
    - Restrict Cookie sending based on `SameSite`

- **Developers Should Note**:
  ```javascript
  // Correct API usage (frontend also needs to cooperate)
  fetch(url, { 
    credentials: 'same-origin' // Avoid accidentally sending cookies cross-domain
  });
  ```

---

### **3. Client-Side Code (Must Cooperate)**
**Primary Responsibility**: Secure data processing and DOM operations
- **Security Practices**:
  ```javascript
  // Avoid dangerous operations
  element.innerHTML = userInput; // ❌ Dangerous
  element.textContent = userInput; // ✅ Safe

  // Use professional libraries
  import DOMPurify from 'dompurify';
  element.innerHTML = DOMPurify.sanitize(userInput);
  ```

---

### **Configuration Division by Level**
| Security Measure            | Server | Browser | Client Code |
|---------------------|--------|--------|------------|
| CSP Header               | ✅     | Execute   | -          |
| CORS Header              | ✅     | Execute   | -          |
| Cookie Security Attributes      | ✅     | Execute   | -          |
| Input Validation            | ✅     | -      | Optional       |
| Output Encoding            | ✅     | -      | ✅         |
| DOM Operation Security         | -      | -      | ✅         |
| Framework Security Features        | -      | -      | ✅         |

---

### **Best Practice Workflow**
1. **Server**: Set strict security HTTP headers (CSP/CORS, etc.)
2. **Server**: Validate and filter all inputs
3. **Server**: Perform context-aware encoding on outputs
4. **Client**: Avoid using dangerous APIs like `innerHTML`
5. **Client**: Use `textContent` or sanitization libraries to handle dynamic content
6. **Browser**: Automatically enforce server security policies

**Example**: Complete workflow for defending against stored XSS
```
User Input → Server Input Validation → Database Storage → 
Server Output Encoding → Client Renders with textContent → 
Browser Blocks Violations Based on CSP
```

All levels must work together to provide comprehensive protection, with **server configuration as the foundational defense line**, and client and browser as necessary supplements.

---

Below is a complete cross-domain security configuration example covering server, client, and browser three-end coordination:

---

### **1. Server-Side Configuration (Node.js + Express Example)**
```javascript
const express = require('express');
const helmet = require('helmet');
const cookieParser = require('cookie-parser');
const DOMPurify = require('dompurify');
const { JSDOM } = require('jsdom');
const dompurify = DOMPurify(new JSDOM('').window);

const app = express();

// 1. Security HTTP header settings
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'", "trusted.cdn.com"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:"],
      connectSrc: ["'self'"],
      frameAncestors: ["'none'"]
    }
  },
  hsts: { maxAge: 31536000, includeSubDomains: true },
  frameguard: { action: 'deny' }
}));

// 2. CORS configuration
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', 'https://trusted-client.com');
  res.header('Access-Control-Allow-Methods', 'GET,POST');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  res.header('Access-Control-Allow-Credentials', 'false');
  next();
});

// 3. Cookie security settings
app.use(cookieParser());
app.use((req, res, next) => {
  res.cookie('sessionID', 'abc123', {
    httpOnly: true,
    secure: true,
    sameSite: 'strict',
    maxAge: 24 * 60 * 60 * 1000
  });
  next();
});

// 4. Input sanitization middleware
app.use(express.json({
  verify: (req, res, buf) => {
    try {
      JSON.parse(buf.toString());
    } catch (e) {
      throw new Error('Invalid JSON');
    }
  },
  limit: '10kb' // Prevent oversized JSON attacks
}));

// 5. Output processing example
app.get('/comments', (req, res) => {
  const rawComments = getCommentsFromDB(); 
  
  // Sanitize before sending
  const safeComments = rawComments.map(comment => ({
    ...comment,
    content: dompurify.sanitize(comment.content)
  }));
  
  res.json(safeComments);
});
```

---

### **2. Client-Side Code (React Example)**
```jsx
import React, { useState, useEffect } from 'react';
import DOMPurify from 'dompurify';

function CommentSection() {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');

  // 1. Secure data fetching
  useEffect(() => {
    fetch('https://api.example.com/comments', {
      credentials: 'same-origin', // Coordinate with Cookie policy
      headers: { 'Content-Type': 'application/json' }
    })
      .then(res => res.json())
      .then(data => setComments(data));
  }, []);

  // 2. Secure data submission
  const handleSubmit = () => {
    // Frontend validation
    if (!newComment.trim()) return;
    
    fetch('https://api.example.com/comments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        content: newComment.substring(0, 1000) // Length limit
      })
    });
  };

  // 3. Secure rendering
  return (
    <div>
      {/* Secure input field */}
      <textarea 
        value={newComment}
        onChange={(e) => setNewComment(e.target.value)}
        maxLength="1000"
      />
      
      {/* Secure comment rendering */}
      {comments.map(comment => (
        <div key={comment.id}>
          {/* Use React default escaping */}
          <p>{comment.author}</p>
          
          {/* Sanitize when HTML rendering is needed */}
          <div 
            dangerouslySetInnerHTML={{ 
              __html: DOMPurify.sanitize(comment.content) 
            }} 
          />
        </div>
      ))}
    </div>
  );
}
```

---

### **3. Browser/HTML Configuration**
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <!-- 1. Disable unsafe default behaviors in legacy browsers -->
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  
  <!-- 2. Enable modern browser security features -->
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'">
  
  <!-- 3. Subresource integrity check -->
  <script 
    src="https://cdn.example.com/react.production.min.js"
    integrity="sha384-4z8Mj7h3A5XFAK4XwcmkX4j5/EN25i/L3Z5+OFD9z5F5F5F5F5F5F5F5F5F5F5F5"
    crossorigin="anonymous">
  </script>
</head>
<body>
  <div id="root"></div>
  
  <!-- 4. Secure script loading -->
  <script type="module" src="/static/js/main.js"></script>
  
  <!-- 5. Prevent iframe embedding -->
  <script>
    if (window !== window.top) {
      window.top.location = window.location;
    }
  </script>
</body>
</html>
```

---

### **4. Web Server Configuration (Nginx Example)**
```nginx
server {
    listen 443 ssl;
    server_name example.com;
    
    # TLS configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # Security headers (supplement application layer settings)
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # Static resource caching strategy
    location /static/ {
        add_header Cache-Control "public, max-age=31536000, immutable";
    }
    
    # API routes disable caching
    location /api/ {
        add_header Cache-Control "no-store";
        proxy_pass http://backend;
    }
    
    # Deny access to sensitive files
    location ~* \.(env|git|htaccess)$ {
        deny all;
    }
}
```

---

### **Multi-End Collaborative Protection Matrix**
| Attack Type       | Server-Side Protection                          | Client-Side Protection                          | Browser Protection               |
|----------------|-----------------------------------|-----------------------------------|-------------------------|
| **Stored XSS**  | Input sanitization + CSP                    | Avoid innerHTML + content sanitization           | CSP enforcement + XSS filter      |
| **Reflected XSS**  | Output encoding                          | URL parameter validation                        | X-XSS-Protection header       |
| **DOM-based XSS**   | -                                 | Use textContent instead of innerHTML       | Modern framework auto-escaping          |
| **CSRF**       | SameSite Cookie + CSRF Token      | Automatically carry Token                      | Follow Cookie policy           |
| **Clickjacking**   | X-Frame-Options header                 | Frame busting script                  | Enforce frame policy         |
| **Data Leakage**   | CORS strict configuration                      | Secure fetch configuration                      | Same-origin policy enforcement          |

This complete example demonstrates how to build a defense-in-depth system through multi-end collaboration. In actual applications, implementation methods need to be adjusted according to specific technology stacks, but core security principles remain consistent.

---

If the server does not configure cross-domain related HTTP headers (such as `Access-Control-Allow-Origin`, etc.), the browser will strictly restrict cross-domain requests according to the **Same-Origin Policy**, with the following specific behaviors:

---

### **1. Simple Requests**
**Typical Scenario**: Regular GET/POST requests with Content-Type of `text/plain`, `multipart/form-data`, or `application/x-www-form-urlencoded`  
**Result**:
- The request can reach the server, and the server will process and return a response normally
- **But the browser will intercept the response**, refusing to return the result to frontend JavaScript code
- Console error:
  ```bash
  Access to fetch at 'http://api.example.com/data' from origin 'http://client.com' 
  has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
  ```

---

### **2. Preflight Requests**
**Typical Scenario**: Custom request headers, PUT/DELETE methods, `application/json` Content-Type, etc.  
**Result**:
- Browser first sends an `OPTIONS` preflight request
- Because the server does not return correct CORS headers, the preflight **fails directly**
- Console error:
  ```bash
  Access to fetch at 'http://api.example.com/data' from origin 'http://client.com' 
  has been blocked by CORS policy: Response to preflight request doesn't pass access control check: 
  No 'Access-Control-Allow-Origin' header is present on the requested resource.
  ```
- **The actual request will not be sent to the server**

---

### **3. Exception Cases**
Even without CORS headers, the following cases can still cross domains:
| Scenario                | Principle                                                                 |
|---------------------|----------------------------------------------------------------------|
| **JSONP**           | Load via `<script>` tag (deprecated, security risks)                       |
| **Image/Audio/Video Resources** | `<img>`, `<video>` and other tags allow cross-domain loading by default (but JavaScript cannot read content) |
| **Server Proxy**       | Forward requests through same-origin backend service                                           |
| **Browser Extensions**       | Extensions may not be restricted by same-origin policy (e.g., Postman)                                |

---

### **4. Potential Risks**
If restrictions are forcibly bypassed (such as disabling browser security settings or using non-browser tools):
1. **Request can complete normally**: The server cannot prevent attacks solely by not configuring CORS
2. **CSRF Risk**: Malicious websites may exploit logged-in user state to initiate requests (requires other protections like `SameSite Cookie`)

---

### **Correct Solution**
Should configure CORS on the server **as needed**, rather than completely disabling it:
```javascript
// Express example (minimal security configuration)
app.use((req, res, next) => {
  // Explicitly specify allowed origins, not using '*'
  const allowedOrigins = ['https://trusted-client.com'];
  const origin = req.headers.origin;
  
  if (allowedOrigins.includes(origin)) {
    res.header('Access-Control-Allow-Origin', origin);
    res.header('Access-Control-Allow-Methods', 'GET,POST');
    res.header('Access-Control-Allow-Headers', 'Content-Type');
  }
  next();
});
```

---

### **Summary by Scenario**
| Request Type       | Behavior When Server Has No CORS Headers           | Solution                          |
|----------------|-------------------------------|-----------------------------------|
| Simple Request       | Browser intercepts response                | Configure `Access-Control-Allow-Origin` |
| Preflight Request       | Browser prevents request from being sent            | Properly respond to `OPTIONS` request             |
| Requires Cookies   | Completely unable to cross domain                  | Add `Access-Control-Allow-Credentials: true` |
| Non-browser Environment   | Request completes normally (e.g., cURL, Postman)| Server still needs to verify permissions independently            |

**Core Principle**: CORS is a browser security mechanism, not server access control. The server should also implement:
1. **Authentication** (e.g., JWT)
2. **Permission Checks**
3. **CSRF Protection** (e.g., SameSite Cookie)
4. **Input Validation**

---

If the frontend does not actively handle cross-domain issues (i.e., does not configure any cross-domain related code or settings), the browser will strictly restrict cross-domain requests according to the **Same-Origin Policy**, with the following specific behaviors:

---

### **1. Request Behavior**
#### **Scenario 1: Frontend Directly Initiates Cross-Domain Request**
```javascript
// Frontend code (no cross-domain handling)
fetch('https://api.other-domain.com/data')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error(error));
```
**Result**:
- **Browser console error**:
  ```bash
  Access to fetch at 'https://api.other-domain.com/data' from origin 'https://your-site.com' 
  has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
  ```
- **Request may reach the server** (visible in server logs), but the browser will intercept the response, and frontend code cannot read the response content.

#### **Scenario 2: Cross-Domain Resource Loading (e.g., fonts, images)**
```html
<!-- Attempt to load cross-domain font -->
<style>
  @font-face {
    font-family: 'CustomFont';
    src: url('https://other-domain.com/font.woff2');
  }
</style>
```
**Result**:
- Font/image may **fail to load** (depending on resource type and server configuration)
- Console error:
  ```bash
  Access to font at 'https://other-domain.com/font.woff2' from origin 'https://your-site.com' 
  has been blocked by CORS policy.
  ```

---

### **2. Root Cause**
The browser will **actively intercept** cross-domain request responses unless one of the following conditions is met:
1. Server returns correct CORS headers (e.g., `Access-Control-Allow-Origin`)
2. Request is **same-origin** (protocol + domain + port exactly match)
3. Uses exemption rules (e.g., some scenarios with `<img>`, `<script>` tags)

---

### **3. Special Cases and Exceptions**
#### **Scenarios Not Restricted by Cross-Domain**
| Scenario                | Reason                                                                 |
|---------------------|----------------------------------------------------------------------|
| **`<img>` Tag**    | Can load cross-domain images (but JavaScript cannot read content via `canvas`)             |
| **`<script>` Tag** | Can load cross-domain JS (requires server not to return `X-Content-Type-Options: nosniff`)    |
| **`<link>` Tag**   | Can load cross-domain CSS (but may not be able to use fonts within)                      |
| **JSONP**           | Bypass restrictions via `<script>` tag (deprecated, security risks)                  |

#### **Cases That May "Appear Successful" But Are Actually Restricted**
1. **Form Submission**:
   ```html
   <form action="https://api.other-domain.com/submit" method="POST">
     <input type="text" name="data">
     <button type="submit">Submit</button>
   </form>
   ```
    - **Behavior**: Request can be sent to the server, but frontend cannot read response content.

2. **Server Proxy**:
    - Frontend requests same-origin server interface, server forwards request to target domain (browser sees this as same-origin request).

---

### **4. Frontend Active Solutions**
If the server cannot be modified (e.g., third-party API), the frontend can take the following **legal** approaches:
#### **Solution 1: Configure Proxy Server**
```nginx
# Nginx proxy configuration example
location /api/ {
  proxy_pass https://api.other-domain.com/;
  proxy_set_header Host api.other-domain.com;
}
```
Frontend only needs to request same-origin URL (e.g., `/api/data`), forwarded by Nginx.

#### **Solution 2: Temporarily Disable Restrictions in Browser Development Mode**
- **Chrome startup parameters** (development/debugging only):
  ```bash
  chrome.exe --disable-web-security --user-data-dir=/tmp
  ```
  ⚠️ Absolutely not for production!

#### **Solution 3: Use CORS Middleware (During Development)**
```javascript
// Local development server configuration (e.g., webpack-dev-server)
devServer: {
  proxy: {
    '/api': 'https://api.other-domain.com'
  }
}
```

---

### **5. Wrong Approaches and Risks**
| Wrong Attempt                | Risk                                                                 |
|-------------------------|----------------------------------------------------------------------|
| **Force Modify Browser Security Settings** | User browsers are uncontrollable and will expose security risks for all websites                         |
| **Use `try-catch` to Bypass**  | Cannot catch CORS errors (browser doesn't return response to code at all)                   |
| **Completely Rely on JSONP**        | Only supports GET requests and may introduce XSS vulnerabilities                                    |

---

### **Summary**
- **If frontend doesn't handle cross-domain**: Browser will intercept requests according to same-origin policy, visible in developer tools as `CORS error`.
- **Legal Solutions**:
    1. Priority: Have server configure CORS headers
    2. Alternative: Use same-origin proxy
    3. Development environment: Configure toolchain proxy
- **Never Recommended**: Use any method to bypass browser security mechanisms in production.

Correct Process:  
**Frontend discovers CORS issue → Check server configuration → Negotiate adding CORS headers or switch to proxy solution**.

---

Correctly configuring frontend cross-domain requests requires **server and frontend coordination**, below are specific methods and best practices:

---

### **I. Response Headers Server Must Configure**
The server needs to add the following HTTP headers in responses (Node.js example):
```javascript
// Express middleware example
app.use((req, res, next) => {
  // Allow specified origin (don't use '*', otherwise cannot send cookies)
  res.header('Access-Control-Allow-Origin', 'https://your-frontend.com'); 
  
  // Allowed HTTP methods
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  
  // Allowed request headers
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  // Allow sending cookies (if needed)
  res.header('Access-Control-Allow-Credentials', 'true');
  
  // Preflight request cache time (seconds)
  res.header('Access-Control-Max-Age', '86400');
  
  // Return 200 directly for OPTIONS requests
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  
  next();
});
```

---

### **II. Frontend Correctly Initiates Cross-Domain Requests**
#### 1. Simple Request
```javascript
fetch('https://api.example.com/data', {
  method: 'GET', // or POST (Content-Type is application/x-www-form-urlencoded)
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  credentials: 'include' // if cookies are needed
})
```

#### 2. Preflight Request
```javascript
fetch('https://api.example.com/data', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer token123'
  },
  body: JSON.stringify({ key: 'value' }),
  credentials: 'include'
});
```

#### 3. Request with Custom Headers
```javascript
fetch('https://api.example.com/data', {
  headers: {
    'X-Custom-Header': 'value',
    'Content-Type': 'application/json'
  }
});
```

---

### **III. Solutions for Different Scenarios**
#### Scenario 1: Control Third-Party API (Server Can Be Modified)
- Configure server CORS headers as described above

#### Scenario 2: Cannot Modify Third-Party API
**Solution A: Through Same-Origin Proxy**
```nginx
# Nginx configuration
location /api/ {
  proxy_pass https://api.other-domain.com/;
  proxy_set_header Host api.other-domain.com;
}
```
Frontend requests `/api/data` → Nginx forwards to `https://api.other-domain.com/data`

**Solution B: JSONP (GET requests only)**
```javascript
function handleResponse(data) {
  console.log(data);
}
const script = document.createElement('script');
script.src = 'https://api.example.com/data?callback=handleResponse';
document.body.appendChild(script);
```

---

### **IV. Security Considerations**
1. **Don't use `Access-Control-Allow-Origin: *`**
    - If requests need to send cookies or Authorization headers, must specify specific domain

2. **Additional Protection for Sensitive Interfaces**
    - Even with CORS configured, still need to verify `Origin` header to prevent CSRF
   ```javascript
   // Server Origin validation example
   const allowedOrigins = ['https://your-frontend.com'];
   if (!allowedOrigins.includes(req.headers.origin)) {
     return res.status(403).send('Forbidden');
   }
   ```

3. **Disable Following Configuration in Production**
   ```javascript
   // Dangerous configuration (absolutely don't use)
   res.header('Access-Control-Allow-Origin', '*');
   res.header('Access-Control-Allow-Credentials', 'true'); // Conflicts with '*'
   ```

---

### **V. Common Issue Troubleshooting**
| Issue | Possible Cause | Solution |
|---------|---------|---------|
| Preflight request fails | Server doesn't properly handle `OPTIONS` method | Add OPTIONS route |
| Cookie request rejected | `credentials: 'include'` not set | Configure both frontend and backend |
| Custom header not effective | Not declared in `Access-Control-Allow-Headers` | Server adds corresponding header |

---

### **VI. Complete Workflow**
1. Browser sends actual request (simple request) or first sends `OPTIONS` preflight request (complex request)
2. Server responds with CORS headers
3. Browser validates header information, removes restrictions if passed
4. Frontend receives response data

---

Following the above methods can ensure security while achieving legal cross-domain requests. For sensitive operations (such as modifying data), it's recommended to always use same-origin proxy forwarding.

---

# Comprehensive Protection Plan to Avoid Frontend XSS Injection

XSS (Cross-Site Scripting) attacks are one of the most common security threats in web applications. Below is a comprehensive defense strategy and practical methods:

## I. Basic Protection Measures

### 1. Input Validation and Filtering
```javascript
// Use regular expressions to filter dangerous characters
function sanitizeInput(input) {
  return input.replace(/[<>"'&\/]/g, '');
}

// Or use professional libraries
import DOMPurify from 'dompurify';
const clean = DOMPurify.sanitize(userInput);
```

### 2. Output Encoding
```javascript
// HTML entity encoding
function htmlEncode(str) {
  return str.replace(/[&<>'"]/g, 
    char => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    }[char]));
}
```

## II. Modern Framework Security Practices

### React Security Practices
```jsx
// Automatically escape content
<div>{userContent}</div> 

// Sanitize when HTML rendering is needed
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(htmlContent) }} />
```

### Vue Security Practices
```html
<!-- Automatic escaping -->
<div>{{ userContent }}</div>

<!-- Use v-html + sanitization when HTML rendering is needed -->
<div v-html="sanitizedHtml"></div>
```

## III. Content Security Policy (CSP)

### Configuration Example
```http
Content-Security-Policy: 
  default-src 'self';
  script-src 'self' 'unsafe-inline' 'unsafe-eval';
  style-src 'self' 'unsafe-inline'; 
  img-src 'self' data:;
  connect-src 'self';
  frame-ancestors 'none';
```

### Meta Tag Method
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; script-src 'self'">
```

## IV. Security HTTP Header Configuration

```http
X-XSS-Protection: 1; mode=block
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer-when-downgrade
```

## V. DOM Operation Security

### Dangerous Operations (Avoid Using)
```javascript
element.innerHTML = userInput;
document.write(userInput);
eval(userInput);
```

### Safe Alternatives
```javascript
element.textContent = userInput;
element.setAttribute('data-value', userInput);
```

## VI. Professional Protection Library Recommendations

1. **DOMPurify** - HTML sanitization
   ```bash
   npm install dompurify
   ```

2. **xss-filters** - General XSS filtering
   ```bash
   npm install xss-filters
   ```

3. **sanitize-html** - Rich text sanitization
   ```bash
   npm install sanitize-html
   ```

## VII. Advanced Protection Technologies

### 1. Subresource Integrity (SRI)
```html
<script src="https://example.com/script.js"
        integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC"
        crossorigin="anonymous"></script>
```

### 2. Trusted Types API (Chrome)
```javascript
// Server header
Content-Security-Policy: require-trusted-types-for 'script'

// Frontend configuration
if (window.trustedTypes) {
  const policy = trustedTypes.createPolicy('default', {
    createHTML: input => DOMPurify.sanitize(input)
  });
}
```

## VIII. Security Practices in Development Process

1. **Code Review**: Check all dynamic content rendering points
2. **Automated Scanning**: Use tools like OWASP ZAP
3. **Security Testing**: Regular penetration testing
4. **Dependency Updates**: Keep security library versions up to date

## IX. Common XSS Attack Scenario Defense

### 1. Stored XSS
- Sanitize all user input before storage
- Encode again on output

### 2. Reflected XSS
- Strictly validate URL parameters
- Implement CSP to restrict inline scripts

### 3. DOM-based XSS
- Avoid using `eval()`, `setTimeout(string)`, etc.
- Use `textContent` instead of `innerHTML`

By implementing the above multi-layered defense measures, XSS attack risks can be significantly reduced. Remember: **There is no single silver bullet solution**, security requires a defense-in-depth system.
