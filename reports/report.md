# Zero-Touch Provisioning Architecture for Proxmox/Ceph Clusters: A Technical Deep-Dive

**Key Points**
*   **Hybrid Orchestration Model:** A robust Zero-Touch Provisioning (ZTP) workflow for Proxmox requires a hybrid approach where **Ansible** handles the imperative "Day 0" bootstrapping (cluster formation, Ceph installation, network interface configuration) and **OpenTofu** (via the `bpg/proxmox` provider) manages the declarative "Day 1" resource lifecycle (VMs, SDN subnets, firewall rules).
*   **Secret Management:** **Infisical** serves as the central root of trust, injecting secrets into the pipeline via Universal Auth or OIDC. This eliminates long-lived credentials in code repositories, utilizing the `infisical.vault` Ansible collection and environment variable injection in Scalr.
*   **State & Execution:** **Scalr** acts as the remote state backend and orchestration engine. By utilizing custom runner images (Docker), Scalr can execute both OpenTofu plans and Ansible playbooks within a unified, controlled environment, sharing state data between stages.
*   **SDN & Storage:** The `bpg/proxmox` provider offers superior support for Proxmox SDN (Software Defined Network) compared to legacy providers, enabling the definition of Zones and VNets as code. However, Ceph OSD provisioning remains a gap in the Terraform provider, necessitating Ansible automation for the storage layer.

## 1. Architectural Overview

The provisioning of a hyper-converged infrastructure (HCI) using Proxmox VE and Ceph demands a rigorous separation of concerns between configuration management and infrastructure orchestration. While OpenTofu (a fork of Terraform) excels at defining the desired state of virtual resources, it lacks the imperative logic required to bootstrap a cluster from bare metal. Conversely, Ansible excels at OS-level configuration but struggles with the state management required for complex lifecycle operations.

This architecture leverages **Scalr** as the central command plane, executing a pipeline that integrates **Infisical** for security, **Ansible** for node convergence, and **OpenTofu** (specifically the `bpg/proxmox` provider) for resource provisioning.

### 1.1 The Role of Components
*   **Infisical:** Acts as the secrets vault, providing dynamic injection of SSH keys, API tokens, and passwords into the CI/CD runtime.
*   **Ansible:** Performs "Day 0" operations: installing packages (`pveceph`, `openvswitch`), forming the Proxmox cluster (Corosync), and bootstrapping the Ceph monitors and managers.
*   **OpenTofu (`bpg/proxmox`):** Performs "Day 1" operations: defining SDN Zones, VNets, and provisioning Virtual Machines (VMs) that consume the Ceph storage.
*   **Scalr:** Provides the remote state backend, locking, and the execution environment (runners) where the automation logic resides.

## 2. Infisical Secret Injection Patterns

Securely managing credentials in a ZTP workflow is critical. Hardcoding credentials in `tfvars` or Ansible inventory files is a security anti-pattern. Infisical allows for the dynamic injection of secrets at runtime.

### 2.1 Pattern A: Universal Auth in Scalr Agents
For the Scalr execution environment (which runs inside a Docker container), the most robust authentication method is **Universal Auth** (Client ID and Client Secret). This method is preferred for machine-to-machine communication where an interactive login is not possible [cite: 1, 2].

**Implementation Strategy:**
1.  **Machine Identity:** Create a Machine Identity in Infisical for the Scalr Agent.
2.  **Environment Variables:** In the Scalr Workspace configuration, set `INFISICAL_CLIENT_ID` and `INFISICAL_CLIENT_SECRET` as sensitive shell variables.
3.  **Runtime Injection:** The custom Scalr runner image (discussed in Section 3) includes the Infisical CLI. A wrapper script or Scalr "Pre-init" hook uses these credentials to fetch the Proxmox API Token and SSH keys, exporting them as environment variables (`PROXMOX_VE_API_TOKEN`, `ANSIBLE_SSH_PRIVATE_KEY_FILE`) before OpenTofu or Ansible executes.

