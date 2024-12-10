default:
  @just --choose

setup:
    #!/usr/bin/env bash
    set -euxo pipefail
    uv venv
    . ./.venv/bin/activate
    uv pip install -e .

clean:
    uv run markata clean

build:
    uv run markata build


deploy:
    npx wrangler pages deploy markout --project-name reader-waylonwalker-com --branch markout

exec:
    #!/usr/bin/env bash
    set -euxo pipefail
    podman run -it --rm -e CLOUDFLARE_API_TOKEN=$CLOUDFLARE_API_TOKEN reader-waylonwalker-com /bin/bash

deploy-image:
    #!/usr/bin/env bash
    set -euxo pipefail
    podman build -t docker.io/waylonwalker/reader-waylonwalker-com .
    version=$(cat version)
    # git tag $version
    podman tag docker.io/waylonwalker/reader-waylonwalker-com docker.io/waylonwalker/reader-waylonwalker-com:$version
    podman push docker.io/waylonwalker/reader-waylonwalker-com
    podman push docker.io/waylonwalker/reader-waylonwalker-com:$version
