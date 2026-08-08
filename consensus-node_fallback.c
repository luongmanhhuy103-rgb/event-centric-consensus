/* ============================================================
 * Event-Centric Adaptive Consensus - Full Firmware
 * Cho Cooja/Contiki-NG trên Z1 mote (MSP430)
 * ============================================================ */

#include "contiki.h"
#include "net/ipv6/simple-udp.h"
#include "dev/serial-line.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ============================================================
 * ============================================================ */
#define WINDOW_SIZE         10
#define BASELINE            50.0f
#define THRESHOLD_ANOMALY   0.40f
#define THRESHOLD_WEIGHT    0.40f
#define NOISE_ESTIMATION_STEPS  20
#define PI_LOCAL            0.6f
#define V_MIN_QUORUM 2

/* ============================================================
 * ============================================================ */
float sigmoid_approx(float x) {
    float ax = x < 0 ? -x : x;
    return 0.5f + 0.5f * (x / (1.0f + ax));
}

/* ============================================================
 * ============================================================ */
static float sensor_buffer[WINDOW_SIZE];
static uint8_t buffer_index = 0;
static float noise_baseline = 1.0f;
static float weight = 0.5f;
static float anomaly = 0.0f;
static uint8_t dead = 0;
static uint8_t consecutive_anomaly_windows = 0;

/* ============================================================
 * ============================================================ */

float compute_context_shift(float *buffer, uint8_t len, float baseline) {
    float sum = 0.0f;
    for (uint8_t i = 0; i < len; i++) {
        sum += buffer[i];
    }
    float mean = sum / len;
    float diff = mean - baseline;
    if (diff < 0) diff = -diff;
    return diff / baseline;
}

float compute_noise_variance(float *buffer, uint8_t len) {
    float sum = 0.0f;
    for (uint8_t i = 0; i < len; i++) {
        sum += buffer[i];
    }
    float mean = sum / len;
    float var = 0.0f;
    for (uint8_t i = 0; i < len; i++) {
        float d = buffer[i] - mean;
        var += d * d;
    }
    var = var / len + 0.1f;
    return var;
}

float compute_weight(float context, float noise) {
    float ratio = context / (noise + 0.001f);
    return sigmoid_approx(ratio);
}

float read_sensor(uint8_t event) {
    if (dead) return 0.0f;
    if (event) {
        return 100.0f + (rand() % 40);
    } else {
        return 50.0f + (rand() % 20) - 10;
    }
}

void update_buffer(float value) {
    sensor_buffer[buffer_index] = value;
    buffer_index = (buffer_index + 1) % WINDOW_SIZE;
}

/* ============================================================
 * PROCESS CHÍNH
 * ============================================================ */
PROCESS(consensus_process, "Event-Centric Consensus");
AUTOSTART_PROCESSES(&consensus_process);

PROCESS_THREAD(consensus_process, ev, data) {
    static struct etimer timer;
    static uint16_t event_start = 25;
    static uint16_t event_end = 45;
    static uint16_t step = 0;
    static uint8_t alarm_triggered = 0;
    
    PROCESS_BEGIN();
    
    printf("=== Event-Centric Consensus Node started ===\n");
    etimer_set(&timer, CLOCK_SECOND / 2);
    
    while(1) {
        PROCESS_WAIT_EVENT();
        
        if(etimer_expired(&timer)) {
            step++;
            uint8_t event = (step >= event_start && step <= event_end);
            
            float value = read_sensor(event);
            update_buffer(value);
            
            if (step > NOISE_ESTIMATION_STEPS) {
                float context = compute_context_shift(sensor_buffer, WINDOW_SIZE, BASELINE);
                float noise = compute_noise_variance(sensor_buffer, WINDOW_SIZE);
                noise_baseline = 0.95f * noise_baseline + 0.05f * noise;
                weight = compute_weight(context, noise_baseline);
                
                if (value > 80.0f && event) {
                    anomaly = 0.9f;
                } else {
                    anomaly = 0.1f;
                }
                
                if (anomaly > THRESHOLD_ANOMALY && weight > THRESHOLD_WEIGHT) {
                consecutive_anomaly_windows++;
                if (consecutive_anomaly_windows >= 3) {
                    alarm_triggered = 1;
                    printf("FALLBACK_ALARM: step=%d\n", step);
                }
            } else if (step > NOISE_ESTIMATION_STEPS) {
                consecutive_anomaly_windows = 0;
                    alarm_triggered = 1;
                    printf("ALARM: step=%d, anomaly=%.2f, weight=%.2f\n", step, (double)anomaly, (double)weight);
                }
            }
            
            printf("STEP:%d,VAL:%.2f,C:%.3f,N:%.3f,W:%.3f,A:%.2f\n",
                   step,
                   (double)value,
                   (double)(step > NOISE_ESTIMATION_STEPS ? compute_context_shift(sensor_buffer, WINDOW_SIZE, BASELINE) : 0.0f),
                   (double)noise_baseline,
                   (double)weight,
                   (double)anomaly);
            
            if (step >= 100) {
                printf("=== SIMULATION FINISHED: ALARM=%d ===\n", alarm_triggered);
                PROCESS_EXIT();
            }
            
            etimer_reset(&timer);
        }
    }
    
    PROCESS_END();
}
