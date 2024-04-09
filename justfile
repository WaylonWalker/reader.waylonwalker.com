build:
    markata clean
    mkdir -p markout
    markata build
    npx wrangler pages deploy markout --project-name reader-waylonwalker-com --branch markout

exec:
    podman run -it --rm -e CLOUDFLARE_API_TOKEN=$CLOUDFLARE_API_TOKEN reader-waylonwalker-com /bin/bash

build-image:
    podman build -t docker.io/waylonwalker/reader-waylonwalker-com .

push-image:
    podman push docker.io/waylonwalker/reader-waylonwalker-com
