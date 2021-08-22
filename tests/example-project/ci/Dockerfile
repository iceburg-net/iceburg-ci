ARG REGISTRY=docker.io
# binaries we will use in our step images
FROM $REGISTRY/docker:20 as docker
FROM $REGISTRY/docker/compose:alpine-1.28.6 as compose
FROM $REGISTRY/hadolint/hadolint:latest-alpine as hadolint

# default ci image
FROM $REGISTRY/alpine:3 as default
COPY --from=docker /usr/local/bin/docker /usr/local/bin/
COPY --from=compose /usr/local/bin/docker-compose /usr/local/bin/

RUN apk add --no-cache \
  bats \
  bash

WORKDIR /work
ENTRYPOINT []

# image used for check step
FROM default as check
COPY --from=hadolint /bin/hadolint /usr/local/bin/
