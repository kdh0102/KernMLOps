import subprocess
import time
from dataclasses import dataclass, field
from typing import Literal, cast

import psutil
from data_schema import GraphEngine, demote
from kernmlops_benchmark.benchmark import Benchmark, GenericBenchmarkConfig
from kernmlops_benchmark.errors import (
    BenchmarkNotInCollectionData,
    BenchmarkNotRunningError,
    BenchmarkRunningError,
)
from kernmlops_config import ConfigBase


@dataclass(frozen=True)
class StressNgSetBenchmarkConfig(ConfigBase):
    stress_ng_benchmark: Literal["stress-ng-set"] = "stress-ng-set"
    args: list[str] = field(default_factory=list)


class StressNgSetBenchmark(Benchmark):

    @classmethod
    def name(cls) -> str:
        return "stress_ng_set"

    @classmethod
    def default_config(cls) -> ConfigBase:
        return StressNgSetBenchmarkConfig()

    @classmethod
    def from_config(cls, config: ConfigBase) -> "Benchmark":
        generic_config = cast(GenericBenchmarkConfig, getattr(config, "generic"))
        stress_ng_config = cast(StressNgSetBenchmarkConfig, getattr(config, cls.name()))
        return StressNgSetBenchmark(generic_config=generic_config, config=stress_ng_config)

    def __init__(self, *, generic_config: GenericBenchmarkConfig, config: StressNgSetBenchmarkConfig):
        super().__init__()
        self.generic_config = generic_config
        self.config = config
        self.benchmark_path = "/KernMLOps/scripts/run_stress_ng"
        self.process: subprocess.Popen | None = None

    def is_configured(self) -> bool:
        return self.benchmark_path is not None

    def setup(self) -> None:
        if self.process is not None:
            raise BenchmarkRunningError()
        self.generic_config.generic_setup()

    def run(self) -> None:
        if self.process is not None:
            raise BenchmarkRunningError()

        self.process = subprocess.Popen(
            [self.benchmark_path] + self.config.args,
            preexec_fn=demote(),
            stdout=subprocess.DEVNULL,
        )

    def poll(self) -> int | None:
        if self.process is None:
            raise BenchmarkNotRunningError()
        if not self.start_timestamp:
            p = psutil.Process(self.process.pid)
            if p.status() != "disk-sleep":
                self.start_timestamp = int(time.clock_gettime_ns(time.CLOCK_BOOTTIME) / 1000)
        self.finish_timestamp = int(time.clock_gettime_ns(time.CLOCK_BOOTTIME) / 1000)

        return self.process.poll()

    def wait(self) -> None:
        if self.process is None:
            raise BenchmarkNotRunningError()
        self.process.wait()

    def kill(self) -> None:
        if self.process is None:
            raise BenchmarkNotRunningError()
        self.process.terminate()
        self.finish_timestamp = int(time.clock_gettime_ns(time.CLOCK_BOOTTIME) / 1000)

    @classmethod
    def plot_events(cls, graph_engine: GraphEngine) -> None:
        if graph_engine.collection_data.benchmark != cls.name():
            raise BenchmarkNotInCollectionData()
        # TODO(Patrick): plot when a trial starts/ends

    def to_run_info_dict(self) -> dict[str, list]:
        return {
            "benchmark": [self.name()],
            "args": [" ".join(self.config.args)],
            "start_ts_us": [self.start_timestamp],
            "finish_ts_us": [self.finish_timestamp],
            "return_code": [self.process.returncode],
        }
