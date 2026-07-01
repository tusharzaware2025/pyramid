import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "set_adf_linked_service_ir.py"
SPEC = importlib.util.spec_from_file_location("set_adf_linked_service_ir", SCRIPT_PATH)
set_adf_linked_service_ir = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(set_adf_linked_service_ir)


class SetAdfLinkedServiceIrTests(unittest.TestCase):
    def test_updates_snowflake_linked_service_in_arm_template(self):
        template = {
            "parameters": {
                "ls_snowflake_properties_connectVia_referenceName": {
                    "type": "string",
                    "defaultValue": "SHIR-eunl01wsshir3",
                }
            },
            "resources": [
                {
                    "type": "Microsoft.DataFactory/factories/linkedservices",
                    "apiVersion": "2018-06-01",
                    "name": "[concat(parameters('factoryName'), '/ls_snowflake')]",
                    "properties": {
                        "type": "SnowflakeV2",
                        "connectVia": {
                            "referenceName": "[parameters('ls_snowflake_properties_connectVia_referenceName')]",
                            "type": "IntegrationRuntimeReference",
                        },
                    },
                },
                {
                    "type": "Microsoft.DataFactory/factories/linkedservices",
                    "apiVersion": "2018-06-01",
                    "name": "[concat(parameters('factoryName'), '/ls_adls')]",
                    "properties": {
                        "type": "AzureBlobFS",
                        "connectVia": {
                            "referenceName": "SHIR-eunl01wsshir3",
                            "type": "IntegrationRuntimeReference",
                        },
                    },
                },
            ],
        }

        updates = set_adf_linked_service_ir.update_adf_document(
            template,
            "ls_snowflake",
            "SHIR-eunl01wsshir3",
            "AHIRVNET01",
        )

        self.assertEqual(updates["linkedServices"], ["ls_snowflake"])
        self.assertEqual(
            updates["templateParameters"],
            ["ls_snowflake_properties_connectVia_referenceName"],
        )
        self.assertEqual(
            template["resources"][0]["properties"]["connectVia"]["referenceName"],
            "AHIRVNET01",
        )
        self.assertEqual(
            template["parameters"]["ls_snowflake_properties_connectVia_referenceName"][
                "defaultValue"
            ],
            "AHIRVNET01",
        )
        self.assertEqual(
            template["resources"][1]["properties"]["connectVia"]["referenceName"],
            "SHIR-eunl01wsshir3",
        )

    def test_updates_environment_parameter_file_values(self):
        parameter_file = {
            "parameters": {
                "ls_snowflake_properties_connectVia_referenceName": {
                    "value": "SHIR-eunl01wsshir3"
                },
                "ls_adls_properties_connectVia_referenceName": {
                    "value": "SHIR-eunl01wsshir3"
                },
            }
        }

        updated = set_adf_linked_service_ir.update_parameter_file(
            parameter_file,
            "ls_snowflake",
            "SHIR-eunl01wsshir3",
            "AHIRVNET01",
        )

        self.assertEqual(updated, ["ls_snowflake_properties_connectVia_referenceName"])
        self.assertEqual(
            parameter_file["parameters"]["ls_snowflake_properties_connectVia_referenceName"][
                "value"
            ],
            "AHIRVNET01",
        )
        self.assertEqual(
            parameter_file["parameters"]["ls_adls_properties_connectVia_referenceName"][
                "value"
            ],
            "SHIR-eunl01wsshir3",
        )

    def test_adds_connect_via_to_raw_linked_service_json(self):
        linked_service = {
            "name": "ls_snowflake",
            "properties": {
                "type": "SnowflakeV2",
                "typeProperties": {"accountIdentifier": "example"},
            },
        }

        updates = set_adf_linked_service_ir.update_adf_document(
            linked_service,
            "ls_snowflake",
            "SHIR-eunl01wsshir3",
            "AHIRVNET01",
        )

        self.assertEqual(updates["linkedServices"], ["ls_snowflake"])
        self.assertEqual(
            linked_service["properties"]["connectVia"],
            {
                "referenceName": "AHIRVNET01",
                "type": "IntegrationRuntimeReference",
            },
        )


if __name__ == "__main__":
    unittest.main()
