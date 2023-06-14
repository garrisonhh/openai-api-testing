{
  inputs = {
    nixpkgs.url = github:NixOs/nixpkgs/nixos-23.05;
  };

  outputs = { self, nixpkgs }:
    let
      # environment
      system = "x86_64-linux";

      # project reqs
      inherit (pkgs) mkShell;
      pkgs = nixpkgs.legacyPackages.${system};

      # developer shell
      devShell = mkShell {
        packages = with pkgs.python311Packages; [
          python
          requests
        ];
      };
    in {
      devShells.${system}.default = devShell;
    };
}