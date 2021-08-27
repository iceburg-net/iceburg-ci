# iceburg-ci

:icecream: straightforward docker compose driven CI for your projects

## usage

TBD example project


## environment variables

the following variables are available to CI steps. the [CI platform](#CI-Platform-Integration) is expected to provide sensible values for some.

name | example | description
--- | --- | ---
PIPELINE_HOME | ~/.iceburg-ci/workspace-zHM | location of a fresh iCEBURG CI checkout provided by the [downstreamer](https://github.com/iceburg-net/iceburg-ci-downstreamer). facilitates the sharing of common steps and tools across projects.
PIPELINE_STEP | test | name of the running CI step
PIPELINE_ID | main-88 | unique namespace for a build. useful for versioning. typically provided by the CI platform as `<branch name>-<build number>`. defaults to `local-0` when not provided.
PROJECT_ROOT | ~/git/acme-app | location of the top-level project folder, aka "root level of the application repository".


### oci image spec variables

in addition, the following variables are available for providing metadata, such as labelling according to the [OCI image spec](https://github.com/opencontainers/image-spec/blob/main/annotations.md). these must be provided by the [CI Platform](#CI-Platform-Integration).

name | example | description
--- | --- | ---
__AUTHORS | Mr. Bean | build author
__CREATED | 2021-06-15T23:32:41Z | artifact creation date
__REVISION | e351118cd | revision/ref used to build.
__SOURCE | git@github.com/iceburg-net/iceburg-ci.git | source/repo URL
__URL | http://jenkins/job/3562 | build/CI URL
__VERSION | 1.10.3 | build version or tag

### runtime variables

:bulb: in addition to the listed variables, the current runtime environment variables (with the exception of those in a blocklist such as `JAVA_HOME` and `PATH`) are passed through to the step container.


## CI Platform Integration

### GitHub Actions

### GitLab CI

### Jenkins Pipeline
