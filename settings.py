from typing import List, Dict
import math
from enum import Enum


class APICosts:
    cold: float
    hot: float

    def __init__(self, cold: float, hot: float) -> None:
        self.cold = cold
        self.hot = hot


class BackupService:
    per_vm_under_50: int
    per_vm_over_50: int

    def __init__(self, per_vm_under_50: int, per_vm_over_50: int) -> None:
        self.per_vm_under_50 = per_vm_under_50
        self.per_vm_over_50 = per_vm_over_50


class BackupSnapshotCost:
    instance: float

    def __init__(self, instance: float) -> None:
        self.instance = instance


class BackupVault:
    lrs: int
    grs: int
    ra_grs: float

    def __init__(self, lrs: int, grs: int, ra_grs: float) -> None:
        self.lrs = lrs
        self.grs = grs
        self.ra_grs = ra_grs


class AzureBackup:
    backup_service: BackupService
    backup_vault: BackupVault
    backup_snapshot_cost: BackupSnapshotCost

    def __init__(
        self,
        backup_service: BackupService,
        backup_vault: BackupVault,
        backup_snapshot_cost: BackupSnapshotCost,
    ) -> None:
        self.backup_service = backup_service
        self.backup_vault = backup_vault
        self.backup_snapshot_cost = backup_snapshot_cost


class AzureBlob:
    name: str
    cost: float
    cost_tb: float
    cost_pb: float

    def __init__(self, name: str, cost: float) -> None:
        self.name = name
        self.cost = cost
        self.cost_tb = cost * 1024
        self.cost_pb = cost * 1024**2


class AzureCompute:
    vm_size: str
    per_hour: float
    per_month: float
    per_year: float
    worker: bool
    throughput: int

    def __init__(
        self, vm_size: str, per_hour: float, worker: bool, throughput: int
    ) -> None:
        self.vm_size = vm_size
        self.per_hour = per_hour
        self.per_month = per_hour * 24 * 30
        self.per_year = self.per_month * 12
        self.worker = worker
        self.throughput = throughput


class WorkerSpeed(Enum):
    SLOW = 90
    MEDIUM = 180
    FAST = 270


class StorageAccountSpeedLimit(Enum):
    LOW = 3200
    HIGH = 7680


class VBAzureApplianceRAM(Enum):
    TINY = 4
    SMALL = 8
    MEDIUM = 16
    LARGE = 32
    XLARGE = 64


class General:
    veeam_reduction: float
    azure_reduction: float
    daily_change_rate: float
    veeam_source_block_size: int
    worker_speed: WorkerSpeed
    azstorage_acc_limit: StorageAccountSpeedLimit
    max_no_policies_per_vba: int
    max_worker_per_account: int
    max_no_vms_per_vbr: int
    max_workloads_policy: int
    vbaz_appliance_ram: VBAzureApplianceRAM

    def __init__(
        self,
        veeam_reduction: float,
        azure_reduction: float,
        daily_change_rate: float,
        veeam_source_block_size: int,
        worker_speed: WorkerSpeed,
        azstorage_acc_limit: StorageAccountSpeedLimit,
        max_no_policies_per_vba: int,
        max_no_vms_per_vbr: int,
        max_workloads_policy: int,
        vbaz_appliance_ram: VBAzureApplianceRAM,
        backup_window: int,
        total_capacity: float,
        total_increment_size: float,
    ) -> None:
        self.veeam_reduction = veeam_reduction
        self.azure_reduction = azure_reduction
        self.daily_change_rate = daily_change_rate
        self.veeam_source_block_size = veeam_source_block_size
        self.worker_speed = worker_speed.value
        self.azstorage_acc_limit = azstorage_acc_limit.value
        self.max_no_policies_per_vba = max_no_policies_per_vba
        self.max_worker_per_account = math.ceil(
            azstorage_acc_limit.value / worker_speed.value
        )
        self.max_no_vms_per_vbr = max_no_vms_per_vbr
        self.max_workloads_policy = max_workloads_policy
        self.vbaz_appliance_ram = vbaz_appliance_ram.value
        self.min_req_no_storage_acc = math.ceil(
            total_capacity
            * 1024**2
            * daily_change_rate
            * veeam_reduction
            / (azstorage_acc_limit.value * backup_window * 3600)
        )
        self.no_workers_based_on_storage_volume = math.ceil(
            total_increment_size
            * 1024**2
            / (worker_speed.value * backup_window * 3600)
        )


