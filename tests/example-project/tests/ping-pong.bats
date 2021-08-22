#!/usr/bin/env bats

@test "pinging TEST_URI" {
  echo "TEST_URI: $TEST_URI"
  [ "$(wget -qO- $TEST_URI)" = "pong" ]
}
