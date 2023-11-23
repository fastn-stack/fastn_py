{
  description = "fastn_py";

  outputs = { self, nixpkgs }: 
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
  in 
  {
      devShells.${system}.default = pkgs.mkShell {
          name = "fastn_py_shell";
          buildInputs = with pkgs; [ 
              black # format python code
              python311
          ];
      };
  };
}
