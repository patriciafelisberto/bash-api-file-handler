#!/usr/bin/env bash

INPUT_FILE="$1"
LOW="$2"
HIGH="$3"

if [ ! -f "$INPUT_FILE" ]; then
    echo "Arquivo não encontrado!"
    exit 1
fi

if [ -z "$LOW" ] || [ -z "$HIGH" ]; then
    echo "Uso: ./between-msgs.sh input LOW HIGH"
    exit 1
fi

awk -v low="$LOW" -v high="$HIGH" '
{
    # numberMessages está no campo 3
    num = $3+0
    if (num >= low && num <= high) {
        print $0
    }
}
' "$INPUT_FILE"
