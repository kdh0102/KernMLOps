from __future__ import annotations

import time
from dataclasses import dataclass

import polars as pl
import psutil
from data_collection.bpf_instrumentation.bpf_hook import BPFProgram
from data_schema import CollectionTable
from data_schema.cpu_usage import CPUUsageTable


@dataclass(frozen=True)
class CPUUsageData:
  ts_uptime_us: int

  cpu_id: int
  cpu_usage: float

  @classmethod
  def from_usage_list(cls, ts_uptime_us: int, usage_list: list[float]) -> CPUUsageData:
    usage_data_list = []
    for cpu_id, cpu_usage in enumerate(usage_list):
      usage_data_list.append(
        cls(
          ts_uptime_us=ts_uptime_us,
          cpu_id=cpu_id,
          cpu_usage=cpu_usage,
        )
      )
    return usage_data_list

@dataclass(frozen=True)
class CPUUsageDataRaw:
  ts_uptime_us: int
  cpu_usage_list: list[float]

  def parse(self) -> list[CPUUsageData]:
    return CPUUsageData.from_usage_list(
      ts_uptime_us=self.ts_uptime_us,
      usage_list=self.cpu_usage_list,
    )

class CPUUsageHook(BPFProgram):

  @classmethod
  def name(cls) -> str:
    return "cpu_usage"

  def __init__(self):
    pass

  def load(self, collection_id: str):
    self.collection_id = collection_id
    self.cpu_usage = list[CPUUsageDataRaw]()

  def poll(self):
    self.cpu_usage.append(
      CPUUsageDataRaw(
        ts_uptime_us=int(time.clock_gettime_ns(time.CLOCK_BOOTTIME) / 1000),
        cpu_usage_list=psutil.cpu_percent(percpu=True),
      )
    )

  def close(self):
    pass

  def data(self) -> list[CollectionTable]:
    return [
      CPUUsageTable.from_df_id(
        pl.DataFrame(*[
          raw_data.parse()
          for raw_data in self.cpu_usage
        ]),
        collection_id=self.collection_id,
      )
    ]

  def clear(self):
    self.cpu_usage.clear()

  def pop_data(self) -> list[CollectionTable]:
    cpu_table = self.data()
    self.clear()
    return cpu_table
