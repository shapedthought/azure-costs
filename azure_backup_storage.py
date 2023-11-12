import math
from inputs import InputWorkload
from settings import Settings


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
