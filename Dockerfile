FROM astral/uv:python3.12-bookworm-slim

WORKDIR /usr/src/autoapply

COPY . .

RUN setup.sh
