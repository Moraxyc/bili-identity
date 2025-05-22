# B站用户认证 API 文档

本接口提供一套基于 B站UID 和主被动验证码的身份验证机制，包括验证码生成、发送、验证及认证状态查询。

## 接口列表

---

### 1. `POST /api/auth/passive`

#### 接口描述

用于被动生成验证码

#### 请求参数

| 参数 | 类型 | 描述       |
| ---- | ---- | ---------- |
| uid  | str  | 用户的 UID |

#### 请求示例

```bash
curl -X POST http://localhost:8000/api/auth/passive \
  -H "Content-Type: application/json" \
  -d '{"uid": "12345678"}'
```

#### 响应示例

```json
{
  "code": "4821"
}
```

> 同时返回 `Set-Cookie: session_id=xxx` 用于会话标识。

---

### 2. `POST /api/auth/send`

#### 接口描述

用于主动发送验证码（通过站内私信发送，不建议作为首选验证方式，不排除B站对此有监控，发现有账号大批量私信陌生用户什么的）。

#### 请求参数

| 参数 | 类型 | 描述       |
| ---- | ---- | ---------- |
| uid  | str  | 用户的 UID |

#### 请求示例

```bash
curl -X POST http://localhost:8000/api/auth/send \
  -H "Content-Type: application/json" \
  -d '{"uid": "12345678"}'
```

#### 响应示例

```json
{
  "message": "验证码已发送"
}
```

> 同样会设置 `session_id` cookie。

---

### 3. `POST /api/auth/verify`

#### 接口描述

提交并验证验证码。

只用在主动验证的情况。

#### 请求参数

| 参数 | 类型 | 描述     |
| ---- | ---- | -------- |
| uid  | str  | 用户 UID |
| code | str  | 验证码   |

#### 请求示例

```bash
curl -X POST http://localhost:8000/api/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"uid": "12345678", "code": "482134"}'
```

#### 成功响应示例

```json
{
  "message": "验证成功"
}
```

#### 失败响应示例

```json
{
  "detail": "验证码错误或已过期"
}
```

---

### 4. `GET /api/auth/status`

#### 接口描述

用于查询当前用户的验证状态。需要用户已登录（携带 `session_id` cookie）。

#### 请求示例

```bash
curl -X GET http://localhost:8000/api/auth/status \
  --cookie "session_id=your-session-id"
```

#### 已验证响应

```json
{
  "message": "已认证"
}
```

#### 未登录或未验证响应

```json
{
  "detail": "未登录"
}
```

或

```json
{
  "detail": "用户尚未验证"
}
```

---

## 使用说明

两种验证都会在请求验证码时设置session！

### 主动验证

1. 用户首次访问页面时，请调用 `/api/auth/send` 发送验证码。
2. Bot发送验证码给对应uid的用户，可在私信页面看到。如果发现不存在，可能是B站限制了发送，可以尝试被动验证。
3. 用户通过其他方式（例如 网页）输入验证码后，调用 `/api/auth/verify` 进行验证。
4. 携带cookie的状态下通过 `/api/auth/status` 检查认证状态。

### 被动验证

1. 用户首次访问页面时，调用 `/api/auth/passive` 获取验证码。
2. 将返回的code通过私信发送给Bot进行验证。
3. 携带cookie的状态下通过 `/api/auth/status` 检查认证状态。
