import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import functools
from app.azure_backup_storage import AzureBackupCost, AzureBackupInstances

# from full_response import FullResponse
from app.veeam_azure_compute_cost import VeeamComputeCost
from app.veeam_backup import VeeamBackup
from app.settings import (
    AzureComputeInstance,
    Settings,
    VeeamParameters,
    AzureBackup,
    AzureBlob,
    BackupService,
    General,
    BackupVault,
    APICosts,
    AzureCompute,
    WorkerSpeed,
    VBAzureApplianceRAM,
    StorageAccountSpeedLimit,
)
from app.inputs import VMWorkload, InputWorkload
from app.full_response import (
    ComputeCostTotalResponse,
    CostComparisonResponse,
    FullResponse,
    VeeamAzureCostStorageResponse,
    VeeamBackupResponse,
)
from app.inputs_request import FullRequest
from app.veeam_storage_costs import VeeamAzureCosts
from app.cost_comparison import CostComparison

app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


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


def get_worker_speed(speed: int) -> WorkerSpeed:
    match speed:
        case 90:
            return WorkerSpeed.SLOW
        case 180:
            return WorkerSpeed.MEDIUM
        case 270:
            return WorkerSpeed.FAST
        case _:
            return WorkerSpeed.MEDIUM


def get_storage_account_speed(speed: int) -> StorageAccountSpeedLimit:
    match speed:
        case "3200":
            return StorageAccountSpeedLimit.LOW
        case "7680":
            return StorageAccountSpeedLimit.HIGH
        case _:
            return StorageAccountSpeedLimit.LOW


def get_vbaz_appliance_ram(ram: int) -> VBAzureApplianceRAM:
    match ram:
        case 4:
            return VBAzureApplianceRAM.TINY
        case 8:
            return VBAzureApplianceRAM.SMALL
        case 16:
            return VBAzureApplianceRAM.MEDIUM
        case 32:
            return VBAzureApplianceRAM.LARGE
        case 64:
            return VBAzureApplianceRAM.XLARGE
        case _:
            return VBAzureApplianceRAM.MEDIUM


@app.get("/baseSettings")
async def base_settings():
    with open("json/full_request_updated.json") as f:
        return json.load(f)


