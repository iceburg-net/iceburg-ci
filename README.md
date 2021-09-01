# iceburg-ci

:icecream: straightforward docker compose driven CI for your projects

our goal is to support a single convention for CI builds across projects by providing one that is familiar and easy to drop in.

## quickstart

:one: enable iceburg-ci by including the [downstreamer](https://github.com/iceburg-net/iceburg-ci-downstreamer/) in your project or installing it as a system-wide tool.

:two: add a compliant `ci/docker-compose.yml` file to your project following one of the [examples](#examples).

:three: run a step (see [usage](#usage)) either via `bin/ci` or `iceburg-ci` (from any folder within the project if installed as a system tool).

## summary

iCEBURG CI provides a consistent interface to kickoff builds, both locally and on the CI platform.
> :family: This ensures accessible builds -- even when CI is down! Developers can run _exactly_ what the CI platform runs without having to check-in code.

projects include a compliant `ci/docker-compose.yml` in their repositories. this file defines an eponymously named service for each available step. at minimum, the default steps are represented (typically the `build` , `check`, and `test` services).

> :monorail: This ensures portable builds. The compose file works the same across platforms and projects.

the behavior of each step is defined by the service's command/entrypoint. for instance, the 'check' service's command may be `command: hadolint src/Dockerfile`. each service can reference a Dockerfile or image† to provide its own dependencies, such as a specific versions of terraform or the JDK.
> :package: This ensures self contained  builds. Only docker is needed on the host/developer machine.

† Instead of including a Dockerfile, a service may reference a  published image to keep things cached and DRY. The [iceburgci/step-image:universal](https://github.com/iceburg-net/iceburg-ci-docker-images) image makes a good choice.


iceburg-ci tooling is used to kickoff CI steps -- matching the requested step(s) to the appropriate docker-compose commands (e.g. `docker-compose run --rm test`) while taking care of concurrency, [environment variables](#environment-variables), volume mounts, and cleanup.
> :vertical_traffic_light: This ensures reliably repeatable builds. Developers don't need to reverse engineer nor do pipeline definitions need to be ported from one DSL to the next.

## usage

`bin/ci` (or `iceburg-ci` if system installed) `[step name...]`

e.x. to run the `larry`, `curly`, and `moe` step:

```
project$ bin/ci larry curly moe
```

steps are executed in the order specified. **failure will halt the execution of subsequent steps**.

if no steps are provided, the DEFAULT_STEPS will execute (currently `check` -> `build` -> `test`). thus the following are equivalent;
```
$ bin/ci
$ bin/ci check build test
```

### environment variables

the following variables are available to CI steps. the [CI platform](#ci-platform-integration) is expected to provide sensible values for some.

name | example | description
--- | --- | ---
PIPELINE_HOME | ~/.iceburg-ci/workspace-zHM | a fresh checkout of the iceburg-ci repository provided by the [downstreamer](https://github.com/iceburg-net/iceburg-ci-downstreamer). facilitates [sharing of common steps and tools](#central-steps-and-tools) and serves as a "scratch" directory (it is removed after execution unless ICEBURG_CI_SKIP_CLEANUP is set to 'true').
PIPELINE_ID | main-88 | unique namespace for a build. useful for versioning. typically provided by the CI platform as `<branch name>-<build number>`. defaults to `local-0` when not provided.
PIPELINE_MANIFEST | ~/git/acme-app/ci/manifest.json | location of the [pipeline manifest](#pipeline-manifest) file. defaults to `$PROJECT_HOME/ci/manifest.json`
PIPELINE_STEP | test | name of the running CI step
PROJECT_HOME | ~/git/acme-app | top-level project folder, aka "your repository root".


#### oci image spec variables

in addition, the following variables are available for providing metadata, such as labelling according to the [OCI image spec](https://github.com/opencontainers/image-spec/blob/main/annotations.md). these must be provided by the [CI Platform](#ci-platform-integration).

name | example | description
--- | --- | ---
__AUTHORS | Mr. Bean | build author
__CREATED | 2021-06-15T23:32:41Z | artifact creation date
__REVISION | e351118cd | revision/ref used to build.
__SOURCE | git@github.com/iceburg-net/iceburg-ci.git | source/repo URL
__URL | http://jenkins/job/3562 | build/CI URL
__VERSION | 1.10.3 | build version or tag

#### runtime variables

:mag: in addition to the listed variables, the current runtime environment variables (with the exception of those in a blocklist such as `JAVA_HOME` and `PATH`) are passed through to the step container.


### examples

TBD -- and link to examples repository.

### Central Steps and Tools

The contents of the iceburg-ci repository (or your organization's [self hosted one](https://github.com/iceburg-net/iceburg-ci-downstreamer#self-hosted-iceburg-ci)) is available to any step by referencing the `$PIPELINE_HOME` [variable](#environment-variables) -- and we can use this repository to provide centrally managed tooling to help keep things DRY.

For instance, you may want to include a common `build` step shared by some projects. To do this;

* commit your shared workflow to the iceburg-ci repository under `lib/steps/acme/build` (any path will do -- `lib/steps` is just a suggestion). e.g.
  ```sh
  iceburg-ci$ cat lib/steps/acme/build

  #!/usr/bin/env bash
  echo "Greetings form the ACME CORPORATION build step." >&2
  echo "My version of the aws cli is:" >&2
  aws --version
  ...
  ```

* execute the shared workflow from a project's `build` step. e.g.
  ```yml
  acme-project$ cat ci/docker-compose.yml

  ---
  version: "3.9"

  services:
    build:
      image: "amazon/aws-cli:2.2.33"
      command: "$PIPELINE_HOME/lib/steps/acme/build"
  ```

### Pipeline Manifest

> NOTE: the manifest tooling currently requires step containers to have a working python3 environment.

iCEBURG CI keeps a manifest of step execution through a central [bin/manifest](bin/manifest) tool. the location of the manifest is determined by the `PIPELINE_MANIFEST` [variable](#environment-variables) -- typically `ci/manifest.json`. steps can reference the manifest to perform work (see [step artifacts](#step-artifacts)). A pipeline that is currently running the `build` step looks like:

```yml
---
# example showing a currently running 'build' step
id: local-0
steps:
  - name: check
    status:
      start: 2020-01-30 05:30:45
      end: 2020-01-30 05:30:50
      code: 0
  - name: build
    status:
      start: 2020-01-30 05:30:51
      end: null
      code: null
```

The [lib/pipeline-manifest](lib/pipeline-manifest/) folder contains a full example and manifest schema.

the [CI platform](#ci-platform-integration) may make the manifest available as an downloadable artifact to pass around or to give users insight into what happened without having to look through logs.

#### step artifacts

the [bin/manifest](bin/manifest) tool provides a convention for steps to register their results (`add` artifacts) or to work with the results (`list` artifacts) of prior step(s). for instance, a 'publish' step may want to publish artifacts that were produced by the 'build' step. below is an example;

```yml
---
version: "3.9"
services:
  build:
    image: "iceburgci/step-image:universal"
    command: |
      sh -c '
        set -eo pipefail
        docker build -t acme-app:$PIPELINE_ID src/
        docker tag acme-app:$PIPELINE_ID acme-app:latest

        # register image(s) as 'docker' type artifacts
        "$PIPELINE_HOME/bin/manifest" artifact add -t docker \
          acme-app:$PIPELINE_ID \
          acme-app:latest
      '

  publish:
    image: "iceburgci/step-image:universal"
    command: |
      sh -c '
        set -eo pipefail
        # publish docker image(s) from the 'build' step
        "$PIPELINE_HOME/bin/manifest" artifact ls -t docker -s build | \
          while read -r img; do
            publish_img="acme.registry/$img"
            docker tag "$img" "$publish_img"
            docker push "$publish_img"
            "$PIPELINE_HOME/bin/manifest" artifact add -t docker "$publish_img"
          done
      '
```

the `bin/manifest artifact add` and `bin/manifest artifact ls` commands are used. `-t` groups artifacts under an _arbitrary_  type ('file' being the default). `-s` is used for working with artifacts in a different step (the current step name / [[$PIPELINE_STEP](#environment-variables)] being the default). see the command help for more.


### CI Platform Integration

#### GitHub Actions

iceburg-ci-vars-action TBD
iceburg-ci-manifest-action TBD

#### GitLab CI

We recommend you include the following variable definitions in where iCEBURG CI is invoked.

```yml
variables:
  PIPELINE_ID: $CI_COMMIT_REF_SLUG-$CI_PIPELINE_IID
  __AUTHORS: $CI_COMMIT_AUTHOR
  __REVISION: $CI_COMMIT_SHA
  __SOURCE: $CI_PROJECT_URL
  __URL: $CI_PIPELINE_URL
  __VERSION:
    value: $CI_COMMIT_TAG
    description: defaults to commit tag (if a tag is pushed)
```

TODO: manifest example


#### Jenkins Pipeline

We recommend you include the following environment definitions where iCEBURG CI is invoked.

```groovy
environment {
  // pipeline params
  BUILD_CHANNEL="${env.BRANCH_NAME}".replaceAll(/[^A-Za-z0-9_\-\.]/, "_").take(120)
  BUILD_REVISION="${env.BUILD_NUMBER}"
  PIPELINE_ID="${env.BUILD_CHANNEL}-${env.BUILD_REVISION}"
  __AUTHORS="${env.GIT_AUTHOR_NAME}"
  __REVISION="${env.GIT_COMMIT}"
  __SOURCE="${env.GIT_URL}"
  __URL="${env.BUILD_URL}"
  __VERSION="${env.TAG_NAME}"
}
```

TODO: manifest example

## history

iCEBURG CI is patterned from [AnyCI](https://github.com/anyci/anyci/) but favors a familiar convention (the expectation fo ci/docker-compose.yml) over flexibility.

Early roots are in bin/exec and groundcontrol/starfleet's `sun/planet:moon` overlay inspired by docker image convention.
