default:
  @just --list


# fuzzy picker
[group('just')]
f:
  @just --choose

[group('lint')]
setup:
    #!/usr/bin/env bash
    set -euxo pipefail
    uv venv
    . ./.venv/bin/activate
    uv pip install -e .

[group('work')]
clean:
    uv run markata clean

[group('work')]
build:
    uv run markata build


[group('work')]
deploy:
    npx wrangler pages deploy markout --project-name reader-waylonwalker-com --branch markout

[group('work')]
exec:
    #!/usr/bin/env bash
    set -euxo pipefail
    podman run -it --rm -e CLOUDFLARE_API_TOKEN=$CLOUDFLARE_API_TOKEN reader-waylonwalker-com /bin/bash

[group('work')]
deploy-image:
    #!/usr/bin/env bash
    set -euxo pipefail
    version=$(cat version)
    echo deploying {{GREEN}}$version{{NORMAL}}
    podman build -t docker.io/waylonwalker/reader-waylonwalker-com -t docker.io/waylonwalker/reader-waylonwalker-com:$version -t registry.wayl.one/reader-waylonwalker-com -t registry.wayl.one/reader-waylonwalker-com:$version .
    # git tag $version
    podman push docker.io/waylonwalker/reader-waylonwalker-com
    podman push docker.io/waylonwalker/reader-waylonwalker-com:$version
    podman push registry.wayl.one/reader-waylonwalker-com
    podman push registry.wayl.one/reader-waylonwalker-com:$version

[group('manage')]
version:
    #!/usr/bin/env bash
    version=$(cat version)
    echo current version {{BOLD}}{{GREEN}}$version{{NORMAL}}

[group('manage')]
version-patch:
    #!/usr/bin/env bash
    version=$(cat version)
    echo current version {{BOLD}}{{GREEN}}$version{{NORMAL}}
    version=$(echo $version | awk -F. '{print $1"."$2"."$3+1}')
    echo new version {{BOLD}}{{GREEN}}$version{{NORMAL}}
    echo $version > version

[group('manage')]
version-minor:
    #!/usr/bin/env bash
    version=$(cat version)
    echo current version {{BOLD}}{{GREEN}}$version{{NORMAL}}
    version=$(echo $version | awk -F. '{print $1"."$2+1".0"}')
    echo new version {{BOLD}}{{GREEN}}$version{{NORMAL}}
    echo $version > version

[group('manage')]
version-major:
    #!/usr/bin/env bash
    version=$(cat version)
    echo current version {{BOLD}}{{GREEN}}$version{{NORMAL}}
    version=$(echo $version | awk -F. '{print $1+1".0.0"}')
    echo new version {{BOLD}}{{GREEN}}$version{{NORMAL}}
    echo $version > version


