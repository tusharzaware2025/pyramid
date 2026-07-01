#!/usr/bin/env python3
"""Remove Azure Data Factory managed private endpoints from ARM templates.

ADF managed private endpoints are environment-specific network resources. Once
created, their target properties are not safely mutable through normal ARM
redeployments, so promoting them through CI/CD can fail with "Invalid payload".
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


MPE_TYPE = (
    "microsoft.datafactory/factories/managedvirtualnetworks/"
    "managedprivateendpoints"
)


def normalize_resource_type(resource_type: str) -> str:
    return resource_type.replace("\\", "/").strip("/").lower()


def is_managed_private_endpoint(resource: dict[str, Any]) -> bool:
    resource_type = resource.get("type")
    return isinstance(resource_type, str) and normalize_resource_type(resource_type) == MPE_TYPE


def endpoint_name(resource_name: Any) -> str | None:
    if not isinstance(resource_name, str) or not resource_name:
        return None

    # Literal ARM names usually look like "factory/default/mpe_name".
    literal_parts = [part for part in resource_name.split("/") if part]
    if literal_parts and not resource_name.lstrip().startswith("["):
        return literal_parts[-1]

    # ADF publish templates commonly emit:
    # [concat(parameters('factoryName'), '/default/mpe_name')]
    match = re.search(r"/default/([^'\"\]\)]+)", resource_name, flags=re.IGNORECASE)
    if match:
        return match.group(1)

    return None


def dependency_targets_endpoint(dependency: Any, removed_endpoint_names: set[str]) -> bool:
    if not isinstance(dependency, str):
        return False

    normalized = dependency.lower()
    if "managedprivateendpoints" not in normalized and "/default/" not in normalized:
        return False

    return any(endpoint.lower() in normalized for endpoint in removed_endpoint_names)


def remove_managed_private_endpoints(template: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    resources = template.get("resources")
    if not isinstance(resources, list):
        return template, []

    removed_names: list[str] = []
    kept_resources: list[Any] = []

    for resource in resources:
        if isinstance(resource, dict) and is_managed_private_endpoint(resource):
            removed_names.append(endpoint_name(resource.get("name")) or str(resource.get("name")))
            continue

        kept_resources.append(resource)

    if not removed_names:
        return template, []

    removed_name_set = set(removed_names)
    for resource in kept_resources:
        if not isinstance(resource, dict):
            continue

        depends_on = resource.get("dependsOn")
        if not isinstance(depends_on, list):
            continue

        resource["dependsOn"] = [
            dependency
            for dependency in depends_on
            if not dependency_targets_endpoint(dependency, removed_name_set)
        ]

    filtered_template = dict(template)
    filtered_template["resources"] = kept_resources
    return filtered_template, removed_names


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove ADF managed private endpoint resources from an ARM template."
    )
    parser.add_argument("template", type=Path, help="Path to the ARM template JSON file.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Write the filtered template to this path. Defaults to overwriting input.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = args.output or args.template

    with args.template.open(encoding="utf-8") as template_file:
        template = json.load(template_file)

    if not isinstance(template, dict):
        raise ValueError(f"{args.template} does not contain a JSON object ARM template.")

    filtered_template, removed_names = remove_managed_private_endpoints(template)

    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(filtered_template, output_file, indent=2)
        output_file.write("\n")

    if removed_names:
        print(
            "Removed ADF managed private endpoint resources: "
            + ", ".join(sorted(removed_names))
        )
    else:
        print("No ADF managed private endpoint resources found.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
