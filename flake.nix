{
  description = "nilm env";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {
        system = "${system}";
        config.allowUnfree = true;  # allow for unfree cuda
      };
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
      electricity = py.buildPythonPackage rec {
        pname = "electricity";
        version = "0.0.1";
        format = "pyproject";
        src = ./. ;
        buildInputs = [
          py.setuptools-scm
        ];
      };

    in {
      devShells.default = pkgs.mkShell rec {
        packages = with pkgs; [
          py.bokeh
          py.jupyterlab
          py.pandas
          py.pytorchWithCuda
          py.scikit-learn
          py.tensorboard
          py.tqdm
          py.widgetsnbextension

          # plotting
          py.plotly
          py.ipywidgets

          # from github
          pyprojroot

          # local
          electricity
        ];
      };
    });
}
