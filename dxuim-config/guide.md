#sample command in UAT
#reference https://techdocs.broadcom.com/us/en/ca-enterprise-software/it-operations-management/ca-unified-infrastructure-management-probes/GA/probe-development-tools/restful-web-services/uimapi-apis/uimapi-call-reference.html

curl -k -u accountsvcid -XPUT "https://1.1.1.1:8443/uimapi/probes/DXUIM/ulnstapor0a/ulelkapor0a/processes/config" -H "Content-Type: application/json" -d '[{ "encrypt": "false", "key": "/setup/loglevel", "value": "1" }]'

url endpoint: "/uimapi/probes/{domain}/{hub}/{robot}/{probe}/config"

domain: DXUIM
hub: ulnstapor0a
robot: ulelkapor0a
probe: processes

## metadata convention (new)

So the sync job can tell the requester whether activation succeeded or
failed (see ansible/roles/notify_requester), every new probe config file
should carry a sibling `metadata` key alongside `probeConfigKeys`:

```json
{
  "probeConfigKeys": [ ... ],
  "metadata": {
    "requestedBy": "user:default/jdoe",
    "approvedBy": "user:default/lead-sre"
  }
}
```

This is stripped out before the config is PUT to DX UIM — it's never
sent to the probe, just read by Ansible to know who to notify. Files
committed before this convention existed (e.g. the original
processes.json) don't have it; the sync still runs, it just can't notify
anyone for those.

## catalog-info.yaml convention (new)

Every robot folder should also carry a `catalog-info.yaml` (see
`UAT/ulaeiapos0a/catalog-info.yaml` for the real example) so the robot
shows up in Backstage's Catalog — that Catalog view *is* the "overall
asset for alerts configured," there's no separate inventory to build or
maintain. This is what gives the robot a Grafana tab, an owner, and a
lifecycle, the same way the ELK skeleton does for microservices.

Important: Ansible only ever reads from Bitbucket (see
mock/branching-strategy.html) — it never commits anything back. So
unlike the ELK path, where the Scaffolder template generates
catalog-info.yaml automatically, this file currently has to be authored
by hand alongside the probe configs, in the same commit. There's no DX
UIM Scaffolder template yet — if that gets built later (mirroring
microservice-keyword-alert), it should generate this file too, exactly
like the ELK skeleton does.
