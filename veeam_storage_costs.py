from dataclasses import dataclass
from settings import Settings
from inputs import InputWorkload
from veeam_backup import VeeamBackupResult


@dataclass
class VeeamAzureCostsResult:
    name: str
    storage_per_month: float
    snap_cost_month: float
    api_per_month: float
    total_storage_cost_month: float
    total_storage_cost_year: float
    agent_cost_month: float
    agent_cost_year: float


class VeeamAzureCosts:
    def __init__(
        self,
        settings: Settings,
        inputs: InputWorkload,
        veeam_backup_totals: VeeamBackupResult,
    ) -> None:
        self.settings = settings
        self.inputs = inputs
        self.veeam_backup_totals = veeam_backup_totals

    def calculate_storage_costs(self) -> list[VeeamAzureCostsResult]:
        __results: list[VeeamAzureCostsResult] = []
        for i in self.settings.azure_blob:
            __storage_per_month = (
                self.veeam_backup_totals.total_backup_volume
                * i.cost_tb
                * (1 - self.inputs.backup_properties.azure_discount)
            )
            __snap_cost_month = (
                self.veeam_backup_totals.snapshot_volume
                * self.settings.vm_snapshot_cost
                * 1024
                * (1 - self.inputs.backup_properties.azure_discount)
            )
            __api_per_month = (
                self.veeam_backup_totals.api_put_per_month
                * self.settings.api_costs.cold  # todo
                * (1 - self.inputs.backup_properties.azure_discount)
            )
            __total_storage_cost_month = (
                __storage_per_month + __snap_cost_month + __api_per_month
            )
            __total_storage_cost_year = __total_storage_cost_month * 12

            __agent_cost_month = __storage_per_month + __api_per_month

            __agent_cost_year = __agent_cost_month * 12

            __result = VeeamAzureCostsResult(
                i.name,
                __storage_per_month,
                __snap_cost_month,
                __api_per_month,
                __total_storage_cost_month,
                __total_storage_cost_year,
                __agent_cost_month,
                __agent_cost_year,
            )
            __results.append(__result)

        return __results
