from dataclasses import dataclass
import settings
import inputs
import veeam_backup


@dataclass
class VeeamAzureCostsResult:
    name: str
    storage_per_month: float
    snap_cost_month: float
    api_per_month: float
    total_storage_cost_month: float
    total_storage_cost_year: float


class VeeamAzureCosts:
    def __init__(
        self,
        settings: settings,
        inputs: inputs,
        veeam_backup_totals: veeam_backup.VeeamBackupResult,
    ) -> None:
        self.settings = settings
        self.inputs = inputs
        self.veeam_backup_totals = veeam_backup_totals

    def calculate_storage_costs(self) -> [VeeamAzureCostsResult]:
        __results: [VeeamAzureCostsResult] = []
        for i in self.settings.AzureBlob:
            __storage_per_month = (
                self.veeam_backup_totals.incremental_size
                * i.cost
                * self.inputs.BackupProperties.azure_discount
            )
            __snap_cost_month = (
                self.veeam_backup_totals.snapshot_volume
                * i.cost
                * 1024
                * self.inputs.BackupProperties.azure_discount
            )
            __api_per_month = (
                self.veeam_backup_totals.api_put_per_month
                * self.settings.ApiCosts.cold
                * self.inputs.BackupProperties.azure_discount
            )
            __total_storage_cost_month = (
                __storage_per_month + __snap_cost_month + __api_per_month
            )
            __total_storage_cost_year = __total_storage_cost_month * 12

            __result = VeeamAzureCostsResult(
                i.name,
                __storage_per_month,
                __snap_cost_month,
                __api_per_month,
                __total_storage_cost_month,
                __total_storage_cost_year,
            )
            __results.append(__result)

        return __results
