#!/usr/bin/env python3
#
# @Source https://github.com/iceburg-net/iceburg-ci/blob/main/bin/manifest.py
# @Style python-black
# @Version 0.0.2
#
# usage: foo [-h] [-f FILE] [-v] {artifact,step} ...
#
# Queries and Updates the CI Pipeline Step Manifest
#
# optional arguments:
#   -h, --help            show this help message and exit
#   -f FILE, --file FILE  manifest file (default: ./manifest.json)
#   -v, --verbose         increase output verbosity (default: False)
#
# commands:
#   {artifact,step}
#     artifact            add and list artifacts
#     step                start and stop steps

import argparse
from datetime import datetime
import json
import logging
import os
import sys


def main(args, loglevel):
    logging.basicConfig(
        format="%(asctime)s [%(levelname)-8s] %(message)s (%(filename)s:%(lineno)s)",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=loglevel,
    )

    try:
        manifest = PipelineManifest(args.file)
        if args.command == "step":
            if args.subcommand == "start":
                manifest.step_start(args.step_name)
            elif args.subcommand == "stop":
                manifest.step_stop(args.step_name, exit_code=args.exit_code)
            manifest.write(args.file)
        elif args.command == "artifact":
            if args.subcommand == "add":
                manifest.artifact_add(
                    args.name, step_name=args.step_name, type=args.type
                )
                manifest.write(args.file)
            elif args.subcommand == "ls":
                manifest.artifact_list(
                    step_names=args.step_name,
                    types=args.type,
                    step_count=args.step_count,
                )
    except Exception as e:
        logging.critical("operation failed")
        sys.exit(1)


