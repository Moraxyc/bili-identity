{
  description = "Bili Identity";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } (
      top@{
        ...
      }:
      {
        imports = [
          ./nix/devshell.nix
        ];
        flake = {
        };
        systems = [
          "x86_64-linux"
          "aarch64-linux"
          "x86_64-darwin"
          "aarch64-darwin"
        ];
        perSystem =
          { config, pkgs, ... }:
          {
            packages = rec {
              default = bili-identity;
              bili-identity = pkgs.callPackage ./nix/package.nix { };
            };
          };
      }
    );
}
