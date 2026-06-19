# EICS Release Management Runbook

## Release Overview

This is the EICS Release Management Runbook for the first production deployment of the MVP data product across Azure, Azure Data Factory, Snowflake, Azure Analysis Services, and Power BI.

The purpose of this Runbook is to provide the Implementation, Backout, Testing, Impact, and Operational validation plan for promotion to Production.

As the deployment is performed across data platform, engineering, BI, and network components, this runbook provides the end-to-end sequence required for coordinated production cutover.

The Release team will ensure that this runbook is attached to the relevant Release Change as logged in SNI or the approved change management system.

## Release Metadata

| Field | Value |
| --- | --- |
| POD | Data Platform / MVP Data Product |
| Business / Value Stream | MVP Data Product |
| Release Type | Special / First Production Deployment |
| Release Name | Azure ADF to Snowflake MVP Data Product Production Deployment |
| Change Reference | TBD - attach approved change record |
| Demand / RITM Reference | TBD |
| Application / Platform | Azure Data Factory, Azure Storage, SAP HANA source integration, Snowflake, Azure Analysis Services, Power BI |
| Source Systems | SAP HANA and Azure Storage Account in another Azure subscription |
| Target Platform | Snowflake Production database in same Snowflake account as Dev/Test/Prod |
| Reporting Path | Power BI -> Azure Analysis Services cube -> Snowflake over Private Link |
| Network Connectivity | Private Link, firewall controls, Zscaler controls |
| Production Azure Subscription | Production subscription, separate from Dev/Test subscriptions |
| Dev/Test Azure Subscriptions | Separate non-production subscriptions |
| Snowflake Environments | Dev, Test, and Prod in the same Snowflake account |
| Requested Template | RUNBOOK_TEMPLATE_20251114_GMNC_US (1).docx |

## Roles and Responsibilities

| Role / Area | Owner |
| --- | --- |
| Platform deployment | Tushar |
| Engineering run and technical testing | James |
| Power BI / reporting testing | Ajith |
| Network readiness and troubleshooting | Network Team |
| Change coordination | Release Manager / Change Owner - TBD |
| Snowflake DBA / Admin | Tushar / Platform Team - confirm named approver |
| Azure Data Factory CI/CD | Tushar / Engineering Team - confirm named approver |
| Business sign-off | Business Owner - TBD |

## Environment Summary

| Layer | Dev / Test | Production |
| --- | --- | --- |
| Azure subscription | Separate non-production subscription(s) | Separate production subscription |
| ADF | Dev/Test factory and linked services functional | First-time Production deployment. Production pipelines/triggers are not present yet and will be created by CI/CD with triggers disabled initially. |
| SAP HANA connectivity | Functional through approved network path | Must be validated from production integration runtime/network path |
| Azure Storage source | Functional from another subscription | Must validate cross-subscription access, firewall, identity, and Private Endpoint/DNS |
| Snowflake | Dev/Test databases in same account | First-time Production database deployment. Production objects/data are not present yet. |
| Snowflake data | Dev has full historical load; Test to be refreshed from Dev clone | Prod to be created from the approved Dev/Test clone path |
| RBAC | Dev/Test functional | Prod RBAC to be synchronized after clone |
| Azure Analysis Services | Separate Azure subscription, connected by Private Link | Production cube points to production Snowflake objects through Private Link |
| Power BI | Functional via Azure Analysis Services | Validate reports through cube only; no direct Power BI-to-Snowflake access |
| Network | Private Link, firewall, Zscaler in place for Dev/Test | Production Private Link, DNS, firewall, and Zscaler policy must be validated |

## Deployment Principles

1. Production cutover must follow an approved change window.
2. No production data load, clone, RBAC sync, ADF promotion, cube refresh, or Power BI validation starts until the change is approved and all owners are available.
3. Snowflake Production must not be exposed directly to Power BI. Reporting validation must occur through Azure Analysis Services.
4. All connectivity checks must use production network paths, Private Link, production DNS resolution, firewall policy, and Zscaler policy.
5. The Dev database is the source of the full historical data clone. The planned sequence is Dev to Test validation, then Prod creation/refresh after Test validation.
6. RBAC must be applied after database clone because cloned database objects do not replace environment-level access governance requirements.
7. This is a first-time Production deployment. No existing Production Snowflake database objects or ADF production pipelines/triggers are expected. If unexpected Production assets are found, pause and confirm ownership before proceeding.
8. Backout before go-live means disabling or removing newly deployed Production assets and not releasing reporting to users; there is no prior Production data pipeline to restore.
9. Every deployment command, pipeline run, clone statement, RBAC statement, and validation result must be logged with timestamp, executor, and evidence link.

