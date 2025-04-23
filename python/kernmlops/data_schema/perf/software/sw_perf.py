from __future__ import annotations

import polars as pl
from bcc import PerfType
from data_schema.memory_usage import MemoryUsageGraph
from data_schema.perf.perf_schema import (
    CumulativePerfGraph,
    CustomHWEventID,
    PerfCollectionTable,
    PerfSoftwareConfig,
    RatePerfGraph,
)
from data_schema.schema import (
    CollectionGraph,
    GraphEngine,
)

class SoftwareCPUCyclesPerfTable(PerfCollectionTable):

    @classmethod
    def name(cls) -> str:
        return "sw_cpu_cycles"

    @classmethod
    def ev_type(cls) -> int:
        return PerfType.SOFTWARE

    @classmethod
    def ev_config(cls) -> int:
      return PerfSoftwareConfig.config(
          event=PerfSoftwareConfig.Event.PERF_COUNT_SW_CPU_CLOCK,
      )

    @classmethod
    def hw_ids(cls) -> list[CustomHWEventID]:
        return []

    @classmethod
    def component_name(cls) -> str:
        return "sw_cpu_cycles"

    @classmethod
    def measured_event_name(cls) -> str:
        return "Counts"

    @classmethod
    def from_df(cls, table: pl.DataFrame) -> SoftwareCPUCyclesPerfTable:
        return SoftwareCPUCyclesPerfTable(table=table.cast(cls.schema(), strict=True))

    def __init__(self, table: pl.DataFrame):
        self._table = table

    @property
    def table(self) -> pl.DataFrame:
        return self._table

    def filtered_table(self) -> pl.DataFrame:
        return self.table

    def graphs(self) -> list[type[CollectionGraph]]:
        return [SoftwareCPUCyclesRateGraph, SoftwareCPUCyclesCumulativeGraph]

class SoftwareCPUCyclesRateGraph(RatePerfGraph):
    @classmethod
    def perf_table_type(cls) -> type[PerfCollectionTable]:
        return SoftwareCPUCyclesPerfTable

    @classmethod
    def trend_graph(cls) -> type[CollectionGraph] | None:
        return MemoryUsageGraph

    @classmethod
    def with_graph_engine(cls, graph_engine: GraphEngine) -> CollectionGraph | None:
        perf_table = graph_engine.collection_data.get(cls.perf_table_type())
        if perf_table is not None:
            return SoftwareCPUCyclesRateGraph(
                graph_engine=graph_engine,
                perf_table=perf_table
            )
        return None

class SoftwareCPUCyclesCumulativeGraph(CumulativePerfGraph):
    @classmethod
    def perf_table_type(cls) -> type[PerfCollectionTable]:
        return SoftwareCPUCyclesPerfTable

    @classmethod
    def trend_graph(cls) -> type[CollectionGraph] | None:
        return None

    @classmethod
    def with_graph_engine(cls, graph_engine: GraphEngine) -> CollectionGraph | None:
        perf_table = graph_engine.collection_data.get(cls.perf_table_type())
        if perf_table is not None:
            return SoftwareCPUCyclesCumulativeGraph(
                graph_engine=graph_engine,
                perf_table=perf_table
            )
        return None

class SoftwareTaskClockPerfTable(PerfCollectionTable):

    @classmethod
    def name(cls) -> str:
        return "sw_task_clock"

    @classmethod
    def ev_type(cls) -> int:
        return PerfType.SOFTWARE

    @classmethod
    def ev_config(cls) -> int:
      return PerfSoftwareConfig.config(
          event=PerfSoftwareConfig.Event.PERF_COUNT_SW_TASK_CLOCK,
      )

    @classmethod
    def hw_ids(cls) -> list[CustomHWEventID]:
        return []

    @classmethod
    def component_name(cls) -> str:
        return "sw_task_clock"

    @classmethod
    def measured_event_name(cls) -> str:
        return "Counts"

    @classmethod
    def from_df(cls, table: pl.DataFrame) -> SoftwareTaskClockPerfTable:
        return SoftwareTaskClockPerfTable(table=table.cast(cls.schema(), strict=True))

    def __init__(self, table: pl.DataFrame):
        self._table = table

    @property
    def table(self) -> pl.DataFrame:
        return self._table

    def filtered_table(self) -> pl.DataFrame:
        return self.table

    def graphs(self) -> list[type[CollectionGraph]]:
        return [SoftwareTaskClockRateGraph, SoftwareTaskClockCumulativeGraph]

