# Bili Identity [WIP]

## 项目简介

**Bili Identity** 旨在为各类网站、社区、个人站点提供一个简易、可自托管的 Bilibili 账号身份认证兼容层。
本项目通过 B 站私信验证码的方式，间接验证用户 B 站身份，并对外以 OpenID Connect 接口提供标准认证服务。

**适用场景**：

- Bilibili 官方未提供 OAuth2/OpenID 的站点认证API访问权限
- 需要以低成本、开源自托管方式接入 B 站账号登录的第三方网站

## 文档

接口文档:

- [B站用户认证 API 文档](docs/auth_api.md)

## TODO

- [x] 基本Bilibili私信鉴权功能 主被动
- [x] JWT鉴权, JWK签名
- [ ] 对外暴露的OpenID API
  - [x] /.well-known/openid-{configuration,jwks}
  - [ ] /api/oidc/{auth,token,userinfo}
- [ ] 前端界面优化
- [ ] 部署文档（含 Docker/一键脚本）
- [ ] 日志与安全监控
- [ ] 配置界面优化（如支持 ENV 配置、可视化）
- [ ] 完善单元测试、集成测试
- [ ] 社区案例与常见问题文档

## 风险与免责声明

- 本项目为第三方开源项目，与 Bilibili 官方无任何关系。
- 仅用于学习交流、个人项目和非商业用途，请勿用于违法用途。
- 使用时请注意账号安全及隐私保护。
