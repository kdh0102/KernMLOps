create_yaml_file() {
    local filename="$1"
    shift

    # Start the YAML file
    echo "---" >"$filename"
    echo "collector_config:" >>"$filename"
    echo "  generic:" >>"$filename"
    echo "    poll_rate: 0.1" >>"$filename"
    echo "    output_dir: data" >>"$filename"
    echo "    output_graphs: false" >>"$filename"
    echo "    hooks:" >>"$filename"
    echo "      - memory_usage" >>"$filename"
    echo "      - perf" >>"$filename"
    echo "      - disk_usage" >>"$filename"
    echo "      - cpu_usage" >>"$filename"

    echo "benchmark_config:" >>"$filename"
    echo "  stress_ng_benchmarks:" >>"$filename"

    # Loop through the remaining arguments
    while (($#)); do
        local key="${1%%:*}"
        local value="${1#*:}"
        echo "    $key: $value" >>"$filename"
        shift
    done
}

host_name=$(hostname)

for benchmark_name in "memcached"; do


    rm -rf data/curated
    create_yaml_file "overrides.yaml" "starting_idx:0" "num_exps:$file_count" "num_reps:3"
    make benchmark-$benchmark_name
    mv data/curated data/$dir_name-curated
    zip -r "data/$dir_name-curated.zip" "data/$dir_name-curated"
    scp "data/$dir_name-curated.zip" dhkim@mew3:/home/dhkim/kernmlops_results/$host_name-$dir_name-curated.zip
    rm -rf data/$dir_name-curated
    rm -rf data/$dir_name-curated.zip
done