### 2.2 Pattern B: Ansible Lookup Plugin (`infisical.vault`)
When Ansible runs (either via Scalr or a separate CI pipeline), it requires access to secrets for tasks such as setting root passwords or joining nodes. The `infisical.vault` collection allows Ansible to retrieve secrets directly during playbook execution [cite: 1, 3].

**Configuration:**
The collection supports Universal Auth. The lookup plugin is used within tasks to fetch specific secrets without writing them to disk.

```yaml
# Example Ansible Task using Infisical Lookup
- name: Retrieve Proxmox Root Password
  ansible.builtin.set_fact:
    pve_root_password: "{{ lookup('infisical.vault.read_secrets', 'PVE_ROOT_PASSWORD', universal_auth_client_id=..., universal_auth_client_secret=...) }}"
```

This pattern ensures that sensitive data exists in memory only for the duration of the specific task requiring it [cite: 3].

### 2.3 Pattern C: GitHub Actions OIDC Integration
For the CI/CD pipeline driving the automation (e.g., linting, testing), **OIDC (OpenID Connect)** is the recommended pattern. This eliminates the need to store long-lived Infisical credentials in GitHub Secrets.

**Workflow:**
1.  **Trust Relationship:** Configure Infisical to trust the GitHub repository's OIDC issuer.
2.  **Action Execution:** Use the `Infisical/secrets-action` in the workflow. The action exchanges the GitHub OIDC token for a short-lived Infisical access token [cite: 4, 5].
3.  **Secret Injection:** The action injects the requested secrets as environment variables into the runner, available for subsequent steps (e.g., `tofu plan`).

## 3. `bpg/proxmox` Optimization for Ceph & SDN

The `bpg/proxmox` provider is distinct from other providers (like Telmate) due to its extensive support for Proxmox's newer features, specifically SDN and direct file management via SSH [cite: 6, 7, 8].

### 3.1 Optimizing for Ceph
While OpenTofu is not ideal for *installing* Ceph (an imperative task), it is excellent for *configuring* the consumption of Ceph storage.

**Repository Management:**
Use the `proxmox_virtual_environment_apt_standard_repository` resource to ensure all nodes are pointed to the correct Ceph repositories (e.g., `ceph-quincy-no-subscription` or enterprise) [cite: 9]. This ensures consistency across the cluster before provisioning begins.

**Disk Provisioning on Ceph:**
When defining VMs, the `disk` block must be optimized for Ceph (RBD).
*   **Datastore:** Point to the Ceph storage pool (e.g., `datastore_id = "ceph-pool"`).
*   **Discard:** Set `discard = "on"` to enable TRIM, allowing Ceph to reclaim unused space [cite: 10, 11].
*   **IO Thread:** Set `iothread = true` to offload disk I/O processing to a separate thread, improving performance for RBD backed drives [cite: 10, 12].
*   **SSD Emulation:** Set `ssd = true` to expose the drive as a non-rotational device to the guest OS [cite: 10].

### 3.2 Software Defined Network (SDN) Configuration
The `bpg/proxmox` provider supports Proxmox SDN resources, allowing for the creation of complex network topologies as code [cite: 8, 13].

**Zone Definition:**
Use `proxmox_virtual_environment_sdn_zone_*` resources. For a private cluster network, a **Simple** or **VLAN** zone is often sufficient.
*   **Simple Zone:** Creates an isolated bridge on each node.
*   **VLAN Zone:** Uses an existing bridge (`vmbr0`) and tags traffic, allowing isolation across the cluster [cite: 14].

**VNet and Subnet Management:**
The provider allows defining VNets (`proxmox_virtual_environment_sdn_vnet`) and Subnets (`proxmox_virtual_environment_sdn_subnet`) with specific CIDR blocks and DHCP ranges [cite: 13].
*   **IPAM:** The provider integrates with the PVE IPAM to track allocated IPs.
*   **Applier Resource:** Crucially, SDN changes in Proxmox are staged. The `proxmox_virtual_environment_sdn_applier` resource is required to trigger the "Apply" action in the SDN controller, pushing changes to the nodes [cite: 12, 13].

## 4. Scalr Workspace Design & Ansible Inventory Integration

