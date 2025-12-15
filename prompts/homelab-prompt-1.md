Research and design an advanced 'Zero-Touch' provisioning workflow for an existing 3-node Proxmox cluster backed by Ceph, optimizing for a specific stack: OpenTofu (using the `bpg/proxmox` provider), Scalr (remote backend), Ansible, and Infisical (secrets management).

Format the output as a technical deep-dive document covering the following:

1. **Secret Injection Strategy (Infisical Integration)**:
   - Analyze the security and operational trade-offs of different integration patterns: using the Infisical OpenTofu/Terraform provider directly versus injecting secrets as environment variables into the Scalr run environment.
   - Determine the best practice for passing Infisical-managed SSH keys and API tokens into the Ansible runtime without writing them to disk.

2. **OpenTofu & `bpg/proxmox` Optimization**:
   - Identify specific resource configurations in the `bpg/proxmox` provider that maximize performance for Ceph-backed VMs (e.g., `scsi-single` controller types, `iothread`, `discard`, and `aio` settings).
   - Research the current capabilities of `bpg/proxmox` for managing Proxmox SDN (Software Defined Network) zones and SNAT configurations to isolate homelab projects.

3. **Scalr & State Management**:
   - Propose a workspace architecture in Scalr that efficiently handles dependencies (e.g., a 'base-infra' workspace for SDN/Storage tags vs. 'app-cluster' workspaces).
   - Evaluate methods for Ansible to consume the OpenTofu state from Scalr: compare using the `terraform-inventory` tool against Scalr's state outputs versus using the Proxmox dynamic inventory plugin filtered by OpenTofu-managed tags.

4. **CI/CD Pipeline Architecture**:
   - Design a reference pipeline steps (assuming GitHub Actions) that orchestrates this stack: Authenticate Infisical -> Plan in Scalr -> Apply -> Dynamic Inventory Generation -> Ansible Configure.
   - specifically address how to handle 'Day 2' operations, such as resizing a Ceph disk in OpenTofu and ensuring the file system expansion is handled automatically by Ansible.

5. **Gap Analysis**:
   - Highlight known limitations of the `bpg/proxmox` provider specifically regarding existing Ceph pools or LXC unprivileged container mapping, and provide workarounds using local-exec hooks or Ansible.

## CLI Version
```bash
mise run start -- "Research and design a Zero-Touch provisioning workflow for a 3-node Proxmox/Ceph cluster using OpenTofu (bpg/proxmox), Scalr, Ansible, and Infisical. Cover: 1. Infisical secret injection patterns. 2. bpg/proxmox optimization for Ceph & SDN. 3. Scalr workspace design & Ansible inventory integration. 4. GitHub Actions CI/CD pipeline & Day 2 ops. 5. Gap analysis/workarounds for bpg/proxmox. Output as a technical deep-dive." --output report.md
```
