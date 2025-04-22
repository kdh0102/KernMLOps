create_yaml_file() {
    local filename="$1"
    shift

    # Start the YAML file
    echo "---" >"$filename"
    echo "collector_config:" >>"$filename"
    echo "  generic:" >>"$filename"
    echo "    poll_rate: 0.005" >>"$filename"
    echo "    output_dir: data" >>"$filename"
    echo "    output_graphs: false" >>"$filename"
    echo "    hooks:" >>"$filename"
    echo "      - memory_usage" >>"$filename"
    echo "      - perf" >>"$filename"
    echo "      - disk_usage" >>"$filename"

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

dir_path="/KernMLOps/stress_ng_combinations"
for dir in "$dir_path"/*/; do
    dir_name=$(basename "$dir")
    echo "Directory: $dir_name"
    rm -rf data/curated
    rm -rf scripts/stress-ng-args
    cp -r $dir scripts/stress-ng-args
    create_yaml_file "overrides.yaml" "starting_idx:1" "num_exps:6" "num_reps:30"
    make stress-ng-benchmarks
    mv data/curated data/$dir_name-curated
    zip -r "data/$dir_name-curated.zip" "data/$dir_name-curated"
    scp "data/$dir_name-curated.zip" dhkim@mew3:/home/dhkim/kernmlops_results
    rm -rf tmp-stress-ng-*
done
