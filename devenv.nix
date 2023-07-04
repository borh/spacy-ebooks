{ pkgs, lib, ... }:

{
  # https://devenv.sh/basics/
  # https://devenv.sh/packages/
  packages = with pkgs; [
    git
    zlib
    stdenv.cc.cc.lib
  ];

  enterShell = ''
    export OPENAI_API_KEY=$(cat /run/agenix/openai-api)
    export OPENAI_API_ORG=$(cat /run/agenix/openai-org)
  '';

  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
    package = pkgs.python311;
    poetry.enable = true;
  };

  scripts.export-pip.exec = "poetry export -f requirements.txt --output requirements.txt; poetry export --with llm -f requirements.txt --output requirements-llm.txt";

  scripts.ptw.exec = "poetry run ptw";

  env.LD_LIBRARY_PATH = lib.mkIf pkgs.stdenv.isLinux (
    lib.makeLibraryPath (with pkgs; [
      gcc-unwrapped.lib
      linuxPackages_latest.nvidia_x11
      zlib
      cmake
      cudaPackages.cudatoolkit
      cudaPackages.cudnn
      cudaPackages.libcublas
      cudaPackages.libcurand
      cudaPackages.libcufft
      cudaPackages.libcusparse
      cudaPackages.cuda_nvtx
      cudaPackages.cuda_cupti
      cudaPackages.cuda_nvrtc
      cudaPackages.nccl
    ])
  );
  env.CUDA_HOME = "${pkgs.cudaPackages.cudatoolkit}";
  env.CUDA_PATH = "${pkgs.cudaPackages.cudatoolkit}";

  # https://devenv.sh/pre-commit-hooks/
  # pre-commit.hooks.shellcheck.enable = true;

  # https://devenv.sh/processes/
  # processes.ping.exec = "ping example.com";

  # See full reference at https://devenv.sh/reference/options/
}
