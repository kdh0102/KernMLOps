import os
from datetime import datetime
from pathlib import Path
from time import sleep, time
from typing import cast

import data_collection
import data_schema
import polars as pl
from data_schema import demote
from kernmlops_benchmark import Benchmark, BenchmarkNotConfiguredError
from kernmlops_config import ConfigBase


def poll_instrumentation(
  benchmark: Benchmark,
  bpf_programs: list[data_collection.bpf.BPFProgram],
  poll_rate: float = .5,
) -> int:
    loop_start = None
    return_code = benchmark.poll()
    while return_code is None:
        try:
            for bpf_program in bpf_programs:
                bpf_program.poll()
            if poll_rate > 0:
                sleep_time = poll_rate - (time() - loop_start) if loop_start else poll_rate
                if sleep_time > 0:
                    sleep(sleep_time)
                loop_start = time()
            return_code = benchmark.poll()
            # clean data when missed samples - or detect?
        except KeyboardInterrupt:
            benchmark.kill()
            return_code = 0 if benchmark.name() == "faux" else 1
    return return_code


def run_collect(
    *,
    collector_config: ConfigBase,
    benchmark: Benchmark,
    verbose: bool
):
    if not benchmark.is_configured():
        raise BenchmarkNotConfiguredError(f"benchmark {benchmark.name()} is not configured")
    benchmark.setup()

    generic_config = cast(data_collection.GenericCollectorConfig, getattr(collector_config, "generic"))
    bpf_programs = generic_config.get_hooks()
    system_info = data_collection.machine_info().to_polars()
    system_info = system_info.unnest(system_info.columns)
    collection_id = system_info["collection_id"][0]
    output_dir = generic_config.get_output_dir() / "curated" if bpf_programs else generic_config.get_output_dir() / "baseline"

    for bpf_program in bpf_programs:
        bpf_program.load(collection_id)
        if verbose:
            print(f"{bpf_program.name()} BPF program loaded")
    if verbose:
        print("Finished loading BPF programs")
    benchmark.run()
    if verbose:
        print(f"Started benchmark {benchmark.name()}")

    tick = datetime.now()
    return_code = poll_instrumentation(benchmark, bpf_programs, poll_rate=generic_config.poll_rate)
    collection_time_sec = (datetime.now() - tick).total_seconds()
    for bpf_program in bpf_programs:
        bpf_program.close()
    demote()()
    if verbose:
        print(f"Benchmark ran for {collection_time_sec}s")
    if return_code != 0:
        print(f"Benchmark {benchmark.name()} failed with return code {return_code}")
        output_dir = generic_config.get_output_dir() / "failed"

    print("BENCHMARK RUNINFO:", benchmark.start_timestamp, benchmark.finish_timestamp)

    collection_tables: list[data_schema.CollectionTable] = [
        data_schema.SystemInfoTable.from_df(
            system_info.with_columns([
                pl.lit(collection_time_sec).alias("collection_time_sec"),
                pl.lit(os.getpid()).alias("collection_pid"),
                pl.lit(benchmark.name()).alias("benchmark_name"),
                pl.lit([hook.name() for hook in bpf_programs]).cast(pl.List(pl.String())).alias("hooks"),
            ])
        ),
        data_schema.BenchmarkRunInfoTable.from_df(
            pl.DataFrame(benchmark.to_run_info_dict())
        )
    ]
    for bpf_program in bpf_programs:
        collection_tables.extend(bpf_program.pop_data())
    for collection_table in collection_tables:
        if verbose:
            print(f"{collection_table.name()}: {collection_table.table}")
        Path(output_dir / collection_table.name()).mkdir(parents=True, exist_ok=True)
        collection_table.table.write_parquet(output_dir / collection_table.name() / f"{collection_id}.{benchmark.name()}.parquet")
    collection_data = data_schema.CollectionData.from_tables(collection_tables)
    if generic_config.output_graphs:
        collection_data.graph(out_dir=generic_config.get_output_dir() / "graphs")
