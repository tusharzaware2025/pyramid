import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "filter_adf_arm_template.py"
SPEC = importlib.util.spec_from_file_location("filter_adf_arm_template", SCRIPT_PATH)
filter_adf_arm_template = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(filter_adf_arm_template)


class FilterAdfArmTemplateTests(unittest.TestCase):
    def test_removes_managed_private_endpoint_resources(self):
        template = {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "parameters": {
                "factoryName": {"type": "string"},
                "mpe_adls_global_raw_properties_privateLinkResourceId": {"type": "string"},
            },
            "resources": [
                {
                    "type": "Microsoft.DataFactory/factories/managedVirtualNetworks",
                    "apiVersion": "2018-06-01",
                    "name": "[concat(parameters('factoryName'), '/default')]",
                },
                {
                    "type": "Microsoft.DataFactory/factories/managedVirtualNetworks/managedPrivateEndpoints",
                    "apiVersion": "2018-06-01",
                    "name": "[concat(parameters('factoryName'), '/default/mpe_adls_global_raw')]",
                    "dependsOn": [
                        "[concat(variables('factoryId'), '/managedVirtualNetworks/default')]"
                    ],
                    "properties": {
                        "privateLinkResourceId": "[parameters('mpe_adls_global_raw_properties_privateLinkResourceId')]",
                        "groupId": "dfs",
                    },
                },
                {
                    "type": "Microsoft.DataFactory/factories/pipelines",
                    "apiVersion": "2018-06-01",
                    "name": "[concat(parameters('factoryName'), '/pipeline_copy_raw')]",
                    "dependsOn": [
                        "[concat(variables('factoryId'), '/managedVirtualNetworks/default/managedPrivateEndpoints/mpe_adls_global_raw')]",
                        "[concat(variables('factoryId'), '/datasets/ds_raw')]",
                    ],
                },
            ],
        }

        filtered_template, removed_names = (
            filter_adf_arm_template.remove_managed_private_endpoints(template)
        )

        self.assertEqual(removed_names, ["mpe_adls_global_raw"])
        self.assertEqual(len(filtered_template["resources"]), 2)
        self.assertNotIn(
            "managedPrivateEndpoints",
            "\n".join(resource["type"] for resource in filtered_template["resources"]),
        )
        self.assertEqual(
            filtered_template["resources"][1]["dependsOn"],
            ["[concat(variables('factoryId'), '/datasets/ds_raw')]"],
        )
        self.assertIn(
            "mpe_adls_global_raw_properties_privateLinkResourceId",
            filtered_template["parameters"],
        )

    def test_leaves_templates_without_managed_private_endpoints_unchanged(self):
        template = {
            "resources": [
                {
                    "type": "Microsoft.DataFactory/factories/pipelines",
                    "name": "factory/pipeline_copy_raw",
                }
            ]
        }

        filtered_template, removed_names = (
            filter_adf_arm_template.remove_managed_private_endpoints(template)
        )

        self.assertEqual(removed_names, [])
        self.assertIs(filtered_template, template)


if __name__ == "__main__":
    unittest.main()