# Section 1 - Implementation Plan

## Pre-Deployment Entry Criteria

| Check | Expected Result | Owner | Status |
| --- | --- | --- | --- |
| Approved change record exists | Approved for production implementation | Release Manager / Change Owner | TBD |
| Deployment window confirmed | All participants available | Release Manager / Change Owner | TBD |
| Dev historical load complete | Dev Snowflake database contains full history and latest approved load | James | TBD |
| Test validation complete | Test was cloned/refreshed from Dev and validated successfully | James | TBD |
| Source systems stable | SAP HANA and Azure Storage source availability confirmed | James | TBD |
| ADF first Production release artifact approved | CI/CD artifact/version identified for initial Production pipeline deployment | Tushar | TBD |
| Snowflake bootstrap scripts approved | Database clone/create, RBAC, grants, warehouse, and validation scripts reviewed | Tushar | TBD |
| Production Azure prerequisites ready | Production ADF instance, managed identities, Key Vault references, private endpoints, DNS, and firewall rules ready | Tushar / Network Team | TBD |
| Azure Analysis Services prerequisites ready | Production cube connection strings/credentials available and approved | Ajith | TBD |
| Power BI validation users ready | Report testers identified and access available | Ajith | TBD |
| First-time deployment backout approval confirmed | Stop/disable/remove-new-assets approach and decision authority confirmed | Release Manager / Change Owner | TBD |

## Implementation Steps

