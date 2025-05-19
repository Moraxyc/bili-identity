{
  perSystem =
    { pkgs, ... }:
    {
      devShells.default = pkgs.mkShellNoCC {
        venvDir = ".venv";
        buildInputs =
          with pkgs;
          [ ]
          ++ (with python313Packages; [
            venvShellHook

            bilibili-api-python
          ]);
      };
    };
}