class VeeamParameters(General):
    veeam_reduction: float
    azure_reduction: float
    daily_change_rate: float
    veeam_source_block_size: int
    worker_speed: WorkerSpeed
    azstorage_acc_limit: StorageAccountSpeedLimit
    max_no_policies_per_vba: int
    max_no_vms_per_vbr: int
    max_workloads_policy: int
    vbaz_appliance_ram: VBAzureApplianceRAM
    backup_window: int
    total_capacity: float
    total_increment_size: float
    veeam_std_cost: int
    discount_veeam_price: int
    total_no_azure_vms: int
    result_min_vba_appliances: int

    def __init__(
        self,
        veeam_reduction: float,
        azure_reduction: float,
        daily_change_rate: float,
        veeam_source_block_size: int,
        worker_speed: WorkerSpeed,
        azstorage_acc_limit: StorageAccountSpeedLimit,
        max_no_policies_per_vba: int,
        max_no_vms_per_vbr: int,
        max_workloads_policy: int,
        vbaz_appliance_ram: VBAzureApplianceRAM,
        backup_window: int,
        total_capacity: float,
        total_increment_size: float,
        veeam_std_cost: int,
        discount_veeam_price: int,
        total_no_azure_vms: int,
        max_no_workers_per_appliance: int,
    ) -> None:
        super().__init__(
            veeam_reduction,
            azure_reduction,
            daily_change_rate,
            veeam_source_block_size,
            worker_speed,
            azstorage_acc_limit,
            max_no_policies_per_vba,
            max_no_vms_per_vbr,
            max_workloads_policy,
            vbaz_appliance_ram,
            backup_window,
            total_capacity,
            total_increment_size,
        )

        self.veeam_std_cost = veeam_std_cost
        self.discount_veeam_price = discount_veeam_price
        self.total_no_azure_vms = total_no_azure_vms
        self.no_vba_appliances_based_on_vms = math.ceil(
            total_no_azure_vms / max_no_workers_per_appliance
        )  # calculated
        self.ram_available_for_policies = math.ceil(
            vbaz_appliance_ram.value - (vbaz_appliance_ram.value * 0.05) - 1.5
        )  # calculated
        self.max_no_of_maxed_policies = math.floor(
            self.ram_available_for_policies * 1024 / (100 + (3 * max_workloads_policy))
        )
        self.no_vba_appliances_based_policies = math.ceil(
            self.max_no_of_maxed_policies / self.max_no_of_maxed_policies
        )  # calculated
        self.result_min_vba_appliances = max(
            self.no_vba_appliances_based_on_vms, self.no_vba_appliances_based_policies
        )  # calculated


class Settings:
    azure_backup: AzureBackup
    azure_blob: List[AzureBlob]
    api_costs: APICosts
    azure_compute: List[AzureCompute]
    general: General
    veeam_parameters: VeeamParameters

    def __init__(
        self,
        azure_backup: AzureBackup,
        azure_blob: List[AzureBlob],
        api_costs: APICosts,
        azure_compute: List[AzureCompute],
        general: General,
        veeam_parameters: VeeamParameters,
    ) -> None:
        self.azure_backup = azure_backup
        self.azure_blob = azure_blob
        self.api_costs = api_costs
        self.azure_compute = azure_compute
        self.general = general
        self.veeam_parameters = veeam_parameters
