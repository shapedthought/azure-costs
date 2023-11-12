import math
from inputs import InputWorkload
from settings import Settings
from veeam_backup import VeeamBackupResult


class AzureIndResult:
    backup_instance_cost: float
    total_backup_volume: float

    def __init__(self, backup_instance_cost: float, total_backup_volume: float) -> None:
        self.backup_instance_cost = backup_instance_cost
        self.total_backup_volume = total_backup_volume


class AzureBackupResult:
    backup_instances: [AzureIndResult]
    total_instance_cost: float
    total_storage: float

    def __init__(self, backup_instances: [AzureIndResult]) -> None:
        self.backup_instances = backup_instances
        self.total_instance_cost = 0
        self.total_storage = 0
        for i in backup_instances:
            self.total_instance_cost += i.backup_instance
            self.total_storage += i.total_backup_volume


class AzureBackup:
    azure_results: AzureBackupResult

    def __init__(self, inputs: InputWorkload, settings: Settings) -> AzureBackupResult:
        self.inputs = inputs
        self.settings = settings
        azure_results: AzureBackupResult

    def calculate_backup(self) -> None:
        instance_results: [AzureIndResult] = []
        for i in self.inputs.vm_workloads:
            if i.size <= 50:
                __backup_instance_cost = (
                    i.count * self.settings.azure_backup.backup_service.per_vm_under_50
                )
            else:
                __backup_instance_cost = (
                    i.count
                    * math.ceil(i.count / 500)
                    * self.settings.azure_backup.backup_service.per_vm_over_50
                )
            __backup_instance_cost_discounted = __backup_instance_cost * (
                1 - self.inputs.backup_properties.azure_discount
            )
            __total_backup_volume = (1 - self.settings.general.veeam_reduction) * (
                i.total_size_tb
                + (
                    (i.total_size_tb * self.settings.general.daily_change_rate)
                    * self.inputs.backup_properties.retention_days
                    - 1
                )
            )
            __result = AzureIndResult(
                __backup_instance_cost_discounted, __total_backup_volume
            )
            instance_results.append(__result)

        return AzureBackupResult(instance_results)


class AzureBackupCostResult:
    type: str
    storage_per_month: float
    snapshot_per_month: float
    total_storage_per_month: float
    total_storage_per_year: float

    def __init__(self, type, storage_per_month, snapshot_per_month) -> None:
        self.type = type
        self.storage_per_month = storage_per_month
        self.snapshot_per_month = snapshot_per_month
        self.total_storage_per_month = storage_per_month + snapshot_per_month
        self.total_storage_per_year = self.total_storage_per_month * 12


class AzureBackupCost:
    azure_results: AzureBackupResult

    def __init__(
        self,
        azure_backup: AzureBackup,
        inputs: InputWorkload,
        veeam_backup_totals: VeeamBackupResult,
        settings: Settings,
    ) -> AzureBackupResult:
        self.azure_backup = azure_backup
        self.inputs = inputs
        self.veeam_backup_totals = veeam_backup_totals
        self.settings = settings

    def calculate_backup_cost(self) -> AzureBackupCostResult:
        __storage_per_month = self.azure_backup.azure_results.total_storage * (
            self.settings.azure_backup.backup_vault.ra_grs
            * 1024
            * (1 - self.inputs.backup_properties.azure_discount)
        )
        __storage_cost_month = (
            self.veeam_backup_totals.snapshot_volume
            * 1024
            * (1 - self.inputs.backup_properties.azure_discount)
        )
        __azure_cost_result = AzureBackupCostResult(
            "Azure Backup",
            __storage_per_month,
            __storage_cost_month,
        )
        return __azure_cost_result