| Step | Implementation Step | Implementer | Evidence / Notes |
| --- | --- | --- | --- |
| 1 | Open deployment bridge and confirm change approval, implementation window, participants, communication channel, and escalation path. | Release Manager / Change Owner | Record bridge details and attendees. |
| 2 | Announce deployment start to stakeholders and place any dependent reporting or data refresh expectations on hold. | Release Manager / Change Owner | Communication sent. |
| 3 | Confirm this is a first-time Production deployment: no existing Production Snowflake database/data objects and no existing Production ADF pipelines/triggers are expected. If any unexpected Production assets exist, pause and confirm ownership before continuing. | Tushar / James | Empty-state confirmation captured. |
| 4 | Validate production Snowflake private connectivity from approved Azure production network path and Azure Analysis Services subscription path. | Network Team | Confirm Private Link endpoint, DNS resolution, routing, firewall, and Zscaler policy. |
| 5 | Validate production ADF prerequisites: managed private endpoints, managed identity, Key Vault references, integration runtime, and firewall allow rules for SAP HANA, Azure Storage source, and Snowflake. | Tushar / Network Team | Prerequisite checks pass before code deployment. |
| 6 | Confirm Dev Snowflake database is the approved historical source and has completed data reconciliation checks. | James | Capture reconciliation summary. |
| 7 | Refresh Test from Dev using Snowflake zero-copy clone only if final Test validation is not already complete. | Tushar | Example: CREATE OR REPLACE DATABASE TEST_DB CLONE DEV_DB; |
| 8 | Validate Test after clone/RBAC if Step 7 was executed: row counts, min/max dates, duplicate checks, rejected records, and representative business queries. | James | Test validation evidence attached. |
| 9 | Obtain go/no-go approval to proceed to Production creation. | Release Manager / Change Owner with Tushar, James, Ajith, Network Team | Decision recorded. |
| 10 | Prepare Production Snowflake parameters: target database name, schema names, warehouse name, role names, service accounts, and environment-specific variables. | Tushar | Parameter sheet attached. |
| 11 | Create Production Snowflake database from the approved source using Snowflake clone strategy. Because Production is empty, use CREATE DATABASE rather than replacing an existing Production database. | Tushar | Example: CREATE DATABASE PROD_DB CLONE DEV_DB; or CREATE DATABASE PROD_DB CLONE TEST_DB; |
| 12 | Apply Production RBAC after clone: required roles, grants, future grants, warehouse access, ADF service account access, Azure Analysis Services access, admin access, and reporting read-only access. | Tushar | RBAC execution log and grant validation queries. |
| 13 | Validate Production Snowflake access for ADF, Azure Analysis Services cube, admin, engineering read, and reporting read roles. | Tushar / James | Record role-specific query evidence. |
| 14 | Deploy ADF code to Production using CI/CD for the first time. Deploy linked services, datasets, dataflows, pipelines, global parameters, integration runtime references, and triggers in disabled state. | Tushar | CI/CD run URL and artifact version. |
| 15 | Validate ADF production linked services without enabling schedules: SAP HANA, Azure Storage source subscription, Snowflake, Key Vault, integration runtime, and managed private endpoints. | Tushar / James / Network Team | All connection tests pass. |
| 16 | Run one controlled/manual ADF smoke load or validation pipeline into Production landing/staging objects. | James | Confirm load status and no duplicate/unexpected writes. |
| 17 | Run Production data validation after smoke load: source-to-target counts, sample business keys, date range, audit columns, load control tables, error tables, rejected records, Snowflake query history, and warehouse usage. | James | Attach validation result. |
| 18 | Enable only the required production ADF triggers/schedules after smoke validation approval. | Tushar | Trigger names and enabled timestamp recorded. |
| 19 | Configure basic production monitoring: ADF alerts, Snowflake query/load failure checks, warehouse/resource monitor checks, and support escalation contacts. | Tushar / James | Monitoring evidence attached. |
| 20 | Update Azure Analysis Services cube connection to production Snowflake endpoint/database/schema/warehouse/role through Private Link. Confirm credentials are stored securely and not embedded in reports. | Ajith / Tushar / Network Team | Connection and credential evidence. |
| 21 | Process or refresh the Azure Analysis Services cube against production Snowflake. | Ajith | Refresh/process job result. |
| 22 | Validate Power BI reports through Azure Analysis Services only. Confirm no direct Power BI-to-Snowflake connection is used. | Ajith | Report screenshots, dataset lineage, and query validation. |
| 23 | Execute business-facing report validation: filters, measures, totals, row-level security if applicable, latest refresh timestamp, and comparison to Test/UAT baseline. | Ajith / Business Tester | Evidence and sign-off captured. |
| 24 | Confirm network production steady state: Private Link status, private DNS resolution, firewall logs, Zscaler logs, denied traffic review, and no public endpoint dependency. | Network Team | Network validation record. |
| 25 | Announce implementation complete and attach evidence to the change record: CI/CD run, Snowflake clone/RBAC scripts, validation output, cube refresh result, Power BI evidence, network checks, approvals, and sign-offs. | Release Manager / Change Owner | Communication sent and evidence complete. |

## Production Cutover Checklist

| Area | Validation Item | Owner | Pass / Fail |
| --- | --- | --- | --- |
| Snowflake clone | Production database created/refreshed from approved Dev/Test source | Tushar | TBD |
| Snowflake RBAC | Production access synchronized and validated | Tushar | TBD |
| ADF first deployment | CI/CD completed successfully and triggers initially deployed disabled | Tushar | TBD |
| ADF connectivity | SAP HANA, Azure Storage, Snowflake, Key Vault tests passed | James / Tushar | TBD |
| ADF run | Smoke load and first scheduled load successful | James | TBD |
| Network | Private Link, DNS, firewall, and Zscaler validated | Network Team | TBD |
| Azure Analysis Services | Cube connects to production Snowflake through Private Link | Ajith | TBD |
| Power BI | Reports validated through cube and signed off | Ajith | TBD |
| Monitoring | Alerts and runbooks enabled | Tushar / James | TBD |

# Section 2 - Backout Plan

## Backout Decision Criteria

Backout will be considered if one or more of the following occurs and cannot be remediated within the approved change window:

1. Production Snowflake clone fails or creates inconsistent production objects.
2. RBAC sync fails and required service accounts or users cannot access production safely.
3. First Production ADF deployment fails and cannot be corrected during the change window.
4. Production ADF cannot connect to SAP HANA, source Azure Storage, Key Vault, or Snowflake.
5. Private Link, DNS, firewall, or Zscaler controls block production traffic and Network Team cannot remediate during the window.
6. Azure Analysis Services cube cannot connect to production Snowflake.
7. Power BI reports show materially incorrect results or cannot be accessed.
8. Data validation shows critical mismatch, duplicate load, missing history, or unacceptable rejected records.

