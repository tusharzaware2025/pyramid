#!/usr/bin/env python3
"""Set an Azure Data Factory linked service integration runtime.

Use this before ARM deployment when an environment parameter file or generated
ADF template still points a linked service at an old self-hosted IR.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


LINKED_SERVICE_TYPE = "microsoft.datafactory/factories/linkedservices"
DEFAULT_LINKED_SERVICE = "ls_snowflake"
DEFAULT_OLD_IR = "SHIR-eunl01wsshir3"
DEFAULT_TARGET_IR = "AHIRVNET01"


def normalize_resource_type(resource_type: str) -> str:
    return resource_type.replace("\\", "/").strip("/").lower()


def is_linked_service_resource(resource: dict[str, Any]) -> bool:
    resource_type = resource.get("type")
    return (
        isinstance(resource_type, str)
        and normalize_resource_type(resource_type) == LINKED_SERVICE_TYPE
    )


def adf_name_matches(value: Any, target_name: str) -> bool:
    if not isinstance(value, str):
        return False

    normalized = value.lower()
    target = target_name.lower()

    if normalized == target or normalized.endswith(f"/{target}"):
        return True

    # ADF publish templates commonly emit concat expressions containing
    # '/linked_service_name'.
    return bool(re.search(rf"/{re.escape(target)}(['\"\]\)])", value, re.IGNORECASE))


def should_update_parameter(
    parameter_name: str,
    parameter_value: Any,
    linked_service: str,
    old_ir: str | None,
) -> bool:
    if not isinstance(parameter_value, str):
        return False

    name = parameter_name.lower()
    if linked_service.lower() not in name:
        return False

    if old_ir and parameter_value.lower() == old_ir.lower():
        return True

    return (
        "connectvia" in name
        or "integrationruntime" in name
        or "integration_runtime" in name
        or name.endswith("_ir")
    )


def set_connect_via(properties: dict[str, Any], target_ir: str) -> bool:
    connect_via = properties.get("connectVia")
    if not isinstance(connect_via, dict):
        properties["connectVia"] = {
            "referenceName": target_ir,
            "type": "IntegrationRuntimeReference",
        }
        return True

    changed = False
    if connect_via.get("referenceName") != target_ir:
        connect_via["referenceName"] = target_ir
        changed = True

    if connect_via.get("type") != "IntegrationRuntimeReference":
        connect_via["type"] = "IntegrationRuntimeReference"
        changed = True

    return changed


def update_template_parameters(
    parameters: Any,
    linked_service: str,
    old_ir: str | None,
    target_ir: str,
) -> list[str]:
    if not isinstance(parameters, dict):
        return []

    updated: list[str] = []
    for parameter_name, parameter_definition in parameters.items():
        if not isinstance(parameter_definition, dict):
            continue

        if should_update_parameter(
            parameter_name,
            parameter_definition.get("defaultValue"),
            linked_service,
            old_ir,
        ):
            parameter_definition["defaultValue"] = target_ir
            updated.append(parameter_name)

    return updated


def update_parameter_file(
    parameter_file: dict[str, Any],
    linked_service: str,
    old_ir: str | None,
    target_ir: str,
) -> list[str]:
    parameters = parameter_file.get("parameters")
    if not isinstance(parameters, dict):
        return []

    updated: list[str] = []
    for parameter_name, parameter_definition in parameters.items():
        if not isinstance(parameter_definition, dict):
            continue

        if should_update_parameter(
            parameter_name,
            parameter_definition.get("value"),
            linked_service,
            old_ir,
        ):
            parameter_definition["value"] = target_ir
            updated.append(parameter_name)

    return updated


def update_adf_document(
    document: dict[str, Any],
    linked_service: str,
    old_ir: str | None,
    target_ir: str,
) -> dict[str, list[str]]:
    updated = {"linkedServices": [], "templateParameters": []}

    resources = document.get("resources")
    if isinstance(resources, list):
        for resource in resources:
            if not isinstance(resource, dict) or not is_linked_service_resource(resource):
                continue

            if not adf_name_matches(resource.get("name"), linked_service):
                continue

            properties = resource.setdefault("properties", {})
            if not isinstance(properties, dict):
                raise ValueError(f"Linked service {linked_service} properties must be an object.")

            if set_connect_via(properties, target_ir):
                updated["linkedServices"].append(linked_service)

        updated["templateParameters"].extend(
            update_template_parameters(
                document.get("parameters"),
                linked_service,
                old_ir,
                target_ir,
            )
        )
        return updated

    # Support raw ADF linked service JSON checked into collaboration branches:
    # {"name": "ls_snowflake", "properties": {...}}
    if adf_name_matches(document.get("name"), linked_service):
        properties = document.setdefault("properties", {})
        if not isinstance(properties, dict):
            raise ValueError(f"Linked service {linked_service} properties must be an object.")

        if set_connect_via(properties, target_ir):
            updated["linkedServices"].append(linked_service)

    return updated


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as input_file:
        document = json.load(input_file)

    if not isinstance(document, dict):
        raise ValueError(f"{path} does not contain a JSON object.")

    return document


def write_json(path: Path, document: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as output_file:
        json.dump(document, output_file, indent=2)
        output_file.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Point an ADF linked service at the expected integration runtime."
    )
    parser.add_argument("template", type=Path, help="ADF ARM template or raw linked service JSON.")
    parser.add_argument(
        "--parameters",
        action="append",
        type=Path,
        default=[],
        help="ADF ARM parameter file to update. Repeat for dev, qat, and prod files.",
    )
    parser.add_argument(
        "--linked-service",
        default=DEFAULT_LINKED_SERVICE,
        help=f"Linked service name to update. Defaults to {DEFAULT_LINKED_SERVICE}.",
    )
    parser.add_argument(
        "--old-integration-runtime",
        default=DEFAULT_OLD_IR,
        help=f"Old IR value to replace. Defaults to {DEFAULT_OLD_IR}.",
    )
    parser.add_argument(
        "--integration-runtime",
        default=DEFAULT_TARGET_IR,
        help=f"Target IR reference name. Defaults to {DEFAULT_TARGET_IR}.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    template = read_json(args.template)
    updates = update_adf_document(
        template,
        args.linked_service,
        args.old_integration_runtime,
        args.integration_runtime,
    )
    write_json(args.template, template)

    for parameter_path in args.parameters:
        parameter_file = read_json(parameter_path)
        updated_parameters = update_parameter_file(
            parameter_file,
            args.linked_service,
            args.old_integration_runtime,
            args.integration_runtime,
        )
        write_json(parameter_path, parameter_file)
        if updated_parameters:
            print(
                f"{parameter_path}: updated parameters "
                + ", ".join(sorted(updated_parameters))
            )
        else:
            print(f"{parameter_path}: no matching parameters found.")

    if updates["linkedServices"]:
        print(
            f"{args.template}: set {args.linked_service} connectVia.referenceName "
            f"to {args.integration_runtime}."
        )
    else:
        print(f"{args.template}: no {args.linked_service} linked service resource found.")

    if updates["templateParameters"]:
        print(
            f"{args.template}: updated template parameter defaults "
            + ", ".join(sorted(updates["templateParameters"]))
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
