build:
    markata clean
    mkdir -p markout
    markata build
    npx wrangler pages deploy markout --project-name reader-waylonwalker-com --branch markout

exec:
    podman run -it --rm -e CLOUDFLARE_API_TOKEN=$CLOUDFLARE_API_TOKEN reader-waylonwalker-com /bin/bash

deploy:
    #!/bin/bash -e
    podman build -t docker.io/waylonwalker/reader-waylonwalker-com .
    version=$(cat version)
    # git tag $version
    podman tag docker.io/waylonwalker/reader-waylonwalker-com docker.io/waylonwalker/reader-waylonwalker-com:$version
    podman push docker.io/waylonwalker/reader-waylonwalker-com
    podman push docker.io/waylonwalker/reader-waylonwalker-com:$version
