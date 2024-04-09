FROM python:3.11

WORKDIR /app

RUN pip install uv

RUN curl -fsSL https://raw.githubusercontent.com/tj/n/master/bin/n | bash -s lts && \
# If you want n installed, you can use npm now.\
npm install -g n && \
npm i -g wrangler

COPY pyproject.toml .
COPY reader_waylonwalker_com/__about__.py ./reader_waylonwalker_com/__about__.py
COPY reader_waylonwalker_com/__init__.py ./reader_waylonwalker_com/__init__.py
COPY README.md .

RUN uv pip install --system .
COPY . .
COPY metrics.json /root/.config/wrangler/metrics.json

RUN pip install ./markata
RUN uv pip install --system --no-deps .

WORKDIR /app

ENV CLOUDFLARE_API_TOKEN=
ENV TZ=America/Chicago

# ENTRYPOINT ['entrypoint.sh']
CMD '/app/entrypoint.sh'


