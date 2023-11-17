from pydantic import BaseModel


class APICosts(BaseModel):
    cold: float
    hot: float


class BackupService(BaseModel):
    per_vm_under_50: int
    per_vm_over_50: int


class BackupSnapshotCost(BaseModel):
    instance: float


class BackupVault(BaseModel):
    lrs: int
    grs: int
    ra_grs: float


class AzureBackup(BaseModel):
    backup_service: BackupService
    backup_vault: BackupVault
    backup_snapshot_cost: BackupSnapshotCost


class AzureBlob(BaseModel):
    name: str
    cost: float


class AzureCompute(BaseModel):
    vm_size: str
    per_hour: float
    worker: bool
    throughput: int


class General(BaseModel):
    veeam_reduction: float
    azure_reduction: float
    daily_change_rate: float
    veeam_source_block_size: int
    worker_speed: int
    azstorage_acc_limit: int
    max_no_policies_per_vba: int
    max_no_vms_per_vbr: int
    max_workloads_policy: int
    vbaz_appliance_ram: int


class VeeamParameters(BaseModel):
    veeam_std_cost: int
    discount_veeam_price: int
    max_no_workers_per_appliance: int


class SettingsRequest(BaseModel):
    azure_backup: AzureBackup
    azure_blob: list[AzureBlob]
    api_costs: APICosts
    azure_compute: list[AzureCompute]
    general: General
    veeam_parameters: VeeamParameters
    vm_snapshot_cost: float
