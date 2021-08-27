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

projects include a compliant `ci/docker-compose.yml` in their repositories. this file defines the available steps and their behavior, as well as orchestrates any runtime dependencies.

> :monorail: This ensures portable builds. The compose file works the same across platforms and projects.

each service in `ci/docker-compose.yml` represents a step. at minimum, the default steps are defined (typically the `build`, `check`, and `test` services). each step can reference it's own Dockerfile or image† to provide dependencies.
> :package: This ensures self contained  builds. The step container provides necessary dependencies.

† Instead of including a Dockerfile, a service may reference an already published image to keep things DRY and centrally managed.


iceburg-ci tooling is used to kickoff CI steps -- matching the requested step(s) to the appropriate docker-compose commands (e.g. `docker-compose run --rm test`) while taking care of concurrency, environment variable conventions, and cleanup.
> :vertical_traffic_light: This ensures reliably repeatable builds. Developers don't need to remember commands nor do pipeline definitions need to be ported from one DSL to the next.

## usage

`bin/ci` (or `iceburg-ci` if system installed) `[step name...]`

e.x. to run the `larry`, `curly`, and `moe` step:

```
project$ bin/ci larry curly moe
```

steps are executed in the order specified. failure will halt the execution of subsequent steps.

if no steps are provided, the ICEBURG_CI_DEFAULT_STEPS will execute (`check` -> `build` -> `test`).

### environment variables

the following variables are available to CI steps. the [CI platform](#ci-platform-integration) is expected to provide sensible values for some.

name | example | description
--- | --- | ---
PIPELINE_HOME | ~/.iceburg-ci/workspace-zHM | location of a fresh iCEBURG CI checkout provided by the [downstreamer](https://github.com/iceburg-net/iceburg-ci-downstreamer). facilitates the sharing of common steps and tools across projects. removed after execution unless ICEBURG_CI_SKIP_CLEANUP is set to 'true'.
PIPELINE_STEP | test | name of the running CI step
PIPELINE_ID | main-88 | unique namespace for a build. useful for versioning. typically provided by the CI platform as `<branch name>-<build number>`. defaults to `local-0` when not provided.
PROJECT_ROOT | ~/git/acme-app | location of the top-level project folder, aka "root level of the application repository".


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

You may find it nice to have centrally maintained and always updated tooling available to any step -- and this is easily facilitated by including them in a [self hosted iceburg-ci repository](https://github.com/iceburg-net/iceburg-ci-downstreamer#self-hosted-iceburg-ci). A checkout of this repository is available at `$PIPELINE_HOME`.

For instance, you may want to include a common `acme` step. To do this,

* commit the step script to the iceburg-ci repository under `lib/steps/acme` (any path will do -- `lib/steps` is just a suggestion). e.g.
  ```
  iceburg-ci$ cat lib/steps/acme

  #!/usr/bin/env bash
  echo "Greetings form the ACME CORPORATION step." >&2
  echo "My version of the aws cli is:" >&2
  aws --version
  ...
  ```

* call the step script from a project's CI workflow. e.g.
  ```
  acme-project$ cat ci/docker-compose.yml

  ---
  version: "3.9"

  services:
    acme:
      image: "amazon/aws-cli:2.2.33"
      command: "$PIPELINE_HOME/lib/steps/acme"
  ```


## CI Platform Integration

### GitHub Actions

iceburg-ci-vars-action TBD

### GitLab CI

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


### Jenkins Pipeline

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

## history

iCEBURG CI is patterned from [AnyCI](https://github.com/anyci/anyci/) but favors a familiar convention (the expectation fo ci/docker-compose.yml) over flexibility.

Early roots are in bin/exec and groundcontrol/starfleet's `sun/planet:moon` overlay inspired by docker image convention.
