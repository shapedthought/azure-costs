from typing import List


class BackupProperties:
    retention_days: int
    backup_window: int
    snapshots_kept: int
    first_snap_full: bool
    avg_vdisk_utilization: int
    veeam_discount: int
    azure_discount: float

    def __init__(
        self,
        retention_days: int,
        backup_window: int,
        snapshots_kept: int,
        first_snap_full: bool,
        avg_vdisk_utilization: int,
        veeam_discount: int,
        azure_discount: float,
    ) -> None:
        self.retention_days = retention_days
        self.backup_window = backup_window
        self.snapshots_kept = snapshots_kept
        self.first_snap_full = first_snap_full
        self.avg_vdisk_utilization = avg_vdisk_utilization
        self.veeam_discount = veeam_discount
        self.azure_discount = azure_discount


class VMWorkload:
    category: str
    count: int
    size: int

    def __init__(self, category: str, count: int, size: int) -> None:
        self.category = category
        self.count = count
        self.size = size
        self.total_size_tb = self.count * self.size / 1024


class InputWorkload:
    vm_workloads: List[VMWorkload]
    backup_properties: BackupProperties
    total_vm_count: int

    def __init__(
        self, vm_workloads: List[VMWorkload], backup_properties: BackupProperties
    ) -> None:
        self.vm_workloads = vm_workloads
        self.backup_properties = backup_properties
        self.total_vm_count = sum([i.count for i in self.vm_workloads])
