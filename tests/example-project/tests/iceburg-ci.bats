#!/usr/bin/env bats

@test "ensure PIPELINE_STEP is set to current step" {
  echo "PIPELINE_STEP: $PIPELINE_STEP"
  [ "$PIPELINE_STEP" = "test" ]
}
