import unittest
from settings import (
    VeeamParameters,
    AzureCompute,
    WorkerSpeed,
    VBAzureApplianceRAM,
    StorageAccountSpeedLimit,
)


class TestSettings(unittest.TestCase):
    def setUp(self):
        self.settings = VeeamParameters(
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
        self.azure_compute = AzureCompute(
            vm_size="Standard_F2s_v2, 2 CPU, 4 GB RAM (payg)",
            per_hour=0.1140,
            worker=True,
            throughput=90,
        )

    def test_calculated_properties(self):
        self.assertEqual(self.settings.max_worker_per_account, 36)
        self.assertEqual(self.settings.min_req_no_storage_acc, 1)
        self.assertEqual(self.settings.no_workers_based_on_storage_volume, 7)
        self.assertEqual(self.settings.no_vba_appliances_based_on_vms, 3)
        self.assertEqual(self.settings.ram_available_for_policies, 29)
        self.assertEqual(self.settings.max_no_of_maxed_policies, 9)
        self.assertEqual(self.settings.no_vba_appliances_based_policies, 1)
        self.assertEqual(self.settings.result_min_vba_appliances, 3)
        self.assertAlmostEqual(self.azure_compute.per_month, 82.08, places=2)
        self.assertAlmostEqual(self.azure_compute.per_year, 984.96, places=2)
