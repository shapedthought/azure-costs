import json
import pprint
import functools
import settings as st
import inputs as ip


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
        settings = st.Inputs.from_dict(settings)

    with open("inputs.json", "r") as f:
        input_vm_workloads = json.load(f)
        input_vm_workloads = ip.Inputs.from_dict(input_vm_workloads)

    pprint.pprint(input_vm_workloads.__dict__)


if __name__ == "__main__":
    main()
