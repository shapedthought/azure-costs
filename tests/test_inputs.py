import unittest

from inputs import InputWorkload, VMWorkload, BackupProperties


class TestInputs(unittest.TestCase):
    def setUp(self) -> None:
        self.backup_properties = BackupProperties(
            retention_days=14,
            backup_window=8,
            snapshots_kept=2,
            first_snap_full=True,
            avg_vdisk_utilization=0.6,
            veeam_discount=0,
            azure_discount=0.3,
        )

        self.vm_workloads = [
            VMWorkload(category="small", count=2000, size=50),
            VMWorkload(category="medium", count=8000, size=100),
            VMWorkload(category="large", count=2000, size=500),
        ]

        self.inputs = InputWorkload(
            vm_workloads=self.vm_workloads, backup_properties=self.backup_properties
        )

    def test_input_workload(self):
        self.assertEqual(self.inputs.backup_properties.retention_days, 14)
        self.assertEqual(self.inputs.backup_properties.backup_window, 8)
        self.assertEqual(self.inputs.backup_properties.snapshots_kept, 2)
        self.assertEqual(self.inputs.backup_properties.first_snap_full, True)
        self.assertEqual(self.inputs.backup_properties.avg_vdisk_utilization, 0.6)
        self.assertEqual(self.inputs.backup_properties.veeam_discount, 0)
        self.assertEqual(self.inputs.backup_properties.azure_discount, 0.3)
        self.assertEqual(self.inputs.vm_workloads[0].category, "small")
        self.assertEqual(self.inputs.vm_workloads[0].count, 2000)
        self.assertEqual(self.inputs.vm_workloads[0].size, 50)
        self.assertEqual(self.inputs.vm_workloads[1].category, "medium")
        self.assertEqual(self.inputs.vm_workloads[1].count, 8000)
        self.assertEqual(self.inputs.vm_workloads[1].size, 100)
        self.assertEqual(self.inputs.vm_workloads[2].category, "large")
        self.assertEqual(self.inputs.vm_workloads[2].count, 2000)
        self.assertEqual(self.inputs.vm_workloads[2].size, 500)
        self.assertAlmostEqual(
            self.inputs.vm_workloads[0].total_size_tb, 97.66, places=2
        )
        self.assertAlmostEqual(
            self.inputs.vm_workloads[1].total_size_tb, 781.25, places=2
        )
        self.assertAlmostEqual(
            self.inputs.vm_workloads[2].total_size_tb, 976.56, places=2
        )
