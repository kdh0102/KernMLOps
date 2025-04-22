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
    create_yaml_file "overrides.yaml" "starting_idx:0" "num_exps:6" "num_reps:10"
    make stress-ng-benchmarks
    mv data/curated data/$dir_name-curated
    rm -rf tmp-stress-ng-*
done

# for i in {0..0}; do
#     rm -rf data/curated
#     starting_idx=$(($i * 100))
#     create_yaml_file "overrides.yaml" "starting_idx:$starting_idx" "num_exps:100" "num_reps:1"
#     make stress-ng-benchmarks
#     mv data/curated data/stressor-mix-$i-curated
#     rm -rf tmp-stress-ng-*
# done