Scalr provides the orchestration layer. A monolithic workspace is ill-suited for a 3-node cluster. A layered workspace design is required.

### 4.1 Workspace Strategy
1.  **Layer 0 (Bootstrap):** (Managed via Ansible/Scalr Shell) - Bare metal configuration, Cluster Join, Ceph Install.
2.  **Layer 1 (Infrastructure - OpenTofu):** SDN Zones, Storage Pools, shared resources.
3.  **Layer 2 (Workloads - OpenTofu):** VMs, Kubernetes Nodes.

### 4.2 Custom Runner Image (The "Fat" Runner)
To execute this hybrid workflow, the default Scalr runner is insufficient. A custom Docker image must be built and defined in Scalr using `SCALR_AGENT_CONTAINER_TASK_IMAGE` [cite: 15, 16].

**Dockerfile Requirements:**
*   **Base:** `debian:trixie-slim` or `scalr/runner`.
*   **Tools:**
    *   `opentofu`
    *   `ansible-core` & `ansible-galaxy` (to install collections).
    *   `infisical` (CLI).
    *   `python3`, `pip` (for Ansible modules like `proxmoxer`, `infisicalsdk`) [cite: 2, 17].
    *   `ssh-client` (required by Ansible and `bpg` provider).

### 4.3 Ansible Inventory Integration
Ansible needs to know the IP addresses of the nodes managed by OpenTofu.
*   **Terraform State as Inventory:** Use the `terraform-inventory` plugin or a script that queries the Scalr remote state.
*   **Scalr Integration:** Scalr allows workspaces to share state outputs. The "Infrastructure" workspace outputs the management IPs of the Proxmox nodes. The "Workload" workspace (or an Ansible job) uses `data "terraform_remote_state"` to fetch these IPs [cite: 18, 19].
*   **Dynamic Inventory:** For Day 2 ops, use the `community.general.proxmox` inventory plugin, which queries the Proxmox API directly to find VMs created by OpenTofu [cite: 20].

## 5. GitHub Actions CI/CD Pipeline & Day 2 Ops

The CI/CD pipeline orchestrates the flow from code commit to Scalr execution.

### 5.1 Pipeline Stages
1.  **Validation:**
    *   **Secret Scanning:** Use `Infisical/secrets-check-action` to ensure no raw secrets are committed [cite: 21].
    *   **Linting:** `tflint` for OpenTofu and `ansible-lint` for playbooks.
2.  **Plan/Dry-Run:**
    *   Trigger a Scalr "Speculative Run" (Plan only) via the Scalr CLI or API.
    *   Run Ansible in `--check` mode against the infrastructure.
3.  **Apply (Main Branch):**
    *   Trigger Scalr Apply.
    *   **Post-Apply Hook:** Scalr supports custom hooks. A `post-apply` hook can trigger an Ansible playbook to configure the newly created VMs (e.g., installing K3s on the nodes) [cite: 22].

### 5.2 Day 2 Operations
*   **Updates:** Use Ansible playbooks to perform rolling updates of the Proxmox nodes. The playbook should leverage the `serial: 1` strategy and interact with the Proxmox API to migrate VMs off a node before rebooting [cite: 23, 24].
*   **Scaling:** To add a 4th node, update the Ansible inventory and run the "Bootstrap" playbook (using `proxmox_cluster` module to join), then update the OpenTofu node list for SDN propagation.

## 6. Gap Analysis & Workarounds for `bpg/proxmox`

While `bpg/proxmox` is powerful, it is not a complete replacement for imperative scripting.

### 6.1 Gap: Cluster Bootstrapping
**Issue:** The provider cannot take three standalone Proxmox nodes and merge them into a cluster. It assumes a cluster (or standalone node) exists and has an API endpoint.
**Workaround:** Use the Ansible `community.proxmox.proxmox_cluster` module. This module handles the creation of the cluster on the first node and the joining of subsequent nodes [cite: 25, 26]. This must be the very first step in the ZTP workflow.

