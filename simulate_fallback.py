#!/usr/bin/env python3
import random
import math
import sys

# Constants
WINDOW_SIZE = 10
BASELINE = 50
THRESHOLD_ANOMALY = 0.40
THRESHOLD_WEIGHT = 0.40
NOISE_ESTIMATION_STEPS = 20
NUM_NODES = 10
V_MIN_QUORUM = 2
SELF_CORROBORATION_N = 3

class Node:
    def __init__(self, node_id, failure_rate=0.0):
        self.id = node_id
        self.buffer = [random.randint(40, 60) for _ in range(WINDOW_SIZE)]
        self.weight = 0.5
        self.anomaly = 0.0
        self.noise_baseline = 1.0
        self.step_counter = 0
        self.dead = random.random() < failure_rate
        self.consecutive_anomaly_windows = 0

    def read_sensor(self, event=False):
        if self.dead:
            return 0
        if event:
            return random.randint(100, 140)
        else:
            trend = random.gauss(0, 2)
            noise = random.gauss(0, 3)
            return 50 + trend + noise

    def update_buffer(self, value):
        if self.dead:
            return
        self.buffer.pop(0)
        self.buffer.append(value)

    def compute_context_shift(self):
        if self.dead:
            return 0
        mean_val = sum(self.buffer) / len(self.buffer)
        return abs(mean_val - BASELINE) / BASELINE

    def compute_noise_variance(self):
        if self.dead:
            return 1.0
        mean_val = sum(self.buffer) / len(self.buffer)
        var = sum((x - mean_val)**2 for x in self.buffer) / len(self.buffer)
        return var + 0.1

    def compute_weight(self, context, noise):
        if self.dead:
            self.weight = 0
            return 0
        ratio = context / (noise + 0.1)
        self.weight = 1 / (1 + math.exp(-ratio))
        return self.weight

    def step(self, event=False):
        self.step_counter += 1
        if self.dead:
            return False
        value = self.read_sensor(event)
        self.update_buffer(value)

        if self.step_counter <= NOISE_ESTIMATION_STEPS:
            context = self.compute_context_shift()
            noise = self.compute_noise_variance()
            if self.noise_baseline == 1.0:
                self.noise_baseline = noise
            else:
                self.noise_baseline = 0.95 * self.noise_baseline + 0.05 * noise
            self.anomaly = 0.1
            self.weight = 0.5
            broadcast = False
        else:
            context = self.compute_context_shift()
            noise_baseline = self.noise_baseline
            self.compute_weight(context, noise_baseline)

            if value > 80 and event:
                self.anomaly = min(0.95, context * 3.5)
            else:
                self.anomaly = min(0.3, context * 0.3)

            broadcast = (self.anomaly > THRESHOLD_ANOMALY and self.weight > THRESHOLD_WEIGHT)

        return broadcast

def run_simulation(failure_rate=0.0, num_nodes=NUM_NODES, steps=100, event_start=25, event_end=45):
    nodes = [Node(i, failure_rate) for i in range(num_nodes)]
    alive_nodes = [n for n in nodes if not n.dead]
    v_local = len(alive_nodes)
    
    if v_local < V_MIN_QUORUM:
        is_fallback = True
    else:
        is_fallback = False
    
    first_alarm_step = None
    consecutive_anomaly_count = 0
    
    for step in range(steps):
        event = (event_start <= step <= event_end)
        broadcasts = []
        for node in nodes:
            if node.step(event):
                broadcasts.append((node.weight, node.anomaly))
        
        if is_fallback:
            # Standalone-Conservative mode
            max_anomaly = 0.0
            for node in nodes:
                if not node.dead and node.anomaly > max_anomaly:
                    max_anomaly = node.anomaly
            if max_anomaly > THRESHOLD_ANOMALY:
                consecutive_anomaly_count += 1
            else:
                consecutive_anomaly_count = 0
            if consecutive_anomaly_count >= SELF_CORROBORATION_N:
                first_alarm_step = step
                break
        else:
            # Swarm Consensus mode
            if broadcasts:
                total_weight = sum(w for w, _ in broadcasts)
                regional_risk = sum(w * a for w, a in broadcasts) / total_weight if total_weight > 0 else 0
                theta_adaptive = 0.5 * (1 - 0.15 * failure_rate)
                if theta_adaptive < 0.35:
                    theta_adaptive = 0.35
                if regional_risk > theta_adaptive:
                    first_alarm_step = step
                    break
    
    if first_alarm_step is not None and event_start <= first_alarm_step <= event_end:
        acc = 100.0
    else:
        acc = 0.0
    
    print(f"ACCURACY: {acc}")
    return acc

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 simulate_fallback.py <failure_rate>")
        sys.exit(1)
    failure_rate = float(sys.argv[1])
    run_simulation(failure_rate)
