mkdir -p markout
markata build
wrangler pages deploy markout --project-name reader-waylonwalker-com --branch markout