class SoftwareTaskClockRateGraph(RatePerfGraph):
    @classmethod
    def perf_table_type(cls) -> type[PerfCollectionTable]:
        return SoftwareTaskClockPerfTable

    @classmethod
    def trend_graph(cls) -> type[CollectionGraph] | None:
        return MemoryUsageGraph

    @classmethod
    def with_graph_engine(cls, graph_engine: GraphEngine) -> CollectionGraph | None:
        perf_table = graph_engine.collection_data.get(cls.perf_table_type())
        if perf_table is not None:
            return SoftwareTaskClockRateGraph(
                graph_engine=graph_engine,
                perf_table=perf_table
            )
        return None

class SoftwareTaskClockCumulativeGraph(CumulativePerfGraph):
    @classmethod
    def perf_table_type(cls) -> type[PerfCollectionTable]:
        return SoftwareTaskClockPerfTable

    @classmethod
    def trend_graph(cls) -> type[CollectionGraph] | None:
        return None

    @classmethod
    def with_graph_engine(cls, graph_engine: GraphEngine) -> CollectionGraph | None:
        perf_table = graph_engine.collection_data.get(cls.perf_table_type())
        if perf_table is not None:
            return SoftwareTaskClockCumulativeGraph(
                graph_engine=graph_engine,
                perf_table=perf_table
            )
        return None

class MajorPageFaultPerfTable(PerfCollectionTable):

    @classmethod
    def name(cls) -> str:
        return "major_page_faults"

    @classmethod
    def ev_type(cls) -> int:
        return PerfType.SOFTWARE

    @classmethod
    def ev_config(cls) -> int:
      return PerfSoftwareConfig.config(
          event=PerfSoftwareConfig.Event.PERF_COUNT_SW_PAGE_FAULTS_MAJ,
      )

    @classmethod
    def hw_ids(cls) -> list[CustomHWEventID]:
        return []

    @classmethod
    def component_name(cls) -> str:
        return "major_page_faults"

    @classmethod
    def measured_event_name(cls) -> str:
        return "Counts"

    @classmethod
    def from_df(cls, table: pl.DataFrame) -> MajorPageFaultPerfTable:
        return MajorPageFaultPerfTable(table=table.cast(cls.schema(), strict=True))

    def __init__(self, table: pl.DataFrame):
        self._table = table

    @property
    def table(self) -> pl.DataFrame:
        return self._table

    def filtered_table(self) -> pl.DataFrame:
        return self.table

    def graphs(self) -> list[type[CollectionGraph]]:
        return [MajorPageFaultRateGraph, MajorPageFaultCumulativeGraph]

class MajorPageFaultRateGraph(RatePerfGraph):
    @classmethod
    def perf_table_type(cls) -> type[PerfCollectionTable]:
        return MajorPageFaultPerfTable

    @classmethod
    def trend_graph(cls) -> type[CollectionGraph] | None:
        return MemoryUsageGraph

    @classmethod
    def with_graph_engine(cls, graph_engine: GraphEngine) -> CollectionGraph | None:
        perf_table = graph_engine.collection_data.get(cls.perf_table_type())
        if perf_table is not None:
            return MajorPageFaultRateGraph(
                graph_engine=graph_engine,
                perf_table=perf_table
            )
        return None

class MajorPageFaultCumulativeGraph(CumulativePerfGraph):
    @classmethod
    def perf_table_type(cls) -> type[PerfCollectionTable]:
        return MajorPageFaultPerfTable

    @classmethod
    def trend_graph(cls) -> type[CollectionGraph] | None:
        return None

    @classmethod
    def with_graph_engine(cls, graph_engine: GraphEngine) -> CollectionGraph | None:
        perf_table = graph_engine.collection_data.get(cls.perf_table_type())
        if perf_table is not None:
            return MajorPageFaultCumulativeGraph(
                graph_engine=graph_engine,
                perf_table=perf_table
            )
        return None