## Backout Plan

Because this is the first Production deployment, there is no previous Production Snowflake data pipeline, ADF trigger schedule, or Power BI production data path to restore. Backout means stopping the rollout, disabling newly created components, preventing user consumption, and cleaning up or quarantining newly created Production objects if required.

| Step | Backout Plan Step | Implementer | Evidence / Notes |
| --- | --- | --- | --- |
| 1 | Declare backout decision on deployment bridge and record approver, reason, timestamp, and impacted component. | Release Manager / Change Owner | Decision logged. |
| 2 | Do not enable any remaining Production ADF triggers/schedules. If any were enabled, disable them immediately and cancel active runs if safe. | Tushar / James | Trigger and run status captured. |
| 3 | Stop any in-progress cube refresh or report release activity. | Ajith | Cube/report status captured. |
| 4 | Quarantine or drop newly created Production Snowflake database objects if the deployment is not accepted. Quarantine is preferred when evidence is needed for troubleshooting; drop is acceptable when approved by the change owner. | Tushar | Example quarantine: ALTER DATABASE PROD_DB RENAME TO PROD_DB_FAILED_YYYYMMDDHH24MI; |
| 5 | Revoke or disable newly granted Production access for ADF, Azure Analysis Services, reporting, and engineering roles if Production is not going live. | Tushar | Grant cleanup evidence attached. |
| 6 | Leave newly deployed ADF artifacts disabled, or delete them only if the deployment owner confirms cleanup is required. Because there was no previous Production pipeline, no prior ADF version needs to be restored. | Tushar | Disabled/deleted artifact evidence. |
| 7 | Point Azure Analysis Services back to non-production baseline or leave the Production cube/report unpublished until the next deployment attempt. | Ajith / Tushar | Connection/publication status captured. |
| 8 | Confirm Power BI users cannot consume failed or unapproved Production data. | Ajith | Workspace/report access status captured. |
| 9 | Validate network rules remain in the intended private state and no temporary public access was introduced. | Network Team | Network confirmation. |
| 10 | Announce backout complete, confirm Production is not live, and provide remediation/next-step summary. | Release Manager / Change Owner | Communication sent. |
| 11 | Attach backout evidence to the change record. | Release Manager / Change Owner | Change updated. |

## Backout Exit Criteria

| Check | Expected Result | Owner | Status |
| --- | --- | --- | --- |
| Production service not released | Failed/unapproved deployment safely halted before go-live | Release Manager / Change Owner | TBD |
| ADF stable | Newly deployed Production triggers disabled and active runs stopped/cancelled if required | James / Tushar | TBD |
| Snowflake stable | Newly created Production database quarantined/dropped or left inaccessible as approved | Tushar | TBD |
| Reporting stable | Azure Analysis Services and Power BI not pointing users to failed/unapproved Production data | Ajith | TBD |
| Network stable | No unintended public routing or blocked critical private traffic | Network Team | TBD |

# Section 3 - Testing

## Pre-Deployment Testing

| Phase | Step | Yes / No / N/A | Owner / Evidence |
| --- | --- | --- | --- |
| E2E | Was end-to-end testing successfully completed in Dev and Test? | TBD | James to attach validation evidence. |
| E2E | Which team performed technical testing? | TBD | Engineering run and test - James. |
| E2E | Were SAP HANA to ADF to Snowflake load paths validated? | TBD | James. |
| E2E | Was Azure Storage source subscription to ADF to Snowflake path validated? | TBD | James / Network Team. |
| E2E | Was Snowflake Dev to Test clone validated? | TBD | Tushar / James. |
| E2E | Was RBAC sync validated in Test? | TBD | Tushar. |
| E2E | Was Azure Analysis Services connection through Private Link validated in Test? | TBD | Ajith / Network Team. |
| E2E | Was Power BI tested through Azure Analysis Services without direct Snowflake connection? | TBD | Ajith. |
| Security / Network | Were Private Link, firewall, DNS, and Zscaler paths validated for Test and Production readiness? | TBD | Network Team. |
| UAT | Was UAT or business validation completed? | TBD | Ajith / Business Owner. |
| UAT | Were report totals and measures compared to expected baseline? | TBD | Ajith. |
| Sign-off | Was pre-deployment sign-off obtained? | TBD | Change Owner to attach sign-off. |
| Artifacts | Add the link where test artifacts can be found or attach signed-off artifacts to the change. | TBD | Change Owner. |

