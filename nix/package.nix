{
  lib,
  python313,
}:

let
  pypkgs = python313.pkgs;
in
pypkgs.buildPythonPackage {
  pname = "bili-identity";
  version = builtins.readFile ../bili_identity/VERSION;
  pyproject = true;

  src = ../.;

  build-system = with pypkgs; [
    setuptools
  ];

  dependencies = import ./deps.nix pypkgs;

  meta = {
    homepage = "https://github.com/Moraxyc/bili-identity";
    description = "Lightweight OpenID layer for Bilibili accounts";
    maintainers = [ lib.maintainers.moraxyc ];
    license = lib.licenses.gpl3Plus;
  };
}
