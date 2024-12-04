import shutil
import subprocess
from dataclasses import dataclass
from typing import Literal, cast

from data_schema import GraphEngine, demote
from kernmlops_benchmark.benchmark import Benchmark, GenericBenchmarkConfig
from kernmlops_benchmark.errors import (
  BenchmarkNotInCollectionData,
  BenchmarkNotRunningError,
  BenchmarkRunningError,
)
from kernmlops_config import ConfigBase


@dataclass(frozen=True)
class StressNgBenchmarkConfig(ConfigBase):
  stress_ng_benchmark: Literal["stress-ng"] = "stress-ng"
  trials: int = 2


class StressNgBenchmark(Benchmark):

    @classmethod
    def name(cls) -> str:
        return "stress_ng"

    @classmethod
    def default_config(cls) -> ConfigBase:
        return StressNgBenchmarkConfig()

    @classmethod
    def from_config(cls, config: ConfigBase) -> "Benchmark":
        generic_config = cast(GenericBenchmarkConfig, getattr(config, "generic"))
        stress_ng_config = cast(StressNgBenchmarkConfig, getattr(config, cls.name()))
        return StressNgBenchmark(generic_config=generic_config, config=stress_ng_config)

    def __init__(self, *, generic_config: GenericBenchmarkConfig, config: StressNgBenchmarkConfig):
        self.generic_config = generic_config
        self.config = config
        self.benchmark_path = shutil.which(self.config.stress_ng_benchmark)
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
            [
                self.benchmark_path,
                "--vm",
                "1",
                "--vm-ops",
                "1000000",
                "--timeout",
                "10s",
            ],
            preexec_fn=demote(),
            stdout=subprocess.DEVNULL,
        )

    def poll(self) -> int | None:
        if self.process is None:
            raise BenchmarkNotRunningError()
        return self.process.poll()

    def wait(self) -> None:
        if self.process is None:
            raise BenchmarkNotRunningError()
        self.process.wait()

    def kill(self) -> None:
        if self.process is None:
            raise BenchmarkNotRunningError()
        self.process.terminate()

    @classmethod
    def plot_events(cls, graph_engine: GraphEngine) -> None:
        if graph_engine.collection_data.benchmark != cls.name():
            raise BenchmarkNotInCollectionData()
        # TODO(Patrick): plot when a trial starts/ends