## Production Smoke Testing

| Step | Test Step | Tester | Expected Result |
| --- | --- | --- | --- |
| 1 | Confirm Snowflake production database exists and expected schemas/tables/views are present. | James / Tushar | Objects available. |
| 2 | Confirm production row counts and date ranges match approved Dev/Test baseline after clone. | James | Counts and ranges match accepted tolerance. |
| 3 | Confirm Snowflake roles and service accounts can access only approved objects. | Tushar | Least-privilege access confirmed. |
| 4 | Confirm ADF linked services connect to SAP HANA, Azure Storage, Key Vault, and Snowflake. | James / Tushar | All tests pass. |
| 5 | Run controlled ADF smoke load. | James | Pipeline succeeds and audit records are correct. |
| 6 | Confirm error/reject tables are empty or contain only known accepted records. | James | No critical errors. |
| 7 | Confirm Snowflake query performance and warehouse sizing are acceptable for validation queries. | James / Tushar | No critical performance issue. |
| 8 | Confirm Azure Analysis Services connects to production Snowflake through Private Link. | Ajith / Network Team | Connection succeeds. |
| 9 | Process or refresh cube. | Ajith | Cube processing succeeds. |
| 10 | Open Power BI report and validate key pages, filters, measures, and latest refresh timestamp. | Ajith | Reports load correctly and values are accepted. |
| 11 | Confirm no direct Power BI to Snowflake connection exists in the production report path. | Ajith | Lineage confirms Power BI -> Azure Analysis Services -> Snowflake. |
| 12 | Confirm firewall and Zscaler logs show expected private traffic and no unexpected denies. | Network Team | No blocking issues. |

## Post-Deployment Testing

| Step | Tester | Test / Validation |
| --- | --- | --- |
| 1 | James | Validate first full or scheduled production ADF run completes successfully. |
| 2 | James | Validate source-to-target reconciliation for SAP HANA and Azure Storage sources. |
| 3 | James | Validate load control/audit tables, rejected records, and duplicate checks. |
| 4 | Tushar | Validate Snowflake RBAC, object ownership, future grants, and service account access. |
| 5 | Tushar | Validate Snowflake monitoring, query history, warehouse usage, and resource monitors. |
| 6 | Network Team | Validate Private Link endpoint health, private DNS, firewall, and Zscaler logs after first load and cube refresh. |
| 7 | Ajith | Refresh/process Azure Analysis Services cube and validate connection to production Snowflake. |
| 8 | Ajith | Validate Power BI report pages, measures, filters, row-level security if applicable, and business totals. |
| 9 | Business Owner / Ajith | Obtain reporting sign-off and attach evidence to change record. |
| 10 | Release Manager / Change Owner | Confirm all post-deployment evidence is attached before change closure. |

## Testing Sign-Off

| Area | Owner | Sign-Off Status | Evidence Link |
| --- | --- | --- | --- |
| Platform deployment | Tushar | TBD | TBD |
| Engineering run and test | James | TBD | TBD |
| Power BI testing | Ajith | TBD | TBD |
| Network validation | Network Team | TBD | TBD |
| Business acceptance | Business Owner - TBD | TBD | TBD |

# Section 4 - Impact

## Downtime and Availability

| Downtime (System Unavailability) | Yes / No / N/A | Details |
| --- | --- | --- |
| Will there be downtime? | No expected end-user downtime | Deployment is expected to be performed with controlled cutover. Reporting users may see stale data until cube refresh completes. |
| Duration of downtime | N/A | If a reporting freeze is required, record start and end time in the change record. |
| Business impact | Limited / controlled | First production deployment; access should be limited to approved users until sign-off. |
| User communication required | Yes | Notify stakeholders before start, at go/no-go, after completion, and after sign-off. |

## Technology Infrastructure Services

