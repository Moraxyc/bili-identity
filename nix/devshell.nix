{
  perSystem =
    { pkgs, ... }:
    let
      pypkgs = pkgs.python313.pkgs;
    in
    {
      devShells.default = pkgs.mkShellNoCC {
        venvDir = ".venv";
        buildInputs =
          with pkgs;
          [
            sqlite

            pypkgs.venvShellHook
            pypkgs.flake8
          ]
          ++ (import ./deps.nix pypkgs);
      };
    };
}