@app.post("/calculate")
async def calculate(input_workload: FullRequest):
    api_costs = APICosts(
        hot=input_workload.settings.api_costs.hot,
        cold=input_workload.settings.api_costs.cold,
    )
    backup_service = BackupService(
        per_vm_under_50=input_workload.settings.azure_backup.backup_service.per_vm_under_50,
        per_vm_over_50=input_workload.settings.azure_backup.backup_service.per_vm_over_50,
    )
    backup_vault = BackupVault(
        lrs=input_workload.settings.azure_backup.backup_vault.lrs,
        grs=input_workload.settings.azure_backup.backup_vault.grs,
        ra_grs=input_workload.settings.azure_backup.backup_vault.ra_grs,
    )
    azure_backup = AzureBackup(
        backup_service=backup_service,
        backup_vault=backup_vault,
        backup_snapshot_cost=input_workload.settings.azure_backup.backup_snapshot_cost,
    )
    azure_blob = []
    for blob in input_workload.settings.azure_blob:
        azure_blob.append(AzureBlob(name=blob.name, cost=blob.cost))

    input_worker = input_workload.settings.azure_compute.worker
    worker = AzureComputeInstance(
        input_worker.vm_size,
        input_worker.per_hour,
        input_worker.per_hour_payg,
        input_worker.throughput,
    )
    input_vba_server = input_workload.settings.azure_compute.vba_server
    vba_server = AzureComputeInstance(
        input_vba_server.vm_size,
        input_vba_server.per_hour,
        input_vba_server.per_hour_payg,
        input_vba_server.throughput,
    )
    input_vbr_server = input_workload.settings.azure_compute.vbr_server
    vbr_server = AzureComputeInstance(
        input_vbr_server.vm_size,
        input_vbr_server.per_hour,
        input_vbr_server.per_hour_payg,
        input_vbr_server.throughput,
    )
    azure_compute = AzureCompute(
        worker=worker, vba_server=vba_server, vbr_server=vbr_server
    )

    worker_speed = get_worker_speed(input_workload.settings.general.worker_speed)

    storage_account_speed = get_storage_account_speed(
        input_workload.settings.general.azstorage_acc_limit
    )

    vbaz_appliance_ram = get_vbaz_appliance_ram(
        input_workload.settings.general.vbaz_appliance_ram
    )

    vm_workloads: list[VMWorkload] = []
    for workload in input_workload.inputs.vm_workloads:
        vm_workloads.append(
            VMWorkload(
                category=workload.category,
                count=workload.count,
                size=workload.size,
            )
        )

    input_workload_obj = InputWorkload(
        vm_workloads=vm_workloads,
        backup_properties=input_workload.inputs.backup_properties,
    )

    general = General(
        inputs=input_workload_obj,
        veeam_reduction=input_workload.settings.general.veeam_reduction,
        azure_reduction=input_workload.settings.general.azure_reduction,
        daily_change_rate=input_workload.settings.general.daily_change_rate,
        veeam_source_block_size=input_workload.settings.general.veeam_source_block_size,
        worker_speed=worker_speed,
        azstorage_acc_limit=storage_account_speed,
        max_no_policies_per_vba=input_workload.settings.general.max_no_policies_per_vba,
        max_no_vms_per_vbr=input_workload.settings.general.max_no_vms_per_vbr,
        max_workloads_policy=input_workload.settings.general.max_workloads_policy,
        vbaz_appliance_ram=vbaz_appliance_ram,
    )

    parameters = VeeamParameters(
        general=general,
        veeam_std_cost=input_workload.settings.veeam_parameters.veeam_std_cost,
        discount_veeam_price=input_workload.settings.veeam_parameters.discount_veeam_price,
        max_no_workers_per_appliance=input_workload.settings.veeam_parameters.max_no_workers_per_appliance,
    )

    settings = Settings(
        azure_backup=azure_backup,
        azure_blob=azure_blob,
        api_costs=api_costs,
        azure_compute=azure_compute,
        general=general,
        veeam_parameters=parameters,
        vm_snapshot_cost=input_workload.settings.vm_snapshot_cost,
    )

    veeam_backup = VeeamBackup(settings=settings, inputs=input_workload_obj)
    incremental_results = veeam_backup.calculate_incremental()
    full_results = veeam_backup.calculate_totals(incremental_results)
    azure_backup_instances = AzureBackupInstances(
        settings=settings, inputs=input_workload_obj
    )
    azure_backup_instance_results = azure_backup_instances.calculate_backup()
    azure_backup_cost = AzureBackupCost(
        settings=settings,
        inputs=input_workload_obj,
        azure_backup=azure_backup_instance_results,
        veeam_backup_totals=full_results,
    )
    azure_backup_cost_result = azure_backup_cost.calculate_backup_cost()
    veeam_az_storage = VeeamAzureCosts(
        settings=settings,
        inputs=input_workload_obj,
        veeam_backup_totals=full_results,
    )
    veeam_az_storage_results = veeam_az_storage.calculate_storage_costs()
    veeam_az_compute = VeeamComputeCost(
        settings=settings,
        inputs=input_workload_obj,
        veeam_backup_totals=full_results,
    )
    veeam_az_compute_totals = veeam_az_compute.calculate_compute_costs()
    cost_comparison = CostComparison(
        veeam_storage_costs=veeam_az_storage_results,
        azure_backup_cost=azure_backup_cost_result,
        veeam_compute_cost=veeam_az_compute_totals,
    )
    cost_comparison_results = cost_comparison.calculate_cost_comparison()
    veeam_backup_response = VeeamBackupResponse(
        inc_backup_size=round(full_results.incremental_size, 2),
        total_backup_volume=round(full_results.total_backup_volume, 2),
        snapshot_volume=round(full_results.snapshot_volume, 2),
        api_put_month=round(full_results.api_put_per_month, 2),
        inc_throughput=round(full_results.incremental_throughput, 2),
        no_workers=full_results.no_workers,
        no_storage_accounts=full_results.no_storage_accounts,
    )
    total_storage_cost_year: list[tuple[str, float]] = []
    for storage in veeam_az_storage_results:
        total_storage_cost_year.append(
            (storage.name, round(storage.total_storage_cost_year, 2))
        )
    veeam_azure_cost_storage_response = VeeamAzureCostStorageResponse(
        total_storage_cost_year=total_storage_cost_year
    )
    compute_cost_total_response = ComputeCostTotalResponse(
        worker_cost=round(veeam_az_compute_totals.total_worker_cost, 2),
        vba_appliance_cost=round(veeam_az_compute_totals.vba_appliance_total, 2),
        vbr_servers_cost=round(veeam_az_compute_totals.vbr_servers_total, 2),
    )
    cost_comparison_response = CostComparisonResponse(
        veeam_backup_total_cost_year=round(
            cost_comparison_results.veeam_backup_total_cost_year, 2
        ),
        azure_backup_total_cost_year=round(
            cost_comparison_results.azure_backup_total_cost_year, 2
        ),
        agent_backup_total_cost_year=round(
            cost_comparison_results.agent_backup_total_cost_year, 2
        ),
    )
    full_response = FullResponse(
        cost_comparison=cost_comparison_response,
        veeam_backup_totals=veeam_backup_response,
        veeam_azure_cost_storage=veeam_azure_cost_storage_response,
        veeam_compute_cost_totals=compute_cost_total_response,
        veeam_vul_cost=veeam_az_compute_totals.vul_cost_year,
        azure_backup_instances_cost=azure_backup_cost_result.azure_backup_instance_cost,
    )
    return full_response