| Technology Infrastructure Services (TIS) | Yes / No / N/A | Details |
| --- | --- | --- |
| Will there be an impact to TIS? | Yes | Network, firewall, Private Link, DNS, Zscaler, Azure subscription connectivity, and Snowflake private connectivity must be validated. |
| Required support | Yes | Network Team must be available during implementation and validation. |
| Escalation | Yes | Escalate immediately for DNS, firewall, Private Link, Zscaler, or cross-subscription connectivity failures. |

## Data

| Data Item | Details |
| --- | --- |
| Data upload or download? | Yes. ADF loads data from SAP HANA and Azure Storage source into Snowflake. Snowflake Dev/Test/Prod database clone is also part of deployment. |
| Application/system performance impact | Potential degradation if warehouses are undersized, pipelines are run concurrently, or cube refresh overlaps with full data load. Monitor ADF, Snowflake warehouse usage, and cube processing. |
| Bulk upload required? | Yes. Historical data is already loaded in Dev; Production will be populated by clone. Controlled smoke/incremental production load will follow. |
| Data migration strategy | Snowflake zero-copy clone from approved Dev/Test source, followed by RBAC synchronization and validation. ADF production loads resume after clone and validation. |
| Data migration process | Validate Dev history, clone Dev to Test, validate Test, clone approved source to Production, run RBAC sync, run smoke load, reconcile, then enable schedules. |
| Technology used | Azure Data Factory, Snowflake zero-copy clone, Snowflake RBAC scripts, Azure Analysis Services cube refresh, Power BI report validation, Azure Private Link. |
| Volume | Full historical database clone from Dev plus ongoing production incremental loads. Exact object count, row count, and storage volume to be recorded from Snowflake metadata before deployment. |
| Data quality controls | Row counts, min/max business dates, source-to-target reconciliation, duplicate checks, null critical field checks, audit table checks, rejected record checks. |

## Network and Security Impact

| Area | Impact / Control |
| --- | --- |
| Private Link | Required for Snowflake connectivity from Azure production and Azure Analysis Services subscription. |
| DNS | Private endpoint DNS resolution must resolve to private addresses from production paths. |
| Firewall | Firewall allow rules must permit only approved private traffic paths. |
| Zscaler | Zscaler policy must not block approved private application connectivity. |
| Public access | No public connectivity should be required for production data path. Any exception must be approved before go-live. |
| Secrets | Credentials must be stored in approved secret stores such as Azure Key Vault or Snowflake integrations. No secrets in code, reports, or runbook evidence. |

## Pre-Deployment Checks for Approval - SAP / Data Platform Specific

| Check | Enter Full Details |
| --- | --- |
| a. Any global risk when deployed to production systems during normal operational time? | Medium operational risk because this is the first production deployment and spans Azure, Snowflake, network, cube, and reporting layers. Mitigation: approved change window, bridge, clone strategy, first-time deployment backout plan, and owner availability. |
| b. Any risk on the production system after deployment, considering month-end or critical reporting cycles? | Confirm deployment does not overlap with month-end close, financial reporting, SAP HANA maintenance, storage maintenance, or Power BI executive reporting cycles. |
| c. Impact on integrations? | Yes. ADF integrations with SAP HANA, Azure Storage source, Snowflake, Key Vault, and Azure Analysis Services reporting path must be validated. |
| d. Data migration impact and risk? | Yes. Production will be initialized through Snowflake clone and then loaded by ADF. Risk is mitigated through Dev/Test validation, pre/post reconciliation, and the ability to disable or quarantine newly created Production assets before go-live. |
| e. Successful pre-deployment checks completed? | TBD. Must be marked Yes only after all entry criteria and evidence are complete. |

# Section 5 - Tier 1 Application Impact

## Impacted Tier 1 Applications

| Application | Yes / No | Impact |
| --- | --- | --- |
| SNI | Yes | Change record and deployment evidence will be logged. No runtime application impact expected. |
| Services Portal | No | No direct impact identified. |
| Flow | No | No direct impact identified. |
| SAP | Yes | SAP HANA is a source system. Read/connectivity path must be available; no SAP application change expected. |
| ITSM (LDC and EDC) | No | No direct runtime impact identified beyond change tracking if applicable. |
| Direct | No | No direct impact identified. |
| Manage Centre | No | No direct impact identified. |
| Workday | No | No direct impact identified. |
| Salesforce | No | No direct impact identified. |
| Medallia | No | No direct impact identified. |
| Integration (ServiceGrid, Snaplogic, BizTalk) | No | No impact identified unless upstream/downstream integration ownership confirms dependency. |
| Omnichannel | No | No direct impact identified. |
| Sitecore | No | No direct impact identified. |

