#!/usr/bin/env bats

@test "ensure PIPELINE_STEP is set to current step" {
  echo "PIPELINE_STEP: $PIPELINE_STEP"
  [ "$PIPELINE_STEP" = "test" ]
}

@test "ensure PIPELINE_HOME is set to root of ci checkout" {
  echo "PIPELINE_HOME: $PIPELINE_HOME"
  [ "$PIPELINE_HOME" = "$(git rev-parse --show-toplevel)" ]
}

@test "ensure manifest contains build step artifacts" {
  "$PIPELINE_HOME/bin/manifest" artifact ls -s build | grep -q "ping-pong:$PIPELINE_ID"
}

@test "support multiple version arguments" {
  bin/ci -v | grep -q "version:"
  bin/ci --version  | grep -q "version:"
  bin/ci version | grep -q "version:"
}

@test "support arbitrary commands" {
  run --separate-stderr bin/ci -- pwd
  [ "$output" = "$PIPELINE_HOME" ]
}

@test "support custom steps" {
  run --separate-stderr bin/ci local-step
  [[ "$output" == *"teapot"* ]]
  [ "$status" -eq 123 ]

  run --separate-stderr bin/ci shared-step
  [[ "$output" == *"teapot"* ]]
  [ "$status" -eq 111 ]
}

@test "ensure optional steps" {
  run bin/ci missing-step
  [[ "$output" == *"WARN"* ]]
  [[ "$output" == *"skipping missing-step"* ]]
  [ "$status" -eq 0 ]
}
