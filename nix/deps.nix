pypkgs: with pypkgs; [
  (bilibili-api-python.overrideAttrs (
    _finalAttrs: _prevAttrs: {
      patches = [ ./0001-fix-fetch_session_msgs.patch ];
    }
  ))
  jwcrypto

  fastapi
  uvicorn

  sqlalchemy
  aiosqlite
  redis

  ruamel-yaml
  pydantic
  pydantic-core

  httpx
]
