{ pkgs, ... }:

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

  # https://devenv.sh/pre-commit-hooks/
  # pre-commit.hooks.shellcheck.enable = true;

  # https://devenv.sh/processes/
  # processes.ping.exec = "ping example.com";

  # See full reference at https://devenv.sh/reference/options/
}
