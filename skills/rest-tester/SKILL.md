---
name: rest-tester
description: 生成符合REST Client规范的.http测试脚本，用于API接口测试
---

# REST Client .http 脚本编写指南

## 基本语法

### 请求格式
```http
### 请求描述（可选）
METHOD URL HTTP/1.1
Header1: value1
Header2: value2

{
    "body": "content"
}
```

### 请求分隔符
使用 `###` 分隔多个请求

## 变量系统

### 环境变量 (settings.json)
```json
"rest-client.environmentVariables": {
    "$shared": {
        "baseUrl": "api.example.com",
        "version": "v1"
    },
    "dev": {
        "host": "localhost:8080",
        "token": "dev-token"
    },
    "prod": {
        "host": "api.example.com",
        "token": "prod-token"
    }
}
```

### 文件变量
```http
@hostname = api.example.com
@port = 8080
@baseUrl = {{hostname}}:{{port}}
@contentType = application/json
@authToken = {{login.response.headers.Authorization}}
```

### 请求变量
```http
# @name login
POST {{baseUrl}}/login
Content-Type: application/json

{
    "username": "admin",
    "password": "123456"
}

###
@token = {{login.response.body.token}}
```

### 系统变量
- `{{$guid}}` - UUID
- `{{$timestamp}}` - 当前时间戳
- `{{$timestamp -1 d}}` - 1天前
- `{{$datetime iso8601}}` - ISO格式时间
- `{{$datetime rfc1123}}` - RFC1123格式时间  
- `{{$randomInt 1 100}}` - 随机整数
- `{{$processEnv PATH}}` - 环境变量
- `{{$dotenv DB_HOST}}` - .env文件变量

### 提示变量
```http
# @prompt username 用户名
# @prompt password 密码
POST {{baseUrl}}/login
Content-Type: {{contentType}}

{
    "username": "{{username}}",
    "password": "{{password}}"
}
```

## 认证方式

### Basic Auth
```http
Authorization: Basic admin:123456
# 或
Authorization: Basic YWRtaW46MTIzNDU2
```

### Digest Auth
```http
Authorization: Digest admin 123456
```

### Bearer Token
```http
Authorization: Bearer {{token}}
```

### AWS Signature
```http
Authorization: AWS <accessId> <accessKey> region:us-east-1 service:s3
```

## 请求体格式

### JSON
```http
Content-Type: application/json

{
    "name": "test",
    "age": {{$randomInt 18 60}}
}
```

### XML
```http
Content-Type: application/xml

<user>
    <name>test</name>
    <age>{{$randomInt 18 60}}</age>
</user>
```

### Form Data
```http
Content-Type: application/x-www-form-urlencoded

name=test
&age={{$randomInt 18 60}}
```

### Multipart/File Upload
```http
Content-Type: multipart/form-data; boundary=boundary

--boundary
Content-Disposition: form-data; name="file"; filename="test.txt"
Content-Type: text/plain

< ./test.txt
--boundary--
```

## 查询参数
```http
GET {{baseUrl}}/users
    ?page=1
    &pageSize=20
    &sort=-createdAt
```

## 请求设置
```http
# @name getUser
# @no-redirect  # 禁止重定向
# @no-cookie-jar  # 不保存cookies
# @note 生产环境请谨慎操作
GET {{baseUrl}}/users/{{userId}}
Authorization: Bearer {{token}}
```

## 完整示例

```http
@baseUrl = {{$processEnv API_URL}}
@contentType = application/json

### 1. 用户登录
# @name login
# @prompt username 用户名
# @prompt password 密码
POST {{baseUrl}}/auth/login
Content-Type: {{contentType}}

{
    "username": "{{username}}",
    "password": "{{password}}"
}

### 2. 获取用户信息
@authToken = {{login.response.body.token}}
@userId = {{login.response.body.userId}}

GET {{baseUrl}}/users/{{userId}}
Authorization: Bearer {{authToken}}

### 3. 创建文章
# @name createPost
POST {{baseUrl}}/posts
Authorization: Bearer {{authToken}}
Content-Type: {{contentType}}

{
    "title": "测试文章 {{$timestamp}}",
    "content": "这是文章内容",
    "tags": ["test", "api"]
}

### 4. 获取文章列表
GET {{baseUrl}}/posts
    ?page=1
    &pageSize=10
    &author={{userId}}
Authorization: Bearer {{authToken}}

### 5. 更新文章
@postId = {{createPost.response.body.id}}

PUT {{baseUrl}}/posts/{{postId}}
Authorization: Bearer {{authToken}}
Content-Type: {{contentType}}

{
    "title": "更新后的标题 {{$datetime iso8601}}",
    "content": "更新后的内容"
}
```