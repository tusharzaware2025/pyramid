# pyramid

## Azure Data Factory CI/CD

Managed private endpoints (MPEs) should be created and approved separately in
each Azure Data Factory environment. Do not redeploy them through the normal ADF
ARM template promotion workflow; ARM deployments can fail with `Invalid payload`
when an existing MPE has environment-specific target properties.

Before running `azure/arm-deploy@v2`, filter the generated ADF ARM template:

```yaml
- name: Remove ADF managed private endpoints from ARM template
  run: python3 scripts/filter_adf_arm_template.py path/to/ARMTemplateForFactory.json

- name: Deploy ADF ARM template
  uses: azure/arm-deploy@v2
  with:
    resourceGroupName: ${{ secrets.AZURE_RESOURCE_GROUP }}
    template: path/to/ARMTemplateForFactory.json
    parameters: path/to/ARMTemplateParametersForFactory.json
```

The filter removes only resources of type
`Microsoft.DataFactory/factories/managedVirtualNetworks/managedPrivateEndpoints`
and leaves template parameters intact so existing parameter files continue to
work.
