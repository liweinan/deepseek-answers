# XSS跨域问题与正确防护方法

## XSS跨域问题概述

XSS（跨站脚本攻击）与跨域问题密切相关，主要体现在以下几个方面：

1. **恶意脚本跨域执行**：攻击者注入的脚本可以在受害者的浏览器中跨域运行
2. **跨域数据窃取**：通过XSS可以窃取不同源的敏感数据
3. **跨域请求伪造**：利用XSS发起跨域请求，执行未授权的操作

## 正确的防护设置方法

### 1. 内容安全策略 (CSP)

```http
Content-Security-Policy: 
  default-src 'self';
  script-src 'self' 'unsafe-inline' 'unsafe-eval';
  connect-src 'self';
  img-src 'self' data:;
  style-src 'self' 'unsafe-inline';
  frame-ancestors 'none';
```

**关键配置**：
- 限制脚本只能从同源加载 (`'self'`)
- 禁止内联脚本 (`'unsafe-inline'`)
- 禁用动态代码执行 (`'unsafe-eval'`)
- 限制资源加载源

### 2. 跨域资源共享 (CORS) 正确配置

```http
Access-Control-Allow-Origin: https://trusted-domain.com
Access-Control-Allow-Methods: GET, POST
Access-Control-Allow-Headers: Content-Type
Access-Control-Allow-Credentials: false  # 除非必要，否则保持false
```

### 3. 输入输出处理

**输入验证**：
```javascript
// 使用正则表达式过滤特殊字符
function sanitizeInput(input) {
  return input.replace(/[<>"'&]/g, '');
}
```

**输出编码**：
```javascript
// HTML实体编码
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

### 4. Cookie安全设置

```http
Set-Cookie: 
  sessionid=abc123; 
  HttpOnly; 
  Secure; 
  SameSite=Strict;
  Path=/;
  Domain=example.com
```

### 5. 现代前端框架的安全实践

**React**：
```jsx
// React自动转义XSS
<div>{userContent}</div>

// 危险情况需要明确使用dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{__html: sanitizedContent}} />
```

**Vue**：
```html
<!-- Vue默认转义 -->
<div v-html="sanitizedContent"></div>
```

## 进阶防护措施

1. **子资源完整性 (SRI)**
```html
<script 
  src="https://example.com/script.js"
  integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC"
  crossorigin="anonymous">
</script>
```

2. **X-XSS-Protection头**（传统浏览器）
```http
X-XSS-Protection: 1; mode=block
```

3. **X-Frame-Options防止点击劫持**
```http
X-Frame-Options: DENY
```

## 开发注意事项

1. 永远不要信任客户端数据
2. 使用专业库处理XSS：
    - DOMPurify
    - sanitize-html
    - xss-filters
3. 定期安全审计和渗透测试
4. 保持所有依赖库更新

正确实施这些措施可以显著降低XSS和跨域攻击的风险，构建更安全的Web应用。

---

安全配置需要在**多个层面**协同实施，具体分布如下：

---

### **1. 服务端配置（必须）**
**主要责任**：设置安全HTTP头、输入验证、输出编码
- **配置位置**：
    - Web服务器（Nginx/Apache）
    - 应用框架（Node.js/Spring/Django等）

**关键配置**：
```nginx
# Nginx示例（部分配置）
add_header Content-Security-Policy "default-src 'self'";
add_header X-Frame-Options "DENY";
add_header X-Content-Type-Options "nosniff";
```

```javascript
// Node.js中间件示例
app.use(helmet()); // 使用helmet自动设置安全头
```

---

### **2. 浏览器端（辅助）**
**主要责任**：遵守服务端的安全策略、执行内置防护
- **自动生效**：
    - 解析CSP、CORS等HTTP头
    - 根据`HttpOnly`限制Cookie访问
    - 根据`SameSite`限制Cookie发送

- **开发者需注意**：
  ```javascript
  // 正确使用API（前端也需要配合）
  fetch(url, { 
    credentials: 'same-origin' // 避免意外跨域带Cookie
  });
  ```

---

### **3. 客户端代码（必须配合）**
**主要责任**：安全的数据处理和DOM操作
- **安全实践**：
  ```javascript
  // 避免危险操作
  element.innerHTML = userInput; // ❌ 危险
  element.textContent = userInput; // ✅ 安全

  // 使用专业库
  import DOMPurify from 'dompurify';
  element.innerHTML = DOMPurify.sanitize(userInput);
  ```

---

### **各层级的配置分工**
| 安全措施            | 服务端 | 浏览器 | 客户端代码 |
|---------------------|--------|--------|------------|
| CSP头               | ✅     | 执行   | -          |
| CORS头              | ✅     | 执行   | -          |
| Cookie安全属性      | ✅     | 执行   | -          |
| 输入验证            | ✅     | -      | 可选       |
| 输出编码            | ✅     | -      | ✅         |
| DOM操作安全         | -      | -      | ✅         |
| 框架安全特性        | -      | -      | ✅         |

---

### **最佳实践流程**
1. **服务端**：设置严格的安全HTTP头（CSP/CORS等）
2. **服务端**：对所有输入进行验证和过滤
3. **服务端**：对输出进行上下文相关编码
4. **客户端**：避免使用`innerHTML`等危险API
5. **客户端**：使用`textContent`或消毒库处理动态内容
6. **浏览器**：自动强制执行服务端的安全策略

**示例**：防御存储型XSS的完整流程
```
用户输入 → 服务端输入验证 → 数据库存储 → 
服务端输出编码 → 客户端用textContent渲染 → 
浏览器根据CSP阻止违规加载
```

所有层级必须协同工作才能提供全面防护，其中**服务端配置是基础防线**，客户端和浏览器是必要的补充。

---

以下是一个完整的跨域安全配置示例，涵盖服务端、客户端和浏览器三端的协同配置：

---

### **1. 服务端配置 (Node.js + Express 示例)**
```javascript
const express = require('express');
const helmet = require('helmet');
const cookieParser = require('cookie-parser');
const DOMPurify = require('dompurify');
const { JSDOM } = require('jsdom');
const dompurify = DOMPurify(new JSDOM('').window);

