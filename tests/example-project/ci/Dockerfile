ARG REGISTRY=docker.io
# binaries we will use in our step images
FROM $REGISTRY/docker:20.10.8 as docker
FROM $REGISTRY/docker/compose:alpine-1.29.2 as compose
FROM $REGISTRY/hadolint/hadolint:latest-alpine as hadolint

# default ci image
FROM $REGISTRY/alpine:3 as default
COPY --from=compose /usr/local/bin/docker-compose /usr/local/bin/
COPY --from=docker /usr/local/bin/docker /usr/local/bin/
COPY --from=hadolint /bin/hadolint /usr/local/bin/

RUN apk add --no-cache \
  bats \
  bash \
  git \
  python3

ENTRYPOINT []
