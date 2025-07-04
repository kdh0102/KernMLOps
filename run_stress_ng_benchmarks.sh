chunk_index="$1" # Get the chunk index (M, 0-based) from the second argument
num_chunks="$2"  # Get the chunk size (N) from the first argument

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

dir_path="/KernMLOps/stress_ng_combinations"
host_name=$(hostname)

dirs=("$dir_path"/*/)
total_dirs=${#dirs[@]}
chunk_size=$((total_dirs / num_chunks))
start_index=$((chunk_index * chunk_size))
end_index=$((start_index + chunk_size))

if ((start_index >= total_dirs)); then
    echo "Chunk index out of range: $start_index >= $total_dirs"
    exit 1
fi

for ((i = start_index; i < end_index && i < total_dirs; i++)); do
    dir="${dirs[i]}"
    dir_name=$(basename "$dir")
    rm -rf data/curated
    rm -rf scripts/stress-ng-args
    cp -r "$dir" scripts/stress-ng-args
    file_count=$(find scripts/stress-ng-args -type f -name "*.txt" | wc -l)
    echo "File count: $file_count, Directory: $dir_name"

    batch_size=128
    num_batches=$(( (file_count + batch_size - 1) / batch_size )) # Calculate the number of batches

    for ((batch = 0; batch < num_batches; batch++)); do
        start=$((batch * batch_size))
        end=$((start + batch_size))
        if ((end > file_count)); then
            end=$file_count
        fi
        echo "Processing batch $batch: files $start to $((end - 1))"
        # Add any batch-specific processing logic here
        create_yaml_file "overrides.yaml" "starting_idx:$start" "num_exps:$batch_size" "num_reps:1"
        make stress-ng-benchmarks
        exp_name=training-$dir_name-$batch
        mv data/curated data/$exp_name-curated
        zip -r "data/$exp_name-curated.zip" "data/$exp_name-curated"
        scp "data/$exp_name-curated.zip" dhkim@mew3:/home/dhkim/kernmlops_results/$host_name-$exp_name-curated.zip
        rm -rf data/$exp_name-curated
        rm -rf data/$exp_name-curated.zip
        rm -rf tmp-stress-ng-*
    done
done
