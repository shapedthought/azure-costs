import math
from app.settings import Settings
from app.inputs import InputWorkload
from app.veeam_backup import VeeamBackupResult


class VeeamComputeCostResult:
    worker_res: float
    worker_res_year: float
    worker_res_3y: float
    worker_res_3y_year: float
    vbas_res: float
    vbas_payg_year: float
    vbas_res_3y: float
    vbas_res_3y_year: float
    vbr_servers_payg: float
    vbr_servers_payg_year: float
    vbr_servers_res_3y: float
    vbr_servers_res_3y_year: float

    total_worker_cost: float
    vba_appliance_total: float
    vbr_servers_total: float
    vbr_quantity_cost: float

    veeam_vul_cost_year: float

    def __init__(
        self,
        worker_payg,
        worker_res_3y,
        vbas_payg,
        vbas_res_3y,
        vbr_servers_payg,
        vbr_servers_res_3y,
        vbr_quantity_cost,
        vul_cost_year,
    ) -> None:
        self.worker_payg = worker_payg
        self.worker_payg_year = worker_payg * 12
        self.worker_res_3y = worker_res_3y
        self.worker_res_3y_year = worker_res_3y * 12
        self.vbas_payg = vbas_payg
        self.vbas_payg_year = vbas_payg * 12
        self.vbas_res_3y = vbas_res_3y
        self.vbas_res_3y_year = vbas_res_3y * 12
        self.vbr_servers_payg = vbr_servers_payg
        self.vbr_servers_payg_year = vbr_servers_payg * 12
        self.vbr_servers_res_3y = vbr_servers_res_3y
        self.vbr_servers_res_3y_year = vbr_servers_res_3y * 12
        self.total_worker_cost = min(self.worker_payg_year, self.worker_res_3y_year)
        self.vba_appliance_total = min(self.vbas_payg_year, self.vbas_res_3y_year)
        self.vbr_servers_total = min(
            self.vbr_servers_payg_year, self.vbr_servers_res_3y_year
        )
        self.vbr_quantity_cost = vbr_quantity_cost
        self.vul_cost_year = vul_cost_year


class VeeamComputeCost:
    def __init__(
        self,
        settings: Settings,
        inputs: InputWorkload,
        veeam_backup_totals: VeeamBackupResult,
    ) -> None:
        self.settings = settings
        self.inputs = inputs
        self.veeam_backup_totals = veeam_backup_totals

    def calculate_compute_costs(self) -> VeeamComputeCostResult:
        worker_vm_cost = self.settings.azure_compute.worker.per_month
        worker_vm_cost_res = self.settings.azure_compute.worker.per_month_payg

        vba_vm_cost = self.settings.azure_compute.vba_server.per_month
        vba_vm_cost_res = self.settings.azure_compute.vba_server.per_month_payg

        vbr_vm_cost = self.settings.azure_compute.vbr_server.per_month
        vbr_vm_cost_res = self.settings.azure_compute.vbr_server.per_month_payg

        __worker_payg_per_month = (
            self.veeam_backup_totals.no_workers
            * worker_vm_cost
            * (1 - self.inputs.backup_properties.azure_discount)
            * self.inputs.backup_properties.backup_window
            / 24
        )

        __worker_payg_3y_per_month = (
            self.veeam_backup_totals.no_workers
            * worker_vm_cost_res
            * (1 - self.inputs.backup_properties.azure_discount)
        )

        __vba_payg = (
            self.settings.veeam_parameters.result_min_vba_appliances
            * vba_vm_cost
            * (1 - self.inputs.backup_properties.azure_discount)
        )

        __vba_payg_res_3y = (
            self.settings.veeam_parameters.result_min_vba_appliances
            * vba_vm_cost_res
            * (1 - self.inputs.backup_properties.azure_discount)
        )

        __vbr_servers_payg = (
            math.ceil(
                self.inputs.total_vm_count / self.settings.general.max_no_vms_per_vbr
            )
            * vbr_vm_cost
            * (1 - self.inputs.backup_properties.azure_discount)
        )
        __vbr_servers_res_3y = (
            math.ceil(
                self.inputs.total_vm_count / self.settings.general.max_no_vms_per_vbr
            )
            * vbr_vm_cost_res
            * (1 - self.inputs.backup_properties.azure_discount)
        )
        __vbr_quantity_cost = (
            12
            * 3
            * vbr_vm_cost_res
            * (1 - self.inputs.backup_properties.azure_discount)
        )
        __vul_cost_year = (
            self.inputs.total_vm_count
            * (self.settings.veeam_parameters.discount_veeam_price / 12 / 10)
            * 12
        )

        __result = VeeamComputeCostResult(
            __worker_payg_per_month,
            __worker_payg_3y_per_month,
            __vba_payg,
            __vba_payg_res_3y,
            __vbr_servers_payg,
            __vbr_servers_res_3y,
            __vbr_quantity_cost,
            __vul_cost_year,
        )

        return __result
