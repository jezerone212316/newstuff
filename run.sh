#!/bin/sh
set -eu

current_time=$(date "+%Y.%m.%d-%H.%M")
if [ -n "${upload:-}" ]; then
    root_dir=/
    mkdir -p /xml_files /reports
else
    root_dir=/shared/
fi

report_extension="${format:-tex}"
xml_dir="xml_files/$current_time"
report_file="reports/report_$current_time.$report_extension"

upload() {
    if [ -z "${upload:-}" ]; then
        return 0
    fi

    case "${upload}" in
        aws)
            python /aws_push.py "$1"
            ;;
        gcp)
            python /gcp_push.py "$1"
            ;;
        *)
            echo "Unsupported upload backend: ${upload}" >&2
            return 1
            ;;
    esac
}

get_filename() {
    printf '%s' "$1" | tr '/' '-'
}

mkdir -p "$root_dir$xml_dir"
while IFS= read -r line || [ -n "$line" ]; do
    line=$(printf '%s' "$line" | tr -d '\r')
    [ -n "$line" ] || continue

    filename="$(get_filename "$line").xml"
    nmap -sV -oX "$root_dir$xml_dir/$filename" -oN - -v1 "$@" --script=vulners/vulners.nse "$line"
    upload "$xml_dir/$filename"
done < /shared/ips.txt

python /output_report.py "$root_dir$xml_dir" "$root_dir$report_file" /shared/ips.txt
if [ "$report_extension" = "tex" ]; then
    sed -i 's/_/\\_/g' "$root_dir$report_file"
    sed -i 's/\$/\\\$/g' "$root_dir$report_file"
    sed -i 's/#/\\#/g' "$root_dir$report_file"
    sed -i 's/%/\\%/g' "$root_dir$report_file"
fi
upload "$report_file"
