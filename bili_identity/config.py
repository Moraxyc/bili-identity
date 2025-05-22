import logging
import os
from functools import lru_cache
from typing import List, Literal, Optional

import yaml
from bilibili_api import Credential
from bilibili_api.session import Session
from pydantic import BaseModel, Field
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

logger = logging.getLogger(__name__)

yaml_ruamel = YAML()
yaml_ruamel.indent(mapping=2, sequence=4, offset=2)
yaml_ruamel.default_flow_style = False


class MissingCredentialError(Exception):
    pass


class AppConfig(BaseModel):
    allowed_hosts: List[str] = ["127.0.0.1"]
    base_url: str = "http://bili-id.example.org"


class ServerConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    workers: int = 2
    reload: bool = False
    cors_origins: List[str] = ["http://example.org"]


class DatabaseConfig(BaseModel):
    uri: str = "sqlite+aiosqlite:///bili_id.db"
    pool_size: int = 10


class RedisConfig(BaseModel):
    enable: bool = Field(
        default=False,
        description="是否使用redis作为session后端，如果不启用，则默认使用内存模式，重启清空",
    )
    uri: str = "redis://localhost"


class LogConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    file: str = "bili_id.log"


class SecurityConfig(BaseModel):
    secret_key: str = Field(
        default="请填写 secret_key",
        description="用于加密 JWT 的密钥，必须保密",
    )
    jwt_expire_seconds: int = Field(
        default=3600, description="JWT 有效时间（秒）"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT 加密算法")
    allowed_redirect_uris: List[str] = Field(
        default_factory=lambda: ["http://your-app.com/callback"],
        description="允许的回调地址列表",
    )
    session_ttl: int = Field(
        default=3600,
        description="B站验证成功的会话有效时间，延长可减少验证次数",
    )


class OIDCConfig(BaseModel):
    client_id: Optional[str] = Field(
        default=None, description="请填写 client_id"
    )
    client_secret: Optional[str] = Field(
        default=None, description="请填写 client_secret"
    )
    issuer: Optional[str] = Field(default=None, description="请填写 issuer")
    redirect_uris: List[str] = Field(
        default_factory=lambda: ["https://your-app.com/callback"]
    )
    scopes_supported: List[str] = Field(
        default_factory=lambda: ["openid", "profile"]
    )


class BiliConfig(BaseModel):
    sessdata: Optional[str] = Field(
        default=None, description="请填写 sessdata"
    )
    bili_jct: Optional[str] = Field(
        default=None, description="请填写 bili_jct"
    )
    buvid3: Optional[str] = Field(default=None, description="请填写 buvid3")
    dedeuserid: Optional[int] = Field(
        default=None, description="请填写 dedeuserid"
    )
    ac_time_value: Optional[str] = Field(
        default=None, description="可选：如果需要刷新cookie（不需要可留空）"
    )
    captcha_msg_template: str = "验证码：{code}，请在5分钟内完成验证"


class Settings(BaseModel):
    app: AppConfig = AppConfig()
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    log: LogConfig = LogConfig()
    server: ServerConfig = ServerConfig()
    security: SecurityConfig = SecurityConfig()
    bili: BiliConfig = BiliConfig()
    oidc: OIDCConfig = OIDCConfig()

    @property
    def credential(self) -> Credential:
        if all(
            [
                self.bili.sessdata,
                self.bili.bili_jct,
                self.bili.buvid3,
                self.bili.dedeuserid,
            ]
        ):
            return Credential(
                sessdata=self.bili.sessdata,
                bili_jct=self.bili.bili_jct,
                buvid3=self.bili.buvid3,
                dedeuserid=str(self.bili.dedeuserid),
                ac_time_value=self.bili.ac_time_value,
            )
        return DummyCredential()

    @property
    def session(self) -> Session:
        if not hasattr(self, "_session"):
            self._session = Session(self.credential)
        return self._session


class DummyCredential(Credential):
    def __init__(self):
        super().__init__(
            sessdata="",
            bili_jct="",
            buvid3="",
            dedeuserid="",
            ac_time_value="",
        )

    def __repr__(self):
        return "<DummyCredential>"


def model_to_commented_map(model: BaseModel) -> CommentedMap:
    fields = model.__class__.__pydantic_fields__
    output = CommentedMap()

    for name, field in fields.items():
        value = getattr(model, name)
        default = value if value is not None else field.default
        output[name] = default

        if field.description:
            output.yaml_set_comment_before_after_key(
                name, before=field.description
            )

    return output


def write_config_with_comments(model: BaseModel, path: str = "config.yaml"):
    config_map = CommentedMap()
    for name, _ in model.__class__.__pydantic_fields__.items():
        section = getattr(model, name)
        if isinstance(section, BaseModel):
            config_map[name] = model_to_commented_map(section)

    (
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.dirname(path)
        else None
    )

    with open(path, "w", encoding="utf-8") as f:
        yaml_ruamel.dump(config_map, f)

    logger.info(f"配置文件已生成并包含注释：{path}")


def ensure_config_file(path: str = "config.yaml"):
    if not os.path.exists(path):
        logger.warning(f"配置文件未找到，自动创建默认配置：{path}")
        default_settings = Settings()
        write_config_with_comments(default_settings, path)


def load_config(path: str = "config.yaml") -> Settings:
    ensure_config_file(path)
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    logger.info(f"配置文件加载成功：{path}")
    settings = Settings(**data)
    cred = settings.credential
    if isinstance(cred, DummyCredential):
        raise MissingCredentialError("请填写必要的Bilibili相关配置")
    return settings


_config_instance: Optional[Settings] = None


@lru_cache
def get_config() -> Settings:
    global _config_instance
    if _config_instance is None:
        _config_instance = load_config()
    return _config_instance


__all__ = ["get_config", "MissingCredentialError"]
