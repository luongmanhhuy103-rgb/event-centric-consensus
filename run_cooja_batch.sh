#!/bin/bash

VARIANT=$1
FAILURE_RATE=$2
SEED_START=${3:-1}
NUM_RUNS=30

echo "Running $VARIANT at $FAILURE_RATE% destruction, $NUM_RUNS runs"

if [ "$VARIANT" == "baseline" ]; then
    FIRMWARE="consensus-node.z1"
else
    FIRMWARE="variants/${VARIANT}/consensus-node.z1"
fi

for ((i=SEED_START; i<SEED_START+NUM_RUNS; i++)); do
    echo "Run $((i-SEED_START+1)): seed=$i"
    
    CSC_FILE="temp_${VARIANT}_fr${FAILURE_RATE}_run${i}.csc"
    LOG_FILE="logs/${VARIANT}/fr${FAILURE_RATE}_run${i}.log"
    
    sed "s/SEED/$i/g; s|FIRMWARE|$FIRMWARE|g" simulation_template.csc > $CSC_FILE
    
    cd ~/contiki-ng/tools/cooja
    ./gradlew run --args="-nogui -contiki=../../ -simulation=../../examples/event-consensus/$CSC_FILE -log=../../examples/event-consensus/$LOG_FILE"
    cd ~/contiki-ng/examples/event-consensus
    
    rm -f $CSC_FILE
done

echo "Done: $VARIANT at $FAILURE_RATE%"
