from __future__ import annotations

import polars as pl
from bcc import PerfType
from data_schema.memory_usage import MemoryUsageGraph
from data_schema.perf.perf_schema import (
    CumulativePerfGraph,
    CustomHWEventID,
    PerfCollectionTable,
    PerfHWCacheConfig,
    RatePerfGraph,
)
from data_schema.schema import (
    CollectionGraph,
    GraphEngine,
)


class LLCPerfTable(PerfCollectionTable):

    @classmethod
    def name(cls) -> str:
        return "llc_misses"

    @classmethod
    def ev_type(cls) -> int:
        return PerfType.HW_CACHE

    @classmethod
    def ev_config(cls) -> int:
      return PerfHWCacheConfig.config(
        cache=PerfHWCacheConfig.Cache.PERF_COUNT_HW_CACHE_LL,
        op=PerfHWCacheConfig.Op.PERF_COUNT_HW_CACHE_OP_READ,
        result=PerfHWCacheConfig.Result.PERF_COUNT_HW_CACHE_RESULT_MISS,
      )

    @classmethod
    def hw_ids(cls) -> list[CustomHWEventID]:
        return []

    @classmethod
    def component_name(cls) -> str:
        return "LLC"

    @classmethod
    def measured_event_name(cls) -> str:
        return "Misses"

    @classmethod
    def from_df(cls, table: pl.DataFrame) -> LLCPerfTable:
        return LLCPerfTable(table=table.cast(cls.schema(), strict=True))

    def __init__(self, table: pl.DataFrame):
        self._table = table

    @property
    def table(self) -> pl.DataFrame:
        return self._table

    def filtered_table(self) -> pl.DataFrame:
        return self.table

    def graphs(self) -> list[type[CollectionGraph]]:
        return [LLCRateGraph, LLCCumulativeGraph]


class LLCRateGraph(RatePerfGraph):
    @classmethod
    def perf_table_type(cls) -> type[PerfCollectionTable]:
        return LLCPerfTable

    @classmethod
    def trend_graph(cls) -> type[CollectionGraph] | None:
        return MemoryUsageGraph

    @classmethod
    def with_graph_engine(cls, graph_engine: GraphEngine) -> CollectionGraph | None:
        perf_table = graph_engine.collection_data.get(cls.perf_table_type())
        if perf_table is not None:
            return LLCRateGraph(
                graph_engine=graph_engine,
                perf_table=perf_table
            )
        return None


class LLCCumulativeGraph(CumulativePerfGraph):
    @classmethod
    def perf_table_type(cls) -> type[PerfCollectionTable]:
        return LLCPerfTable

    @classmethod
    def trend_graph(cls) -> type[CollectionGraph] | None:
        return None

    @classmethod
    def with_graph_engine(cls, graph_engine: GraphEngine) -> CollectionGraph | None:
        perf_table = graph_engine.collection_data.get(cls.perf_table_type())
        if perf_table is not None:
            return LLCCumulativeGraph(
                graph_engine=graph_engine,
                perf_table=perf_table
            )
        return None


class LLCHitPerfTable(PerfCollectionTable):

    @classmethod
    def name(cls) -> str:
        return "llc_hits"

    @classmethod
    def ev_type(cls) -> int:
        return PerfType.HW_CACHE

    @classmethod
    def ev_config(cls) -> int:
      return PerfHWCacheConfig.config(
        cache=PerfHWCacheConfig.Cache.PERF_COUNT_HW_CACHE_LL,
        op=PerfHWCacheConfig.Op.PERF_COUNT_HW_CACHE_OP_READ,
        result=PerfHWCacheConfig.Result.PERF_COUNT_HW_CACHE_RESULT_ACCESS,
      )

    @classmethod
    def hw_ids(cls) -> list[CustomHWEventID]:
        return []

    @classmethod
    def component_name(cls) -> str:
        return "LLC"

    @classmethod
    def measured_event_name(cls) -> str:
        return "Hits"

    @classmethod
    def from_df(cls, table: pl.DataFrame) -> LLCHitPerfTable:
        return LLCHitPerfTable(table=table.cast(cls.schema(), strict=True))

    def __init__(self, table: pl.DataFrame):
        self._table = table

    @property
    def table(self) -> pl.DataFrame:
        return self._table

    def filtered_table(self) -> pl.DataFrame:
        return self.table

    def graphs(self) -> list[type[CollectionGraph]]:
        return [LLCHitRateGraph, LLCHitCumulativeGraph]


class LLCHitRateGraph(RatePerfGraph):
    @classmethod
    def perf_table_type(cls) -> type[PerfCollectionTable]:
        return LLCHitPerfTable

    @classmethod
    def trend_graph(cls) -> type[CollectionGraph] | None:
        return MemoryUsageGraph

    @classmethod
    def with_graph_engine(cls, graph_engine: GraphEngine) -> CollectionGraph | None:
        perf_table = graph_engine.collection_data.get(cls.perf_table_type())
        if perf_table is not None:
            return LLCHitRateGraph(
                graph_engine=graph_engine,
                perf_table=perf_table
            )
        return None


class LLCHitCumulativeGraph(CumulativePerfGraph):
    @classmethod
    def perf_table_type(cls) -> type[PerfCollectionTable]:
        return LLCHitPerfTable

    @classmethod
    def trend_graph(cls) -> type[CollectionGraph] | None:
        return None

    @classmethod
    def with_graph_engine(cls, graph_engine: GraphEngine) -> CollectionGraph | None:
        perf_table = graph_engine.collection_data.get(cls.perf_table_type())
        if perf_table is not None:
            return LLCHitCumulativeGraph(
                graph_engine=graph_engine,
                perf_table=perf_table
            )
        return None
