{
  description = "nilm env";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      py = pkgs.python311Packages;
      pyprojroot = py.buildPythonPackage rec {
        pname = "pyprojroot";
        version = "0.3.0";
        format = "pyproject";
        src = pkgs.fetchPypi{
          inherit pname version;
          sha256 = "sha256-EJcFu3kJaHBJWO/PxczOhdjj2voFSJfMgTcfy79WyxA=";
        };
        buildInputs = [
          py.setuptools
        ];
      };

    in {
      devShells.default = pkgs.mkShell rec {
        packages = with pkgs; [
          py.bokeh
          py.jupyterlab
          py.pandas
          py.pytorch
          py.scikit-learn
          py.tensorboard
          py.tqdm
          py.widgetsnbextension

          # plotting
          py.plotly
          py.ipywidgets

          # from github
          pyprojroot
        ];
      };
    });
}
