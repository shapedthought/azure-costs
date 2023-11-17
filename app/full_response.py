from pydantic import BaseModel
from app.cost_comparison import CostComparisonResult


class VeeamBackupResponse(BaseModel):
    inc_backup_size: float
    total_backup_volume: float
    snapshot_volume: float
    api_put_month: float
    inc_throughput: float
    no_workers: int
    no_storage_accounts: int


class VeeamAzureCostStorageResponse(BaseModel):
    total_storage_cost_year: list[tuple[str, float]]


class ComputeCostTotalResponse(BaseModel):
    worker_cost: float
    vba_appliance_cost: float
    vbr_servers_cost: float


class CostComparisonResponse(BaseModel):
    veeam_backup_total_cost_year: float
    azure_backup_total_cost_year: float
    agent_backup_total_cost_year: float


class FullResponse(BaseModel):
    cost_comparison: CostComparisonResponse
    veeam_backup_totals: VeeamBackupResponse
    veeam_azure_cost_storage: VeeamAzureCostStorageResponse
    veeam_compute_cost_totals: ComputeCostTotalResponse
    veeam_vul_cost: float
    azure_backup_instances_cost: float
