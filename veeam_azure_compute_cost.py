import dataclasses
import settings
import inputs
import veeam_backup


@dataclasses
class VeeamComputeCostResult:
    name: str
    compute_per_month: float
    compute_per_year: float


class VeeamComputeCost:
    def __init__(
        self,
        settings: settings,
        inputs: inputs,
        veeam_backup_totals: veeam_backup.VeeamBackupResult,
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
