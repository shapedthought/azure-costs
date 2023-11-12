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
import unittest


class TestVeeamBackup(unittest.TestCase):
    def setUp(self) -> None:
        self.parameters = VeeamParameters(
            veeam_reduction=0.5,
            azure_reduction=0,
            daily_change_rate=0.03,
            veeam_source_block_size=1024,
            worker_speed=WorkerSpeed.SLOW,
            azstorage_acc_limit=StorageAccountSpeedLimit.LOW,
            max_no_policies_per_vba=200,
            max_no_vms_per_vbr=10000,
            max_workloads_policy=1000,
            vbaz_appliance_ram=VBAzureApplianceRAM.LARGE,
            backup_window=8,
            total_capacity=1855.47,
            total_increment_size=16.70,
            veeam_std_cost=1302,
            discount_veeam_price=1302,
            total_no_azure_vms=12000,
            max_no_workers_per_appliance=4500,
        )
        self.azure_compute = [
            AzureCompute(
                vm_size="Standard_F2s_v2, 2 CPU, 4 GB RAM (payg)",
                per_hour=0.1140,
                worker=True,
                throughput=90,
            ),
            AzureCompute(
                vm_size="Standard_F2s_v2, 2 CPU, 4 GB RAM (res-3y)",
                per_hour=0.05721,
                worker=True,
                throughput=90,
            ),
            AzureCompute(
                vm_size="E4s_v3 4 CPU 32 GB (payg)",
                per_hour=0.32,
                worker=False,
                throughput=0,
            ),
            AzureCompute(
                vm_size="E4s_v3 4 CPU 32 GB (res-3y)",
                per_hour=0.12203,
                worker=False,
                throughput=0,
            ),
        ]
        self.general = General(
            veeam_reduction=0.5,
            azure_reduction=0,
            daily_change_rate=0.03,
            veeam_source_block_size=1024,
            worker_speed=WorkerSpeed.SLOW,
            azstorage_acc_limit=StorageAccountSpeedLimit.LOW,
            max_no_policies_per_vba=200,
            max_no_vms_per_vbr=10000,
            max_workloads_policy=1000,
            vbaz_appliance_ram=VBAzureApplianceRAM.LARGE,
            backup_window=8,
            total_capacity=1855.47,
            total_increment_size=16.70,
        )
        self.azure_blob = [
            AzureBlob(name="Cold RA-GRS (payg)", cost=0.025),
            AzureBlob(name="Cold RA-GRS (1PB-res-3y)", cost=0.0155),
            AzureBlob(name="Hot RA-GRS (payg)", cost=0.049),
            AzureBlob(name="Hot RA-GRS (1PB-res-3y)", cost=0.03038),
        ]
        self.settings = Settings(
            azure_backup=AzureBackup(
                backup_service=BackupService(
                    per_vm_under_50=5,
                    per_vm_over_50=10,
                ),
                backup_vault=BackupVault(lrs=0, grs=0, ra_grs=0.05696),
                backup_snapshot_cost=BackupSnapshotCost(instance=0.145),
            ),
            api_costs=APICosts(
                cold=0.02,
                hot=0.0108,
            ),
            azure_blob=self.azure_blob,
            azure_compute=self.azure_compute,
            general=self.general,
            veeam_parameters=self.parameters,
        )

        self.workloads = [
            VMWorkload(category="small", count=2000, size=50),
            VMWorkload(category="medium", count=8000, size=100),
            VMWorkload(category="large", count=2000, size=500),
        ]
        self.backup_properties = BackupProperties(
            retention_days=14,
            backup_window=8,
            snapshots_kept=2,
            first_snap_full=True,
            avg_vdisk_utilization=0.6,
            veeam_discount=0,
            azure_discount=0.3,
        )
        self.inputs = InputWorkload(
            vm_workloads=self.workloads, backup_properties=self.backup_properties
        )
        self.veeam_backup = VeeamBackup(settings=self.settings, inputs=self.inputs)
        self.incremental_results = self.veeam_backup.calculate_incremental()
        self.full_results = self.veeam_backup.calculate_totals(self.incremental_results)

    def test_veeam_backup(self):
        self.assertAlmostEqual(self.full_results.incremental_size, 16.70, places=2)
        self.assertAlmostEqual(
            self.full_results.total_backup_volume, 788.9296875, places=2
        )
        self.assertAlmostEqual(self.full_results.snapshot_volume, 1146.68, places=0)
        self.assertAlmostEqual(self.full_results.api_put_per_month, 1050624, places=2)
        self.assertAlmostEqual(self.full_results.incremental_throughput, 608, places=0)
        self.assertAlmostEqual(self.full_results.no_workers, 8, places=0)
        self.assertAlmostEqual(self.full_results.no_storage_accounts, 1, places=0)
