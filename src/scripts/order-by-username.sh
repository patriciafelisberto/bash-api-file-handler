#!/usr/bin/env bash

INPUT_FILE="$1"
MODE="$2"  # pode ser -desc ou vazio

if [ ! -f "$INPUT_FILE" ]; then
    echo "Arquivo não encontrado!"
    exit 1
fi

if [ "$MODE" == "-desc" ]; then
    sort -r -k1,1 "$INPUT_FILE"
else
    sort -k1,1 "$INPUT_FILE"
fi