const app = express();

// 1. 安全HTTP头设置
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

// 2. CORS配置
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', 'https://trusted-client.com');
  res.header('Access-Control-Allow-Methods', 'GET,POST');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  res.header('Access-Control-Allow-Credentials', 'false');
  next();
});

// 3. Cookie安全设置
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

// 4. 输入消毒中间件
app.use(express.json({
  verify: (req, res, buf) => {
    try {
      JSON.parse(buf.toString());
    } catch (e) {
      throw new Error('Invalid JSON');
    }
  },
  limit: '10kb' // 防止过大JSON攻击
}));

// 5. 输出处理示例
app.get('/comments', (req, res) => {
  const rawComments = getCommentsFromDB(); 
  
  // 消毒后再发送
  const safeComments = rawComments.map(comment => ({
    ...comment,
    content: dompurify.sanitize(comment.content)
  }));
  
  res.json(safeComments);
});
```

---

### **2. 客户端代码 (React 示例)**
```jsx
import React, { useState, useEffect } from 'react';
import DOMPurify from 'dompurify';

function CommentSection() {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');

  // 1. 安全获取数据
  useEffect(() => {
    fetch('https://api.example.com/comments', {
      credentials: 'same-origin', // 配合Cookie策略
      headers: { 'Content-Type': 'application/json' }
    })
      .then(res => res.json())
      .then(data => setComments(data));
  }, []);

  // 2. 安全提交数据
  const handleSubmit = () => {
    // 前端验证
    if (!newComment.trim()) return;
    
    fetch('https://api.example.com/comments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        content: newComment.substring(0, 1000) // 长度限制
      })
    });
  };

  // 3. 安全渲染
  return (
    <div>
      {/* 安全输入框 */}
      <textarea 
        value={newComment}
        onChange={(e) => setNewComment(e.target.value)}
        maxLength="1000"
      />
      
      {/* 安全渲染评论 */}
      {comments.map(comment => (
        <div key={comment.id}>
          {/* 使用React默认转义 */}
          <p>{comment.author}</p>
          
          {/* 需要渲染HTML时消毒 */}
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

### **3. 浏览器/HTML 配置**
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <!-- 1. 禁用旧版浏览器不安全的默认行为 -->
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  
  <!-- 2. 启用现代浏览器安全特性 -->
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'">
  
  <!-- 3. 子资源完整性检查 -->
  <script 
    src="https://cdn.example.com/react.production.min.js"
    integrity="sha384-4z8Mj7h3A5XFAK4XwcmkX4j5/EN25i/L3Z5+OFD9z5F5F5F5F5F5F5F5F5F5F5F5"
    crossorigin="anonymous">
  </script>
</head>
<body>
  <div id="root"></div>
  
  <!-- 4. 安全加载脚本 -->
  <script type="module" src="/static/js/main.js"></script>
  
  <!-- 5. 禁止iframe嵌套 -->
  <script>
    if (window !== window.top) {
      window.top.location = window.location;
    }
  </script>
</body>
</html>
```

---

### **4. Web服务器配置 (Nginx 示例)**
```nginx
server {
    listen 443 ssl;
    server_name example.com;
    
    # TLS配置
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # 安全头 (补充应用层的设置)
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # 静态资源缓存策略
    location /static/ {
        add_header Cache-Control "public, max-age=31536000, immutable";
    }
    
    # API路由禁用缓存
    location /api/ {
        add_header Cache-Control "no-store";
        proxy_pass http://backend;
    }
    
    # 禁止敏感文件访问
    location ~* \.(env|git|htaccess)$ {
        deny all;
    }
}
```

---

### **各端协同防护矩阵**
| 攻击类型       | 服务端防护                          | 客户端防护                          | 浏览器防护               |
|----------------|-----------------------------------|-----------------------------------|-------------------------|
| **存储型XSS**  | 输入消毒 + CSP                    | 避免innerHTML + 内容消毒           | CSP执行 + XSS过滤器      |
| **反射型XSS**  | 输出编码                          | URL参数验证                        | X-XSS-Protection头       |
| **DOM型XSS**   | -                                 | 使用textContent代替innerHTML       | 现代框架自动转义          |
| **CSRF**       | SameSite Cookie + CSRF Token      | 自动携带Token                      | 遵循Cookie策略           |
| **点击劫持**   | X-Frame-Options头                 | frame busting脚本                  | 强制执行frame策略         |
| **数据泄露**   | CORS严格配置                      | 安全fetch配置                      | 同源策略强制执行          |

这个完整示例展示了如何通过多端协作构建深度防御体系。实际应用中需根据具体技术栈调整实现方式，但核心安全原则保持一致。

---

如果服务端不配置跨域相关的HTTP头（如`Access-Control-Allow-Origin`等），浏览器会根据**同源策略（Same-Origin Policy）**严格限制跨域请求，具体表现如下：

---

### **1. 简单请求（Simple Requests）**
**典型场景**：普通GET/POST请求，Content-Type为`text/plain`、`multipart/form-data`或`application/x-www-form-urlencoded`  
**结果**：
- 请求能到达服务端，服务端会正常处理并返回响应
- **但浏览器会拦截响应**，拒绝将结果返回给前端JavaScript代码
- 控制台报错：
  ```bash
  Access to fetch at 'http://api.example.com/data' from origin 'http://client.com' 
  has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
  ```

---

### **2. 预检请求（Preflight Requests）**
**典型场景**：自定义请求头、PUT/DELETE方法、`application/json`等Content-Type  
**结果**：
- 浏览器先发送`OPTIONS`预检请求
- 因服务端未返回正确的CORS头，预检**直接失败**
- 控制台报错：
  ```bash
  Access to fetch at 'http://api.example.com/data' from origin 'http://client.com' 
  has been blocked by CORS policy: Response to preflight request doesn't pass access control check: 
  No 'Access-Control-Allow-Origin' header is present on the requested resource.
  ```
- **实际请求不会发送到服务端**

---

### **3. 例外情况**
即使没有CORS头，以下情况仍能跨域：
| 场景                | 原理                                                                 |
|---------------------|----------------------------------------------------------------------|
| **JSONP**           | 通过`<script>`标签加载（已淘汰，存在安全隐患）                       |
| **图片/音视频资源** | `<img>`, `<video>`等标签默认允许跨域加载（但JavaScript不能读取内容） |
| **服务器代理**       | 通过同源的后端服务中转请求                                           |
| **浏览器插件**       | 插件可能不受同源策略限制（如Postman）                                |

---

### **4. 潜在风险**
如果强制绕过限制（如关闭浏览器安全设置或使用非浏览器工具）：
1. **请求能正常完成**：服务端无法仅靠不配置CORS来阻止攻击
2. **CSRF风险**：恶意网站可能利用用户已登录的状态发起请求（需配合`SameSite Cookie`等其他防护）

---

### **正确解决方案**
应在服务端**按需配置**CORS，而非完全禁用：
```javascript
// Express示例（最小安全配置）
app.use((req, res, next) => {
  // 明确指定允许的源，而非使用 '*'
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

### **各场景总结**
| 请求类型       | 服务端无CORS头时表现           | 解决方案                          |
|----------------|-------------------------------|-----------------------------------|
| 简单请求       | 浏览器拦截响应                | 配置`Access-Control-Allow-Origin` |
| 预检请求       | 浏览器阻止请求发送            | 正确响应`OPTIONS`请求             |
| 需要带Cookie   | 完全无法跨域                  | 添加`Access-Control-Allow-Credentials: true` |
| 非浏览器环境   | 请求正常完成（如cURL、Postman）| 服务端仍需自主验证权限            |

**核心原则**：CORS是浏览器的安全机制，而非服务端的访问控制。服务端应同时实施：
1. **身份验证**（如JWT）
2. **权限检查**
3. **CSRF防护**（如SameSite Cookie）
4. **输入验证**

---

如果前端不主动处理跨域问题（即不配置任何跨域相关的代码或设置），浏览器会根据**同源策略（Same-Origin Policy）**严格限制跨域请求，具体表现如下：

---

### **1. 请求表现**
#### **场景1：前端直接发起跨域请求**
```javascript
// 前端代码（未做任何跨域处理）
fetch('https://api.other-domain.com/data')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error(error));
```
**结果**：
- **浏览器控制台报错**：
  ```bash
  Access to fetch at 'https://api.other-domain.com/data' from origin 'https://your-site.com' 
  has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
  ```
- **请求可能到达服务端**（查看服务端日志可见请求），但浏览器会拦截响应，前端代码无法读取响应内容。

#### **场景2：跨域资源加载（如字体、图片）**
```html
<!-- 尝试加载跨域字体 -->
<style>
  @font-face {
    font-family: 'CustomFont';
    src: url('https://other-domain.com/font.woff2');
  }
</style>
```
**结果**：
- 字体/图片可能**加载失败**（取决于资源类型和服务端配置）
- 控制台报错：
  ```bash
  Access to font at 'https://other-domain.com/font.woff2' from origin 'https://your-site.com' 
  has been blocked by CORS policy.
  ```

---

### **2. 根本原因**
浏览器会**主动拦截**跨域请求的响应，除非满足以下条件之一：
1. 服务端返回正确的CORS头（如`Access-Control-Allow-Origin`）
2. 请求属于**同源**（协议+域名+端口完全一致）
3. 使用豁免规则（如`<img>`、`<script>`标签的部分场景）

---

### **3. 特殊情况与例外**
#### **不受跨域限制的场景**
| 场景                | 原因                                                                 |
|---------------------|----------------------------------------------------------------------|
| **`<img>` 标签**    | 可以加载跨域图片（但JavaScript无法通过`canvas`读取内容）             |
| **`<script>` 标签** | 可以加载跨域JS（需服务端不返回`X-Content-Type-Options: nosniff`）    |
| **`<link>` 标签**   | 可以加载跨域CSS（但可能无法使用其中的字体资源）                      |
| **JSONP**           | 通过`<script>`标签绕过限制（已淘汰，存在安全隐患）                  |

#### **可能“看似成功”但实际受限的情况**
1. **表单提交**：
   ```html
   <form action="https://api.other-domain.com/submit" method="POST">
     <input type="text" name="data">
     <button type="submit">提交</button>
   </form>
   ```
    - **表现**：请求能发送到服务端，但前端无法读取响应内容。

2. **服务端代理**：
    - 前端请求同源的服务端接口，由服务端中转请求到目标域（此时浏览器看到的是同源请求）。

---

### **4. 前端主动解决方案**
如果服务端无法修改（如第三方API），前端可采取以下**合法**手段：
#### **方案1：配置代理服务器**
```nginx
# Nginx代理配置示例
location /api/ {
  proxy_pass https://api.other-domain.com/;
  proxy_set_header Host api.other-domain.com;
}
```
前端只需请求同源URL（如`/api/data`），由Nginx转发。

#### **方案2：浏览器开发模式临时禁用限制**
- **Chrome启动参数**（仅限开发调试）：
  ```bash
  chrome.exe --disable-web-security --user-data-dir=/tmp
  ```
  ⚠️ 生产环境绝对不可用！

#### **方案3：使用CORS中间件（开发时）**
```javascript
// 本地开发服务器配置（如webpack-dev-server）
devServer: {
  proxy: {
    '/api': 'https://api.other-domain.com'
  }
}
```

---

### **5. 错误做法与风险**
| 错误尝试                | 风险                                                                 |
|-------------------------|----------------------------------------------------------------------|
| **强制修改浏览器安全设置** | 用户浏览器不可控，且会暴露所有网站的安全风险                         |
| **使用`try-catch`绕过**  | 无法捕获CORS错误（浏览器根本不会将响应返回给代码）                   |
| **完全依赖JSONP**        | 仅支持GET请求，且可能引入XSS漏洞                                    |

---

### **总结**
- **如果前端不处理跨域**：浏览器会按同源策略拦截请求，开发者工具中可见请求被标记为`CORS error`。
- **合法解决方案**：
    1. 优先让服务端配置CORS头
    2. 次选使用同源代理
    3. 开发环境可配置工具链代理
- **绝不推荐**：在生产环境使用任何绕过浏览器安全机制的方法。

正确流程：  
**前端发现CORS问题 → 检查服务端配置 → 协商添加CORS头或改用代理方案**。

---

正确配置前端跨域请求需要**服务端和前端协同配合**，以下是具体方法和最佳实践：

---

### **一、服务端必须配置的响应头**
服务端需在响应中添加以下HTTP头（以Node.js为例）：
```javascript
// Express中间件示例
app.use((req, res, next) => {
  // 允许指定的源（不要用'*'，否则无法带Cookie）
  res.header('Access-Control-Allow-Origin', 'https://your-frontend.com'); 
  
  // 允许的HTTP方法
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  
  // 允许的请求头
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  // 允许携带Cookie（如果需要）
  res.header('Access-Control-Allow-Credentials', 'true');
  
  // 预检请求缓存时间（秒）
  res.header('Access-Control-Max-Age', '86400');
  
  // 对OPTIONS请求直接返回200
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  
  next();
});
```

---

### **二、前端正确发起跨域请求**
#### 1. 简单请求（Simple Request）
```javascript
fetch('https://api.example.com/data', {
  method: 'GET', // 或 POST（Content-Type为 application/x-www-form-urlencoded）
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  credentials: 'include' // 如果需要带Cookie
})
```

#### 2. 需预检的请求（Preflight Request）
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

#### 3. 带自定义头的请求
```javascript
fetch('https://api.example.com/data', {
  headers: {
    'X-Custom-Header': 'value',
    'Content-Type': 'application/json'
  }
});
```

---

### **三、不同场景的解决方案**
#### 场景1：控制第三方API（服务端可修改）
- 按上述方法配置服务端CORS头

#### 场景2：无法修改第三方API
**方案A：通过同源代理**
```nginx
# Nginx配置
location /api/ {
  proxy_pass https://api.other-domain.com/;
  proxy_set_header Host api.other-domain.com;
}
```
前端请求`/api/data` → Nginx转发到`https://api.other-domain.com/data`

**方案B：JSONP（仅限GET请求）**
```javascript
function handleResponse(data) {
  console.log(data);
}
const script = document.createElement('script');
script.src = 'https://api.example.com/data?callback=handleResponse';
document.body.appendChild(script);
```

---

### **四、安全注意事项**
1. **不要使用`Access-Control-Allow-Origin: *`**
    - 如果请求需要带Cookie或Authorization头，必须指定具体域名

2. **敏感接口额外保护**
    - 即使配置了CORS，仍需验证`Origin`头防止CSRF
   ```javascript
   // 服务端校验Origin示例
   const allowedOrigins = ['https://your-frontend.com'];
   if (!allowedOrigins.includes(req.headers.origin)) {
     return res.status(403).send('Forbidden');
   }
   ```

3. **生产环境禁用以下配置**
   ```javascript
   // 危险配置（绝对不要用）
   res.header('Access-Control-Allow-Origin', '*');
   res.header('Access-Control-Allow-Credentials', 'true'); // 与'*'冲突
   ```

---

### **五、常见问题排查**
| 问题现象 | 可能原因 | 解决方案 |
|---------|---------|---------|
| 预检请求失败 | 服务端未正确处理`OPTIONS`方法 | 添加OPTIONS路由 |
| 带Cookie请求被拒绝 | 未设置`credentials: 'include'` | 前后端同时配置 |
| 自定义头未生效 | 未在`Access-Control-Allow-Headers`中声明 | 服务端添加对应头 |

---

### **六、完整工作流程**
1. 浏览器发送实际请求（简单请求）或先发`OPTIONS`预检请求（复杂请求）
2. 服务端响应CORS头
3. 浏览器验证头信息，通过则解除限制
4. 前端收到响应数据

---

按照以上方法配置，既能保证安全性，又能实现合法的跨域请求。对于敏感操作（如修改数据），建议始终通过同源代理中转。