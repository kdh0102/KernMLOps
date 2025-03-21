"""Library for maintaining, manipulating, and using schemas."""

import os
from pwd import getpwnam
from typing import Callable

from data_schema import perf
from data_schema.block_io import BlockIOLatencyTable, BlockIOQueueTable, BlockIOTable
from data_schema.disk_usage import DiskUsageTable
from data_schema.file_data import FileDataTable
from data_schema.huge_pages import CollapseHugePageDataTable
from data_schema.memory_usage import MemoryUsageTable
from data_schema.process_metadata import ProcessMetadataTable
from data_schema.quanta_runtime import QuantaQueuedTable, QuantaRuntimeTable
from data_schema.schema import (
    UPTIME_TIMESTAMP,
    CollectionData,
    CollectionGraph,
    CollectionTable,
    GraphEngine,
    SystemInfoTable,
    BenchmarkRunInfoTable,
    collection_id_column,
    cumulative_pma_as_pdf,
)

table_types: list[type[CollectionTable]] = [
    SystemInfoTable,
    BenchmarkRunInfoTable,
    QuantaRuntimeTable,
    QuantaQueuedTable,
    ProcessMetadataTable,
    FileDataTable,
    MemoryUsageTable,
    BlockIOLatencyTable,
    BlockIOQueueTable,
    BlockIOTable,
    CollapseHugePageDataTable,
    DiskUsageTable,
] + list(perf.perf_table_types.values())

def demote(user_id: int | None = None, group_id: int | None = None) -> Callable[[], None]:
    def no_op():
        pass
    if user_id is None:
        # if the user id is unspecified and the account is not privileged do nothing
        if os.getuid() >= 1000:
            return no_op
        if "UNAME" in os.environ:
            user_id = getpwnam(os.environ["UNAME"]).pw_uid
        else:
            raise Exception("not enough information to demote user")
    if group_id is None:
        group_id = int(os.environ.get("GID", user_id))

    def do_demote():
        os.setgid(group_id)
        os.setuid(user_id)
    return do_demote

__all__ = [
    "UPTIME_TIMESTAMP",
    "collection_id_column",
    "cumulative_pma_as_pdf",
    "demote",
    "table_types",
    "perf",
    "CollectionTable",
    "CollectionData",
    "CollectionGraph",
    "GraphEngine",
    "SystemInfoTable",
]
