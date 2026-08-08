#!/usr/bin/env python3
import random
import math
import time
import sys


WINDOW_SIZE = 10
BASELINE = 50
NUM_NODES = 10
THRESHOLD_ANOMALY = 0.6
THRESHOLD_WEIGHT = 0.5

class NodeTB_CP:
    """Node cho TB-CP (Trust-Based Consensus Protocol)"""
    def __init__(self, node_id, failure_rate=0.0):
        self.id = node_id
        self.buffer = [random.randint(40, 60) for _ in range(WINDOW_SIZE)]
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

    def compute_anomaly(self, value):
        return 0.9 if value > 80 else 0.1

    def compute_weight(self):
        if self.dead:
            return 0
        uptime_score = self.uptime / 100.0
        battery_score = self.battery / 100.0
        return 0.5 * uptime_score + 0.5 * battery_score

    def step(self, event=False):
        self.step_counter += 1
        if self.dead:
            return False

        value = self.read_sensor(event)
        self.update_buffer(value)
        anomaly = self.compute_anomaly(value)
        weight = self.compute_weight()

        broadcast = (anomaly > THRESHOLD_ANOMALY and weight > THRESHOLD_WEIGHT)

        # Log: NodeID,Step,Value,Anomaly,Weight,Broadcast
        print(f"{self.id},{self.step_counter},{value:.2f},{anomaly:.2f},{weight:.3f},{broadcast}")
        return broadcast

class NodeLEACH:
    """Node cho LEACH (cluster-based)"""
    def __init__(self, node_id, failure_rate=0.0):
        self.id = node_id
        self.buffer = [random.randint(40, 60) for _ in range(WINDOW_SIZE)]
        self.step_counter = 0
        self.dead = random.random() < failure_rate
        self.alive = not self.dead
        self.is_cluster_head = False
        self.cluster_members = []

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

    def step(self, event=False):
        self.step_counter += 1
        if self.dead:
            return False

        value = self.read_sensor(event)
        self.update_buffer(value)

        if self.is_cluster_head:
            mean_val = sum(self.buffer) / len(self.buffer)
            anomaly = 0.9 if mean_val > 80 else 0.1
            broadcast = (anomaly > THRESHOLD_ANOMALY)
        else:
            broadcast = False

        print(f"{self.id},{self.step_counter},{value:.2f},{0.0},{0.0},{broadcast}")
        return broadcast

def run_simulation_baseline(baseline_type, failure_rate=0.0, num_nodes=NUM_NODES, steps=100, event_start=25, event_end=45):
    if baseline_type == 'tbcp':
        nodes = [NodeTB_CP(i, failure_rate) for i in range(num_nodes)]
    elif baseline_type == 'leach':
        nodes = [NodeLEACH(i, failure_rate) for i in range(num_nodes)]
        num_ch = max(1, int(num_nodes * 0.2))
        ch_indices = random.sample(range(num_nodes), num_ch)
        for idx in ch_indices:
            nodes[idx].is_cluster_head = True
            nodes[idx].cluster_members = [n for n in nodes if n.id != idx and not n.dead]
    else:
        return

    alive_nodes = [n for n in nodes if not n.dead]
    print(f"Failure rate: {failure_rate*100:.0f}%, Alive nodes: {len(alive_nodes)}/{num_nodes}")
    print("NodeID,Step,Value,Anomaly,Weight,Broadcast")

    for step in range(steps):
        event = (event_start <= step <= event_end)
        for node in nodes:
            node.step(event)
        time.sleep(0.02)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 simulate_baselines.py <tbcp|leach> <failure_rate>")
        sys.exit(1)
    baseline = sys.argv[1]
    failure_rate = float(sys.argv[2])
    run_simulation_baseline(baseline, failure_rate)
