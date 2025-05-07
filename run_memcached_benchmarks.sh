chunk_index="$1" # Get the chunk index (M, 0-based) from the second argument
num_chunks="$2"  # Get the chunk size (N) from the first argument

create_yaml_file() {
    local filename="$1"
    shift

    # Start the YAML file
    echo "---" >"$filename"
    echo "collector_config:" >>"$filename"
    echo "  generic:" >>"$filename"
    echo "    poll_rate: 0.05" >>"$filename"
    echo "    output_dir: data" >>"$filename"
    echo "    output_graphs: false" >>"$filename"
    echo "    hooks:" >>"$filename"
    echo "      - memory_usage" >>"$filename"
    echo "      - perf" >>"$filename"
    echo "      - disk_usage" >>"$filename"
    echo "      - cpu_usage" >>"$filename"

    echo "benchmark_config:" >>"$filename"
    echo "  memcached:" >>"$filename"


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

config_file_path="memcached_config/solutions.txt"

if [[ -f "$config_file_path" ]]; then
    while IFS= read -r line || [[ -n "$line" ]]; do
        IFS="-" read -r var1 var2 var3 var4 var5 var6 var7 <<< "$line"
        echo "Parsed values: $var1, $var2, $var3, $var4, $var5, $var6, $var7"
        rm -rf data/curated
        create_yaml_file "overrides.yaml" "operation_count:100000" "record_count:100000" "read_proportion:$var1" "update_proportion:$var2" "scan_proportion:$var3" "insert_proportion:$var4" "rmw_proportion:$var5" "scan_proportion:$var6" "delete_proportion:$var7"
        make benchmark-memcached
        mv data/curated data/$line-curated
        zip -r "data/$line-curated.zip" "data/$line-curated"
        scp "data/$line-curated.zip" dhkim@mew3:/home/dhkim/kernmlops_results/$host_name-$line-curated.zip
        rm -rf data/$line-curated
        rm -rf data/$line-curated.zip
    done < "$config_file_path"
else
    echo "Configuration file not found: $config_file_path"
    exit 1
fi
