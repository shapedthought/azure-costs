from dataclasses import dataclass
from settings import Settings
from inputs import InputWorkload
from veeam_backup import VeeamBackupResult


class VeeamComputeCostResult:
    worker_payg: float
    worker_payg_year: float
    worker_res_3y: float
    worker_res_3y_year: float
    vbas_payg: float
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

    def __init__(
        self,
        worker_payg,
        worker_res_3y,
        vbas_payg,
        vbas_res_3y,
        vbr_servers_payg,
        vbr_servers_res_3y,
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
        self.total_worker_cost = min(self.worker_payg, self.worker_res_3y)
        self.vba_appliance_total = min(self.vbas_payg, self.vbas_res_3y)
        self.vbr_servers_total = min(self.vbr_servers_payg, self.vbr_servers_res_3y)


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

    def calculate_compute_costs(self) -> [VeeamComputeCostResult]:
        __results: [VeeamComputeCostResult] = []

        __worker_payg = list(
            filter(
                lambda x: x.vm_size == "Standard_F2s_v2, 2 CPU, 4 GB RAM (payg)",
                self.settings.Settings.azure_compute,
            )
        )[0]

        __worker_payg_3y = list(
            filter(
                lambda x: x.vm_size == "Standard_F2s_v2, 2 CPU, 4 GB RAM (res-3y)",
                self.settings.Settings.azure_compute,
            )
        )[0]

        __worker_payg = list(
            filter(
                lambda x: x.vm_size == "E4s_v3 4 CPU 32 GB (payg)",
                self.settings.Settings.azure_compute,
            )
        )[0]

        __vba_payg_3y = list(
            filter(
                lambda x: x.vm_size == "E4s_v3 4 CPU 32 GB (res-3y)",
                self.settings.Settings.azure_compute,
            )
        )[0]

        __vbr_payg = __worker_payg

        __vbr_payg_3y = __vba_payg_3y

        __worker_payg_per_month = (
            self.veeam_backup_totals.no_workers
            * __worker_payg
            * self.inputs.BackupProperties.azure_discount
            * self.inputs.BackupProperties.backup_window
            / 24
        )

        __worker_payg_3y_per_month = (
            self.veeam_backup_totals.no_workers
            * __worker_payg_3y
            * self.inputs.BackupProperties.azure_discount
        )
