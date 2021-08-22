# iceburg-ci

:icecream: straightforward docker compose driven CI for your projects

## examples

TBD example project


## environment variable conventions

the following variables are made available to CI steps.

name | example | description
--- | --- | ---
PIPELINE_ID | main-88 | unique namespace for a build (useful for tags). provided by CI platform [TBD gitlab, jenkins, github links].
PIPELINE_ARTIFACTS_PATH | ci/artifacts/main-88 | the output path for step artifacts and manifests

TBD passthrough of runtime environemt variables with the exception of JAVA_HOME, GEM_HOME, TERM &c

### oci image spec variables

in addition, the following variables are available for tagging artifacts according to the OCI image spec. provided by the CI platform [TBD gitlab, jenkins, github links].

name | example | description
--- | --- | ---
__AUTHORS | Mr. Bean | build author
__CREATED | 2021-06-15T23:32:41Z | artifact creation date
__REVISION | e351118cd | revision/ref used to build.
__SOURCE | git@github.com/iceburg-net/iceburg-ci.git | source/repo URL
__URL | http://jenkins/job/3562 | build/CI URL
__VERSION | 1.10.3 | build version or tag
