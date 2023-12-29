from dataclasses import dataclass
import functools
from app.settings import Settings
from app.inputs import InputWorkload
import math


@dataclass
class VeeamBackupResult:
    incremental_size: float
    total_backup_volume: float
    snapshot_volume: float
    api_put_per_month: float
    incremental_throughput: float
    no_workers: int
    no_storage_accounts: int


class VeeamBackup:
    def __init__(self, settings: Settings, inputs: InputWorkload) -> None:
        self.settings = settings
        self.inputs = inputs

    def calculate_incremental(self) -> [VeeamBackupResult]:
        __results: [VeeamBackupResult] = []
        for i in self.inputs.vm_workloads:
            __total_size = i.total_size_tb
            __incremental_size = (
                __total_size
                * self.inputs.backup_properties.avg_vdisk_utilization
                * self.settings.general.daily_change_rate
                * self.settings.general.veeam_reduction
            )
            __total_backup_volume = (1 - self.settings.general.veeam_reduction) * (
                __total_size * self.inputs.backup_properties.avg_vdisk_utilization
                + (
                    (
                        __total_size
                        * self.inputs.backup_properties.avg_vdisk_utilization
                        * self.settings.general.daily_change_rate
                    )
                    * self.inputs.backup_properties.retention_days
                    - 1
                )
            )

            if self.inputs.backup_properties.first_snap_full:
                __snapshot_volume = (
                    __total_size * self.inputs.backup_properties.avg_vdisk_utilization
                    + (
                        __total_size
                        * self.inputs.backup_properties.avg_vdisk_utilization
                        * self.settings.general.daily_change_rate
                        + (self.inputs.backup_properties.snapshots_kept - 1)
                        * self.settings.general.daily_change_rate
                    )
                )
            else:
                __snapshot_volume = (
                    __total_size
                    * self.inputs.backup_properties.avg_vdisk_utilization
                    * self.inputs.backup_properties.snapshots_kept
                    * self.settings.general.daily_change_rate
                )

            __api_put_per_month = (
                (
                    30
                    * self.settings.general.daily_change_rate
                    * (
                        __total_size
                        * self.inputs.backup_properties.avg_vdisk_utilization
                        * 1024**3
                    )
                )
                / self.settings.general.veeam_source_block_size
                / 1000
            )

            __inc_throughput = (
                __incremental_size
                * 1024**2
                / (self.inputs.backup_properties.backup_window * 3600)
            )

            __no_workers = math.ceil(
                __inc_throughput / self.settings.general.worker_speed
            )

            __storage_accounts = max(
                math.ceil(__inc_throughput / self.settings.general.azstorage_acc_limit),
                math.ceil(__no_workers / self.settings.general.max_worker_per_account),
            )

            __results.append(
                VeeamBackupResult(
                    __incremental_size,
                    __total_backup_volume,
                    __snapshot_volume,
                    __api_put_per_month,
                    __inc_throughput,
                    __no_workers,
                    __storage_accounts,
                )
            )

        return __results

    def calculate_totals(self, results: [VeeamBackupResult]) -> VeeamBackupResult:
        __total_incremental_size = functools.reduce(
            lambda x, y: x + y.incremental_size, results, 0.0
        )
        __total_backup_volume = functools.reduce(
            lambda x, y: x + y.total_backup_volume, results, 0.0
        )
        __total_snapshot_volume = functools.reduce(
            lambda x, y: x + y.snapshot_volume, results, 0.0
        )
        __total_api_put_per_month = functools.reduce(
            lambda x, y: x + y.api_put_per_month, results, 0.0
        )
        __total_inc_throughput = functools.reduce(
            lambda x, y: x + y.incremental_throughput, results, 0.0
        )
        __total_no_workers = functools.reduce(
            lambda x, y: x + y.no_workers, results, 0.0
        )
        __total_storage_accounts = functools.reduce(
            lambda x, y: x + y.no_storage_accounts, results, 0.0
        )
        __total_storage_accounts = max([x.no_storage_accounts for x in results])

        result = VeeamBackupResult(
            __total_incremental_size,
            __total_backup_volume,
            __total_snapshot_volume,
            __total_api_put_per_month,
            __total_inc_throughput,
            __total_no_workers,
            __total_storage_accounts,
        )

        return result
