import json
import functools
from azure_backup_storage import AzureBackupCost, AzureBackupInstances
from veeam_azure_compute_cost import VeeamComputeCost
from veeam_backup import VeeamBackup
from settings import (
    Settings,
    VeeamParameters,
    AzureBackup,
    AzureBlob,
    BackupService,
    General,
    BackupVault,
    BackupSnapshotCost,
    APICosts,
    AzureCompute,
    WorkerSpeed,
    VBAzureApplianceRAM,
    StorageAccountSpeedLimit,
)
from inputs import VMWorkload, BackupProperties, InputWorkload
from veeam_storage_costs import VeeamAzureCosts
from cost_comparison import CostComparison


class VmWorkload:
    def __init__(self, category: str, count: int, size: float) -> None:
        self.category = category
        self.count = count
        self.size = size
        self.total_size = count * size


def calculate_vm_totals(vm_workloads: list[VmWorkload]) -> dict[str, float]:
    total_vms = functools.reduce(lambda x, y: x + y.count[0], vm_workloads, 0)
    total_size = functools.reduce(lambda x, y: x + y.total_size, vm_workloads, 0.0)
    return {"total_vms": total_vms, "total_size": total_size}


def main():
    with open("settings.json", "r") as f:
        settings = json.load(f)

    azure_backup = BackupService(
        per_vm_over_50=settings["azure_backup"]["per_vm_over_50"],
        per_vm_under_50=settings["azure_backup"]["per_vm_under_50"],
    )

    backup_snapshot_cost = BackupSnapshotCost(
        instance=settings["azure_backup"]["backup_snapshot_cost"]["instance"],
    )

    backup_vault = BackupVault(
        lrs=settings["azure_backup"]["backup_vault"]["LRS"],
        grs=settings["azure_backup"]["backup_vault"]["GRS"],
        ra_grs=settings["azure_backup"]["backup_vault"]["RA-GRS"],
    )

    azure_backup = AzureBackup(
        backup_service=azure_backup,
        backup_vault=backup_vault,
        backup_snapshot_cost=backup_snapshot_cost,
    )

    azure_blob: list[AzureBlob] = []
    for i in settings["azure_blob"]:
        azure_blob.append(AzureBlob(name=i["name"], cost=i["cost"]))

    api_costs = APICosts(
        cold=settings["api_costs"]["cold"],
        hot=settings["api_costs"]["hot"],
    )

    azure_compute: list[AzureCompute] = []
    for i in settings["azure_compute"]:
        azure_compute.append(
            AzureCompute(
                vm_size=i["vm_size"],
                per_hour=i["per_hour"],
                worker=i["worker"],
                throughput=i["throughput"],
            )
        )

    general = General(
        veeam_reduction=settings["general"]["veeam_reduction"],
        azure_reduction=settings["general"]["azure_reduction"],
        daily_change_rate=settings["general"]["daily_change_rate"],
        veeam_source_block_size=settings["general"]["veeam_source_block_size"],
        worker_speed=settings["general"]["worker_speed"],
        azstorage_acc_limit=settings["general"]["azstorage_acc_limit"],
        max_no_policies_per_vba=settings["general"]["max_no_policies_per_vba"],
        max_no_vms_per_vbr=settings["general"]["max_no_vms_per_vbr"],
        max_workloads_policy=settings["general"]["max_workloads_policy"],
        vbaz_appliance_ram=settings["general"]["vbaz_appliance_ram"],
        backup_window=settings["general"]["backup_window"],
        total_capacity=settings["general"]["total_capacity"],
        total_increment_size=settings["general"]["total_increment_size"],
    )

    with open("inputs.json", "r") as f:
        input_vm_workloads = json.load(f)


if __name__ == "__main__":
    main()