## Other Impacted Applications

| Application | Yes / No | Impact |
| --- | --- | --- |
| Azure Data Factory | Yes | Production CI/CD deployment, linked service validation, trigger enablement, and load execution. |
| Azure Storage source account | Yes | Source data read access from another Azure subscription must be validated. |
| Azure Key Vault | Yes | Secret references for ADF and related services must resolve from production. |
| Snowflake | Yes | Dev/Test/Prod database clone, Production database creation/refresh, RBAC sync, and validation. |
| Azure Analysis Services | Yes | Cube connection to Production Snowflake through Private Link and cube processing/refresh. |
| Power BI | Yes | Reports validated through Azure Analysis Services. No direct Snowflake connectivity. |
| Firewall / Zscaler / Private DNS | Yes | Required for private network connectivity and production validation. |

# Communication Plan

| Event | Audience | Owner | Channel / Evidence |
| --- | --- | --- | --- |
| Deployment start | Stakeholders, platform, engineering, BI, network | Release Manager / Change Owner | Email/Teams/change note |
| Test validation go/no-go | Deployment bridge | Release Manager / Change Owner | Bridge notes |
| Production clone complete | Deployment bridge | Tushar | Bridge notes/change evidence |
| ADF deployment complete | Deployment bridge | Tushar | CI/CD link |
| Production smoke test complete | Deployment bridge | James | Test evidence |
| Power BI validation complete | Deployment bridge | Ajith | Report validation evidence |
| Network validation complete | Deployment bridge | Network Team | Network evidence |
| Deployment complete | Stakeholders | Release Manager / Change Owner | Email/Teams/change note |
| Backout invoked, if required | Stakeholders and support teams | Release Manager / Change Owner | Email/Teams/change note |

# Evidence Checklist

| Evidence Item | Owner | Attached |
| --- | --- | --- |
| Approved change record | Release Manager / Change Owner | TBD |
| Production empty-state confirmation | Tushar / James | TBD |
| Dev/Test/Prod clone SQL and result | Tushar | TBD |
| RBAC script and result | Tushar | TBD |
| ADF CI/CD first Production deployment run | Tushar | TBD |
| ADF linked service test results | James / Tushar | TBD |
| SAP HANA source validation | James | TBD |
| Azure Storage source validation | James | TBD |
| Production smoke load result | James | TBD |
| Data reconciliation results | James | TBD |
| Azure Analysis Services connection and refresh result | Ajith | TBD |
| Power BI report validation evidence | Ajith | TBD |
| Private Link/DNS/firewall/Zscaler validation | Network Team | TBD |
| Final sign-off | Release Manager / Change Owner | TBD |

# Go / No-Go Decision Points

| Decision Point | Required Inputs | Decision Owner |
| --- | --- | --- |
| Start production deployment | Approved change, all owners present, pre-checks passed | Change Owner / Release Manager |
| Proceed from Test clone to Production clone | Test clone, RBAC, data validation, and network checks passed | Change Owner with Tushar and James |
| Enable production ADF triggers | Prod clone, RBAC, linked services, smoke load, and validation passed | Change Owner with Tushar and James |
| Refresh Azure Analysis Services cube | Snowflake production and network checks passed | Change Owner with Ajith and Network Team |
| Complete deployment | Engineering, BI, network, and business validation complete | Change Owner / Release Manager |
| Invoke backout | Critical failure in data, access, ADF, network, cube, or reports | Change Owner / Release Manager |

# Open Items to Confirm Before Final Approval

1. Final production Snowflake database name, schema names, warehouse names, and role names.
2. Whether Production should be cloned directly from Dev after Test sign-off or cloned from the validated Test database.
3. Exact ADF CI/CD release artifact version and deployment pipeline name.
4. Exact source SAP HANA connection path and Azure Storage source account name.
5. Azure Analysis Services server/model name and service principal or managed identity details.
6. Power BI workspace, report names, and expected validation users.
7. Change record number, deployment window, and stakeholder distribution list.
8. Business owner and formal sign-off approver.
9. Whether any public endpoint exceptions exist. If yes, document explicit approval and compensating controls.
