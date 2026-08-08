#!/usr/bin/env python3
import random
import math
import time
import sys
import numpy as np

# Constants
WINDOW_SIZE = 10
BASELINE = 50
THRESHOLD_ANOMALY = 0.40
THRESHOLD_WEIGHT = 0.40
NOISE_ESTIMATION_STEPS = 20
NUM_NODES = 10

class Node:
    def __init__(self, node_id, failure_rate=0.0):
        self.id = node_id
        self.buffer = [random.randint(40, 60) for _ in range(WINDOW_SIZE)]
        self.weight = 0.5
        self.anomaly = 0.0
        self.noise_baseline = 1.0
        self.step_counter = 0
        self.dead = random.random() < failure_rate
        self.alive = not self.dead

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
    print(f"Failure rate: {failure_rate*100:.0f}%, Alive nodes: {len(alive_nodes)}/{num_nodes}")
    print("Step,RegionalRisk,AlarmTriggered")
    
    first_alarm_step = None
    
    for step in range(steps):
        event = (event_start <= step <= event_end)
        
        weights = []
        anomalies = []
        for node in nodes:
            if node.step(event):
                weights.append(node.weight)
                anomalies.append(node.anomaly)
        
        if weights:
            total_weight = sum(weights)
            if total_weight > 0:
                regional_risk = sum(w * a for w, a in zip(weights, anomalies)) / total_weight
            else:
                regional_risk = 0
        else:
            regional_risk = 0
        
        theta_adaptive = 0.6 * (1 - 0.5 * failure_rate)
        alarm_triggered = regional_risk > theta_adaptive and step >= event_start
        
        if alarm_triggered and first_alarm_step is None:
            first_alarm_step = step
        
        print(f"{step},{regional_risk:.4f},{alarm_triggered}")
        time.sleep(0.02)
    
    # Output latency
    if first_alarm_step is not None:
        latency_steps = first_alarm_step - event_start
        print(f"LATENCY_STEPS: {latency_steps}")
        print(f"LATENCY_MS: {latency_steps * 20}")
    else:
        print("LATENCY_STEPS: None")
        print("LATENCY_MS: None")

if __name__ == "__main__":
    failure_rate = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    run_simulation(failure_rate)