### 6.2 Gap: Ceph Installation
**Issue:** There is no `proxmox_ceph_cluster` resource in OpenTofu.
**Workaround:** Use Ansible to run `pveceph install`.
*   **Challenge:** `pveceph install` is interactive.
*   **Solution:** Use `ansible.builtin.command` with `DEBIAN_FRONTEND=noninteractive` or pipe `yes` to the command (`yes | pveceph install`) to automate the installation [cite: 27].

### 6.3 Gap: SSH Requirement for Cloud-Init
**Issue:** The `proxmox_virtual_environment_file` resource (used for uploading custom Cloud-Init user-data) requires SSH access to the Proxmox node; the API token is insufficient [cite: 6, 28, 29].
**Workaround:**
1.  **SSH Configuration:** The Scalr Agent must have the SSH private key injected (via Infisical).
2.  **Permissions:** The SSH user (e.g., `root` or a sudoer) must be configured in the provider block.
3.  **Alternative:** Use `proxmox_virtual_environment_download_file` if the Cloud-Init file can be hosted on a web server accessible by Proxmox, bypassing the need for SSH upload [cite: 30].

### 6.4 Gap: VM ID Conflicts
**Issue:** When creating multiple VMs simultaneously, race conditions can occur in assigning VM IDs if not explicitly defined.
**Workaround:** Explicitly manage VM IDs in OpenTofu code (e.g., using `count.index + 100`) or set `parallelism=1` in the provider configuration to force sequential creation, though this slows down provisioning [cite: 31].

## Conclusion

By combining the declarative power of OpenTofu with the imperative flexibility of Ansible, managed by Scalr and secured by Infisical, a true Zero-Touch Provisioning workflow for Proxmox/Ceph is achievable. The critical success factor lies in the strict sequencing of operations: Ansible must first build the platform (Cluster/Ceph), allowing OpenTofu to consume it (SDN/VMs), with Infisical ensuring that the keys to the kingdom are never exposed in the process.

