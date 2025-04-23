from __future__ import annotations

import polars as pl
from data_schema.schema import (
    UPTIME_TIMESTAMP,
    CollectionGraph,
    CollectionTable,
    GraphEngine,
)


class CPUUsageTable(CollectionTable):

    @classmethod
    def name(cls) -> str:
        return "cpu_usage"

    @classmethod
    def schema(cls) -> pl.Schema:
        return pl.Schema({
            UPTIME_TIMESTAMP: pl.Int64(),
            "cpu_id": pl.Int64(),
            "cpu_usage": pl.Float32(),
        })

    @classmethod
    def from_df(cls, table: pl.DataFrame) -> CPUUsageTable:
        return CPUUsageTable(table=table)

    def __init__(self, table: pl.DataFrame):
        self._table = table

    @property
    def table(self) -> pl.DataFrame:
        return self._table

    def filtered_table(self) -> pl.DataFrame:
        return self.table

    def graphs(self) -> list[type[CollectionGraph]]:
        return [CPUUsageGraph]


class CPUUsageGraph(CollectionGraph):

    @classmethod
    def with_graph_engine(cls, graph_engine: GraphEngine) -> CollectionGraph | None:
        cpu_usage_table = graph_engine.collection_data.get(CPUUsageTable)
        if cpu_usage_table is not None:
            return CPUUsageGraph(
                graph_engine=graph_engine,
                cpu_usage_table=cpu_usage_table
            )
        return None

    @classmethod
    def base_name(cls) -> str:
        return "System CPU Usage"

    @property
    def plot_lines(self) -> list[str]:
        return [
            "read_kb",
            "write_kb",
        ]

    def __init__(
        self,
        graph_engine: GraphEngine,
        cpu_usage_table: CPUUsageTable,
    ):
        self.graph_engine = graph_engine
        self.collection_data = graph_engine.collection_data
        self._cpu_usage_table = cpu_usage_table

    def name(self) -> str:
        return f"{self.base_name()} for Collection {self.collection_data.id}"

    def x_axis(self) -> str:
        return "Benchmark Runtime (sec)"

    def y_axis(self) -> str:
        return "Memory (KB)"

    def plot(self) -> None:
        pass

    def plot_trends(self) -> None:
        cpu_df = self._cpu_usage_table.filtered_table()
        start_uptime_sec = self.collection_data.start_uptime_sec

        for plot_line in self.plot_lines:
            self.graph_engine.plot(
                (
                    (cpu_df.select(UPTIME_TIMESTAMP) / 1_000_000.0) - start_uptime_sec
                ).to_series().to_list(),
                (cpu_df.select(plot_line)).to_series().to_list(),
                label=plot_line.replace("bytes", "kb"),
                y_axis=self.y_axis(),
            )
