#!/usr/bin/env bats

@test "ensure PIPELINE_STEP is set to current step" {
  echo "PIPELINE_STEP: $PIPELINE_STEP"
  [ "$PIPELINE_STEP" = "test" ]
}

@test "ensure manifest contains build step artifacts" {
  "$PIPELINE_HOME/bin/manifest" artifact ls -s build | grep -q "ping-pong:$PIPELINE_ID"
}