**Sources:**
1. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMcuc0pUmUO9BBWUkVNDK69hkDY8REYqVA77_sYPX_Xq0PG97dEwGRUY7w3En8Li3f9ZHG3teoDhz3DgQG74Py4reRFJB6T9ZiJM8Q1AmGY1RxolVvFcIih_6KPs9gIKF29Xopqg==)
2. [infisical.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-t4FeYAsOxOkGcoNa69KLqQ-CI5F6Kr-s3z-9YJfFxUOV4kcVlEzRn_iGPSg2QZrXg1mrZ37Nkz7jrQmKb9n1JNJqyu34c2JEuZralNhOMkIN-mLyASSOXCihHVQr4TAa1HS91EU21BgekzAWXLI=)
3. [ansible.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUHNEcSfzBJ5rqPD2tlSVfiE9J2OPA3HT-BEWDlSKMf39TpmGwLY0ZTX2gS35ULZC_FEg9ZW6jBtXN18vpnndFeHZArp_QfafIcDtfWzxR-EDkbxdErIHmc7_UB1vq-TRAhD26X2oiqiOK5jmbQJ5DU2jM4P61_dw5jW4AprzqTQ72S7T2vMapmDxNapIqnA==)
4. [infisical.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbCfMrEU08LgGErpFD74pU_oK63sshOoDDPQPp7Ow_CKB5bgLohg-T2D4YAdsY_iLSt93DMZSA3F3v4UUVkgYssBZTvEYHSX-nf_lT8-WQHt46UQ8euAfk87DRgIoTT-9M-iqECNLLdYLZvzAau29e-WezbTdHiFfTGJqqSNaRfsiCDUkutFnkizLoBiCb)
5. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBRoFcGGX24QkYw9BS3_5Nlil1UAho62N_sDNMSziNA3YsZOCkvbSDOhDrTLBT6px_9gp076xgzA9JU2g00iFcJPVDS15pyWxf9QeqPMrdJHbwSpWgA57dQetOzTWTnqmU)
6. [faun.pub](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGc5fsVBc6JD6nZ9O9EO8xvvq13UQwgXvtN7OV2xCQvxwVjpfdw3DcTrAlNEca9qyZFE5id1Fty9LGDlxxGZC-Y_wd1WhPHbfAqVQ6ePQFmS8-5B1hILghWyorbYRSGIhJNkBr0DvnYWbWg0EwcseDYZn3qR9k0dR1eVU61zIioplT2k2GN9zDMfNeR5rqfMUsUjS3CDBSfhkgWnc=)
7. [proxmox.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGwsVBvv9qx-DSsBN2l5ot-tXQJbbsveNMnX6DBkplYEeO5fEu4IGFMelhATp80qASv7wgZ9kcMHeynIJkuWWT6BzyFg-k48gDc_6ZgoTPr0Rm2ICJeHSDzOQ9LlOEHhqkbKm84iTq3B0kdGT7h6oSinM8-l80zA==)
8. [opentofu.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnHtjmvQcaW35mWXeibZ6ShOLs9plXRaUMwetlo4rbaAfp9Ugho5s1kNhxDNsNyLHjtrnHirtA_pNZkVspEO3yWnmdow3TIVmVk5-zTgc8_jY17OXGPuvMWC7yxQV8RJ8wcTIVqSzJ8GIsuTOnMX6jF1GcoMNenmB05O_72ClGMQSnJ1INby-0-oS5Hc3KB2Ey9_Kfka7SwZFX9e4eNmxZr3s=)
9. [terraform.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQER_vHTBDbitiuNeZ4_O_5L1-sjyqfT8eM5fm_6OuIZ5OYCu4OHwDjLF-fJXDL9eF0yRVJYTuSWnlGgAbzTqA5RQ2FYjKsmYxSy9ej3F0_cKDZOF-HcAM3AVIiXJlKEiWmW1aBk3NnsN5JA_3T8eTlacljSqCDV5HTq3cNkpwheVAdnoxlOQvTLZ3_Iqod4dvcriRnGBZdcywtIXn9xEfv0V0YWj55Ua7dHwf0=)
10. [trfore.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyOUy9ZaFeQ4gNbyPnSdZtz7KcpmEPbwNpXrnSfcZTLBhuAl0FzQOkPjjjfrvBj3xzPsmswFjohMZVtPIwBr79ItSGiwo4FSdoVI0S6yh1jI-VsrOd1tpAJ1x5em1hqW20VcMCyhvLcVhV8GRl-sXzTeZBKuUjUhuvHXzhdjIvnI2UKcEx)
11. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxvBoee1R6-X1A8eURCVVffZUsCVcBpJ_e2qbVNNO__Iao8mMXBv9XfqGJthW1ZTju6OzqFucHABbYwJ7unXwBNgBRx3cYPgK5fhAQdixsVyaQCeNXXmadZnxerz1fyqxRak2kXZ7MPeQvlzUEZSB3lVZG)
12. [terraform.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuoRnUw8MVgBshIFsevgKOAL2KLMjpZEYkcPe1ruw9WQHYGeG0liUi-UshDCCC6ysMIqtqGfvEQcnDp55X2zPec9vRzB1aKaYgTyb2M6xJG82ZbRbb-0QMremhL5QPImFZr-UuFlIN31ATSfcHWeBza-azOLqoB0wqOepzskbCBWTwhlsF-wlW06jMgED5iGj-W0351B8=)
13. [opentofu.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJPPlFb0i38oN6D1DDZFggMhVT37qj8PgDvGTonbNhy1kcm8u95yVv19edMokRTRI1XwTf1XEMcDZVg4R7x5ApPNEr4ZPVOXJDMLzt4La0k7EH7hNsTfIpkOcJnEUA3XJu-MK6PZRAEuNul3oCbBCkXb4DwkyDYEK53vVej1dAFCd18DJEly8O41KtGT1qc9v1OUfrurDCu8RZCA==)
14. [terraform.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvjPDXpy6qv2he0bIDz6atXL7umwawg0QVlWVH1uH_3S53N0OQEI39P7ndnyHRNNvMj4U-1YW89iAAANrCToJ09fxmxN0pB4Yb0VY1BWWquRWV4YbW4ML8tK3QvLJGCSuG50QLVptUI5hjrvUvcETGRf_EhSKmcry5wfI3AV82TH1CHrhBd_NwpqXVuQnUEd4In_u3v0fajTADgiU9MX_f908w3w==)
15. [scalr.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7F-dR_7oK5VvcYTE6tVKyIUZiWZrmtGJlKH2DR9c5o3-v5i1OVDMpkyaD0n96cZhrTeT-lQBUcEio6YjBWtoGHS80qBh396uKfS4y6-WCBxZcUXbKQN4_4twMcWd7)
16. [scalr.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7LSc83CGXEPMXboZMBZcQneMctMmtrMj-tqtbgxcULzZTllnm_3C6IyBj4SxC1OanuiP2iIhchKQoKbWYWtZb4vx5ytSLPeKzbJbxxYd_Z8G0rLsdR7ESCeCx6Eusi1o=)
17. [xda-developers.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQER7Hbd2L-5lXJLOjtb5fym2GdG8NxfFOeXF2F2z44WAvMW3qmvPyat3bWEg2LGmfo04-tPMo76ziK_6G7O3fcFAl9jkaxw7LVhKLGWwZWJ9aAPipOuOPkQsFin8QCCehI5qn2LocvUHAVZ9pUoBt9dLAIk8-fjwzQU0f40Hzep)
18. [scalr.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFP0KGn_fIBL-0I0VHG34olVsoYZ45YMVkTuQQ8nsTsm9EPcKcw_rThNB89V8TCYOvBlg4VdAmOttQgYhE_Vjwr_veJh22EJhjqOG3BxdpLPp_cwDt4cmQ7ygCTMQbYa5yuKZgfaDgk9T8Ny8AbAFG8WMfMNkQ=)
19. [scalr.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9MAfdlF8gyV2U8SHc08EHfEuOhmYzLPx57LTHjdYjH5ITgvLm5dZE368E5v8Gdih1KQCRRYPqqYYaI6OCb2GSNneFT_D9f_NlYTesbVW67Cq94M-Sv9_sE51Ch-j6xvi3JmVNaNlqKk75ywlCcEj-vdBrEWBVcT29qLwqGsUg4XUr62qTitVg8xfkKDDKcj7ofw==)
20. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYTtUosSbPHsYgQ-42EPoarjEJoiZR7SjzDaXDAKuJnoUNNfxYxyWsQY1vqvmvIxf9L5Qb0tDDOOP0_xi1Y62D1U1C1h1KE8icvwhG91yLdURf45WJkukaH0mAZzAU_FqWLXnfJa05MmbYAjxqKfVUAR4Vnelu7REbIPJVBTxlAS2RiXIxvCOxCiNBaMopfqvrUdqmfV2pkYQGQ0T6vDh-3yx6rmk_6vVYR_XjCqj6h2HbRRG6)
21. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQ8MPt2fzTe5x--OMkOnRGrtiWKQ4hcuAvuFADTf68yu_zQ02lBxKstsoMFOHhmBy0DoEads31EDGTjjqaJWXRZ42JzCnwjeVnN3loSz-Ph_XVxX154FSi1vHECaU8U3OGcnM0rmmHOkyGNjaw76e4UFJDP4ZeZw4=)
22. [scalr.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwZ1xycO4mPh14YwL5X2RJ3Xb5uaJejTNm0CLBC0ouiDkXzw7Z9s_j6sDUHePKyK2jvzXUSrQOnCmNXNT7d8p4GeViFFWX8Z3TgRgTTHmaH6pta4BBpcfI2fgp_zexn5LPvUZ6LuKqnO6Imv3h0PuRiREcqhBLjVnU_7LN13Zt56hnF8XDrfRuWwnbBljm8xDkRZ7eU2mk31L7prw=)
23. [homeserverguides.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlUKy788VzW8AavR4BHc9OTjFkTf8j1AsGtmHx-xjc3KDRj05tPum_66Yh6CBbmD-IqNneZC3G1RSc2rAC3ZcwMdiHqmNiGm2NZgDXA8k2Hf3c1fhW5tiOvY0WCdpS37tZVeFWtUhYNOCUhpReRyeR-FO6XenXyEU0d7B8tqYX)
24. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqfRfRFDZ_qJlHKL4LxYQa8UCrR_KZ8vwIJYisESbQWrz6kegQ8O1s-bVtyBugAjRCHmDE3l6PYEa_ZXBuvaZip1ncY41KRZDzKkLfmqgclGO1yWAPqy2IuzYStE0bvJ8NOsIevW5hjYkXLGwcAcB5gbfeAITLTJ9rUthIMddz_x9mpN7XKrXk4ljCJIASv32XtOZD)
25. [credativ.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7mIkydRCUwaaeowKl0n0fdXJA67YzFbva2f213HfthCDNwbRdNYO3qGciMbtDwKmZCnpeb9f9w-o3AaYM3beEFZMjgUp7dGljpw7rtXhuZVdtwcH_ye9nlxkv9rFYyV4FsN6b0W928iBqyo-tmk-LN59_Xl3phqa99Df0XY5ajScuKIQKrc26vXzUzzFweqh3TpcgdHzvz9FQjqvA07uGh2OeRJQ_KfpQ7XFGm539xwDfRgvY7vTCa4J8BwLPyJ7D-HlfJOt-IIzBFQ==)
26. [ansible.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEFtPNC8EuX4CJdpK5up65cZpw8LwhcOAGnfdvy1-BIcX0dBQ0wfAUirfbEildTeb7tSiqURvwavf-V7fFzOcXGUDrG4x6X4obCQBx8c_uvtvVK4aAfoI7HPKC937kIUtgJJYTHsuIGQAFHVIvMKnwhFUm-srbZ8ahCWy53hZI9Bgz0vu8lL9xdN0YtlY8rgkujJDCTmy7p1jxPH5JB2Gk)
27. [proxmox.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEx97NqDIe6I6NEYEeHxFA-aSSNESzFHI0fBBuvfDAjMb1JXOQoeXbwk5XFVPauFlXJbBEr6eq86dTuiIdiWR0KE31lPgDHIwc5OP_yrD2WWSD6m2_3aCQrcmJENaVF-eD6FkNKwWGbNVRL1Ls1dOS6jRPwnC8tf6426qGdtFfTVhBdGTKPfJ9)
28. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXcoDBJCRGwAjtddO3ftEPvtKMe79bjEsDVCktOO7dZJ80cVWxgtGENeRXtYDypDimU9cF0KIi5lbB43zvbxTb1jVIbHQWMrCyjquE5Vpi6TkWBNZU1CB-P90xOW0gGPHjUH6cxiELaYgM9BzbSxNRBUeqUavjYA660TuNIpoPiF7F09gJ)
29. [terraform.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFu2p4ZdlBzRgGYrdqeX-5aKX-AmrHN7PqWd-8mOFIRxbqscBwZHJT_NNg91GJV089zEPrpg8uKWn2z0Bw57hFHGbPXHz8d0SRRjAaFP1kjTkG8CEtUkzJiD7qiuFRwiWVfW2H_e__vPTUXwPM_PQzD-z11z9_xUpI3PbsHSgtP86TWX6gps76Jds6lw9tnDQrvfrdbTYzuqA==)
30. [marktinderholt.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCxl-xrQJaAZc6LfzbYISd09MANwwPhOt5_13X2GaK3jtpf9qsLz8vOKeMfQbfAxmevOXU5E8etwTlwXkZkpSnTnfqxTGf-uqOCdkv-3lKI16wauA6VpIh6ZVapoIc2rLZhFjGaLYmJ0zdIb8Emda7ISeb0gPoA4QY5OuRzz4JDpxQP9Q5KREw8m_Sy8jgrjl5ivcrtDDmkRAdlsMMjqnY6Yz0p9LmEEOiz1Wj1p9IAI6SBg==)
31. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFA8exPK_P24lCfQVneO-37s1j20ifF8LabrBTrxiVIl5-I5Cghpsz-FkFl3h74NCS4qUbD6sAl3KedmjDmAv2mumkJyxCqdXzoRl-xwS4CqsHrUZzDtkAaZoWhwsACrm3cM0zSxd9m)