class PipelineManifest:
    def __init__(self, file):
        default_manifest = {
            "pipeline_id": os.environ.get("PIPELINE_ID", ""),
            "steps": [],
        }

        try:
            with open(file, "r") as f:
                self.manifest = json.load(f)

        except json.JSONDecodeError as e:
            logging.warning("malformed manifest:resetting to default")
            self.manifest = default_manifest

        except FileNotFoundError as e:
            os.makedirs(os.path.dirname(file), exist_ok=True)
            self.manifest = default_manifest

        except Exception as e:
            logging.error("failed manifest registration")
            raise

    def artifact_add(self, names, type="file", step_name=None):
        step = self.get_running_step(step_name, True)

        if not step:
            logging.error("failed to find any '%s' steps" % step_name)
            raise

        if not "artifacts" in step:
            step["artifacts"] = []

        if "-" in names:
            names.extend(sys.stdin.read().rstrip().split())

        for name in names:
            if name == "-":
                continue
            step["artifacts"].append({"name": name, "type": type})

    def artifact_list(self, types=[], step_names=[], step_count=0):
        considered_count = 1
        for step in reversed(self.manifest["steps"]):
            if step_count and considered_count > step_count:
                break
            elif step_names and step["name"] not in step_names:
                continue
            elif "artifacts" not in step:
                continue

            considered = False
            for artifact in step["artifacts"]:
                if types and artifact["type"] not in types:
                    continue
                if not considered:
                    considered = True
                    considered_count += 1
                print(artifact["name"])

    def step_start(self, step_name):
        self.manifest["steps"].append(
            {
                "name": step_name,
                "status": {"start": self.get_timestamp(), "stop": None, "code": None},
            }
        )

    def step_stop(self, step_name, exit_code=0):
        step = self.get_running_step(step_name)
        if step:
            step["status"]["stop"] = self.get_timestamp()
            step["status"]["code"] = exit_code

    def get_running_step(self, step_name, returnFirstStoppedStep=False):
        first_stopped_step = None

        # traverse steps in reverse order looking for one that has not ended
        for i, step in reversed(list(enumerate(self.manifest["steps"]))):
            if step["name"] == step_name:
                if step["status"]["stop"] == None:
                    return self.manifest["steps"][i]
                elif returnFirstStoppedStep and not first_stopped_step:
                    first_stopped_step = self.manifest["steps"][i]

        logging.warning("failed to find a running '%s' step" % step_name)
        return first_stopped_step if returnFirstStoppedStep else None

    def get_timestamp(self):
        return datetime.now().isoformat(timespec="milliseconds")

    def write(self, file):
        try:
            with open(file, "w", encoding="utf-8") as f:
                json.dump(self.manifest, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error("failed writing manifest")
            raise


if __name__ == "__main__":

    default_step_name = "default"

    cli = argparse.ArgumentParser(
        description="Queries and Updates the CI Pipeline Step Manifest",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    cli.add_argument(
        "-f",
        "--file",
        help="manifest file",
        default=os.environ.get("MANIFEST_FILE", "./manifest.json"),
    )
    cli.add_argument(
        "-v", "--verbose", help="increase output verbosity", action="store_true"
    )

    cli_cmds = cli.add_subparsers(title="commands", dest="command")

    cli_cmd_artifact = cli_cmds.add_parser(
        "artifact",
        help="add and list artifacts",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cli_cmds_artifact = cli_cmd_artifact.add_subparsers(
        title="artifact command", dest="subcommand"
    )
    cli_cmd_artifact_list = cli_cmds_artifact.add_parser(
        "ls",
        help="list artifacts",
        description="list artifacts",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cli_cmd_artifact_list.add_argument(
        "-s", "--step-name", help="only show artifacts from step name(s)", nargs="*"
    )
    cli_cmd_artifact_list.add_argument(
        "-c",
        "--step-count",
        help="include artifacts from up <count> steps. 0 to consider artifacts in all matching steps.",
        default=1,
        type=int,
    )
    cli_cmd_artifact_list.add_argument(
        "-t",
        "--type",
        help="only show artifacts of type(s), e.g. 'file', 'docker', 'mvn', &c.",
        nargs="*",
    )

    cli_cmd_artifact_add = cli_cmds_artifact.add_parser(
        "add",
        help="add artifacts",
        description="add artifacts. artifact names may be passed or read from stdin.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cli_cmd_artifact_add.add_argument(
        "-s",
        "--step-name",
        help="step name",
        default=os.environ.get("PIPELINE_STEP", default_step_name),
    )
    cli_cmd_artifact_add.add_argument(
        "-t",
        "--type",
        help="artifact type, e.g. 'file', 'docker', 'mvn', &c.",
        default="file",
    )
    cli_cmd_artifact_add.add_argument(
        "name",
        help="artifact name(s). if '-', names read from stdin",
        metavar="name|-",
        nargs="+",
    )

    cli_cmd_step = cli_cmds.add_parser("step", help="start and stop steps")
    cli_cmds_step = cli_cmd_step.add_subparsers(title="step command", dest="subcommand")
    cli_cmd_step_start = cli_cmds_step.add_parser(
        "start",
        help="start a step",
        description="start a step",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cli_cmd_step_start.set_defaults(func="step_start")
    cli_cmd_step_start.add_argument(
        "-s",
        "--step-name",
        help="step name",
        default=os.environ.get("PIPELINE_STEP", default_step_name),
    )
    cli_cmd_step_stop = cli_cmds_step.add_parser(
        "stop",
        help="stop a step",
        description="stop a step",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cli_cmd_step_stop.set_defaults(func="step_stop")
    cli_cmd_step_stop.add_argument(
        "-s",
        "--step-name",
        help="step name",
        default=os.environ.get("PIPELINE_STEP", default_step_name),
    )
    cli_cmd_step_stop.add_argument(
        "-e",
        "--exit-code",
        help="exit code (0 for success, 1-255 for error)",
        type=int,
        default=0,
    )

    args = cli.parse_args()
    loglevel = logging.DEBUG if args.verbose else logging.INFO

    if not args.command or not args.subcommand:
        cli.print_help()
    else:
        main(args, loglevel)
