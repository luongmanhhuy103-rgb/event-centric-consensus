#!/bin/bash
echo "Variant,FailureRate,Accuracy,Std"

for variant in baseline no_noise fixed_threshold no_hstrees fallback; do
    for fr in 0.4 0.6; do
        if [ "$variant" == "fallback" ] && [ "$fr" == "0.4" ]; then
            continue
        fi
        LOG_DIR="logs/${variant}"
        PATTERN="fr${fr}_run*.log"
        
        ACCURACIES=$(grep -h "SIMULATION FINISHED: ALARM=" ${LOG_DIR}/${PATTERN} 2>/dev/null | sed 's/.*ALARM=//' | sort -n)
        
        if [ -n "$ACCURACIES" ]; then
            COUNT=$(echo "$ACCURACIES" | wc -l)
            MEAN=$(echo "$ACCURACIES" | awk '{sum+=$1} END {print sum/NR}')
            STD=$(echo "$ACCURACIES" | awk '{sum+=$1; sumsq+=$1*$1} END {print sqrt(sumsq/NR - (sum/NR)^2)}')
            echo "$variant,$fr,$MEAN,$STD"
        fi
    done
done
