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
          ]
          ++ (import ./deps.nix pypkgs);
      };
    };
}
