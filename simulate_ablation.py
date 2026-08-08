#!/usr/bin/env python3
import random
import math
import sys


WINDOW_SIZE = 10
BASELINE = 50
THRESHOLD_ANOMALY = 0.40
THRESHOLD_WEIGHT = 0.40
NOISE_ESTIMATION_STEPS = 20
NUM_NODES = 10

class Node:
    def __init__(self, node_id, failure_rate=0.0, variant='full'):
        self.id = node_id
        self.buffer = [random.randint(40, 60) for _ in range(WINDOW_SIZE)]
        self.weight = 0.5
        self.anomaly = 0.0
        self.noise_baseline = 1.0
        self.step_counter = 0
        self.dead = random.random() < failure_rate
        self.variant = variant

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
        if self.variant == 'no_noise':
            ratio = context / 0.1
        else:
            ratio = context / (noise + 0.1)
        self.weight = 1 / (1 + math.exp(-ratio))
        return self.weight

    def compute_anomaly(self, value, context, event):
        if self.variant == 'no_hstrees':
            return 1.0 if value > 80 else 0.0
        else:
            if value > 80 and event:
                return min(0.95, context * 3.5)
            else:
                return min(0.3, context * 0.3)

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
            self.anomaly = self.compute_anomaly(value, context, event)
            broadcast = (self.anomaly > THRESHOLD_ANOMALY and self.weight > THRESHOLD_WEIGHT)

        return broadcast

def run_simulation(variant, failure_rate, num_nodes=NUM_NODES, steps=100, event_start=25, event_end=45):
    nodes = [Node(i, failure_rate, variant) for i in range(num_nodes)]
    alive_nodes = [n for n in nodes if not n.dead]
    if len(alive_nodes) < 2:
        return 0.0

    broadcast_in_event = set()
    for step in range(steps):
        event = (event_start <= step <= event_end)
        for node in nodes:
            if node.step(event):
                if event:
                    broadcast_in_event.add(step)

    total_event_steps = event_end - event_start + 1
    return (len(broadcast_in_event) / total_event_steps) * 100 if total_event_steps > 0 else 0.0

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 simulate_ablation.py <variant> <failure_rate>")
        sys.exit(1)
    variant = sys.argv[1]
    failure_rate = float(sys.argv[2])
    acc = run_simulation(variant, failure_rate)
    print(f"ACCURACY: {acc}")
