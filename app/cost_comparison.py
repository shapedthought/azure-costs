from app.veeam_storage_costs import VeeamAzureCostsResult
from app.veeam_azure_compute_cost import VeeamComputeCostResult
from app.azure_backup_storage import AzureBackupCostResult


class CostComparisonResult:
    veeam_backup_total_cost_year: float
    azure_backup_total_cost_year: float
    agent_backup_total_cost_year: float

    def __init__(
        self,
        veeam_backup_total_cost_year,
        azure_backup_total_cost_year,
        agent_backup_total_cost_year,
    ) -> None:
        self.veeam_backup_total_cost_year = veeam_backup_total_cost_year
        self.azure_backup_total_cost_year = azure_backup_total_cost_year
        self.agent_backup_total_cost_year = agent_backup_total_cost_year


class CostComparison:
    veeam_storage_costs: list[VeeamAzureCostsResult]
    azure_backup_cost: AzureBackupCostResult
    veeam_compute_cost: VeeamComputeCostResult

    def __init__(
        self,
        veeam_storage_costs: list[VeeamAzureCostsResult],
        azure_backup_cost: AzureBackupCostResult,
        veeam_compute_cost: VeeamComputeCostResult,
    ) -> None:
        self.veeam_storage_costs = veeam_storage_costs
        self.azure_backup_cost = azure_backup_cost
        self.veeam_compute_cost = veeam_compute_cost

    def calculate_cost_comparison(self) -> CostComparisonResult:
        __min_storage_cost = min(
            [x.total_storage_cost_year for x in self.veeam_storage_costs]
        )
        __compute_cost = (
            self.veeam_compute_cost.total_worker_cost
            + self.veeam_compute_cost.vba_appliance_total
            + self.veeam_compute_cost.vbr_servers_total
        )

        __veeam_backup_total = (
            __min_storage_cost
            + __compute_cost
            + self.veeam_compute_cost.total_worker_cost
            + self.veeam_compute_cost.vul_cost_year
        )
        __azure_backup_total = (
            self.azure_backup_cost.total_storage_per_year
            + self.azure_backup_cost.azure_backup_instance_cost
        )
        __agent_backup_total = (
            min([x.agent_cost_year for x in self.veeam_storage_costs])
            + self.veeam_compute_cost.vul_cost_year
            + self.veeam_compute_cost.vbr_quantity_cost
        )
        __cost_results = CostComparisonResult(
            round(__veeam_backup_total, 2),
            round(__azure_backup_total, 2),
            round(__agent_backup_total, 2),
        )
        return __cost_results
