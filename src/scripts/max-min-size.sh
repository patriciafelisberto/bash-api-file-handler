#!/usr/bin/env bash

INPUT_FILE="$1"
MODE="$2"  # pode ser -min ou vazio

if [ ! -f "$INPUT_FILE" ]; then
    echo "Arquivo não encontrado!"
    exit 1
fi

# A saída do arquivo tem o formato:
# username folder numberMessages size SIZE
# Ex: juvati_be@uol.com.br inbox 000232478 size 012345671
# O campo size é o último campo.

if [ "$MODE" == "-min" ]; then
    # Menor size
    awk '
    BEGIN {
        min_size = 999999999999
        line_min = ""
    }
    {
        # Ultimo campo é size, mas com zero-padding. Convertemos para int.
        # Campos:
        # $1 = username
        # $2 = folder (inbox)
        # $3 = numberMessages
        # $4 = size (literal "size")
        # $5 = SIZE valor
        size_val = $5+0
        if (size_val < min_size) {
            min_size = size_val
            line_min = $0
        }
    }
    END {
        print line_min
    }
    ' "$INPUT_FILE"
else
    # Maior size
    awk '
    BEGIN {
        max_size = 0
        line_max = ""
    }
    {
        size_val = $5+0
        if (size_val > max_size) {
            max_size = size_val
            line_max = $0
        }
    }
    END {
        print line_max
    }
    ' "$INPUT_FILE"
fi
