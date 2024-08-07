{
  description = "Development environment for Fanboi Channel";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ ];
        };
      in
      rec {
        devShell = with pkgs; mkShell {
          name = "fanboi2-env";

          packages = [
            bmake

            # DBs
            postgresql_14
            redis

            # Assets
            nodejs
            nodePackages.pnpm

            # Python
            (python311.withPackages (ps: with ps; [
              black
              flake8
              python-lsp-black
              python-lsp-server
            ]))
          ];

          shellHook = ''
            alias make="${pkgs.bmake}/bin/bmake"
          '';
        };
      }
    );
}
