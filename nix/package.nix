{
  lib,
  python3,
}:

python3.pkgs.buildPythonPackage {
  pname = "bili-identity";
  version = builtins.readFile ../bili_identity/VERSION;
  pyproject = true;

  src = ../.;

  build-system = with python3.pkgs; [
    setuptools

  ];

  dependencies = with python3.pkgs; [
    bilibili-api-python
  ];

  meta = {
    homepage = "https://github.com/Moraxyc/bili-identity";
    description = "Lightweight OpenID layer for Bilibili accounts";
    maintainers = [ lib.maintainers.moraxyc ];
    license = lib.licenses.gpl3Plus;
  };
}
