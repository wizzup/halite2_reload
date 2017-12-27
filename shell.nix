{ pkgs ? import <nixpkgs> {} }:

with pkgs;

let py3s = pkgs.python3.buildEnv.override  {
  extraLibs = with pkgs.python3Packages; [ pylint ];
};
in stdenv.mkDerivation {
  name = "pyshell";
  buildInputs = [ py3s ];

  shellHook = ''
    export PS1="\[\033[1;32m\][$name:\W]\n$ \[\033[0m\]"
  '';
}
