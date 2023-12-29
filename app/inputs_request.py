from pydantic import BaseModel
from app.settings_request import SettingsRequest


class BackupProperties(BaseModel):
    retention_days: int
    backup_window: int
    snapshots_kept: int
    first_snap_full: bool
    avg_vdisk_utilization: float
    veeam_discount: int
    azure_discount: float


class VMWorkload(BaseModel):
    category: str
    count: int
    size: int


class InputWorkloadRequest(BaseModel):
    vm_workloads: list[VMWorkload]
    backup_properties: BackupProperties


class FullRequest(BaseModel):
    settings: SettingsRequest
    inputs: InputWorkloadRequest


class NoSettingsRequest(BaseModel):
    inputs: InputWorkloadRequest
