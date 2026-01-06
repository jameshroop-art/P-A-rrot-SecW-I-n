/*
 * AI Communication Buffer Implementation
 * 
 * Implements a tiny neural network for intelligent request handling
 * between Windows drivers and Linux kernel.
 */

#include "ai_buffer.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <pthread.h>
#include <time.h>

/* Global AI model state */
static ai_model_t g_model = {0};
static bool g_initialized = false;
static pthread_mutex_t g_lock = PTHREAD_MUTEX_INITIALIZER;

/* Helper: Extract features from request */
static void extract_features(const comm_request_t *req, feature_vector_t *features) {
    memset(features, 0, sizeof(feature_vector_t));
    
    /* Normalize features to 0-1 range */
    features->features[0] = (float)req->type / (float)REQ_UNKNOWN;
    features->features[1] = (float)(req->device_id & 0xFF) / 255.0f;
    features->features[2] = (float)((req->device_id >> 8) & 0xFF) / 255.0f;
    features->features[3] = (float)(req->address & 0xFFFF) / 65535.0f;
    features->features[4] = (float)req->size / 4096.0f; /* Normalize to page size */
    features->features[5] = (float)(req->flags & 0xFF) / 255.0f;
    features->features[6] = (float)req->priority / 10.0f;
    
    /* Time-based features */
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    uint64_t now_ns = ts.tv_sec * 1000000000ULL + ts.tv_nsec;
    uint64_t time_delta = now_ns - req->timestamp;
    features->features[7] = fmin(1.0f, (float)time_delta / 1000000.0f); /* ms */
    
    /* Historical pattern features */
    uint32_t recent_same_type = 0;
    for (int i = 0; i < 100 && i < g_model.history_index; i++) {
        uint32_t idx = (g_model.history_index - 1 - i) % 1000;
        if ((g_model.history[idx].request_pattern & 0xFF) == req->type) {
            recent_same_type++;
        }
    }
    features->features[8] = (float)recent_same_type / 100.0f;
    
    /* Average recent latency */
    uint64_t sum_latency = 0;
    uint32_t count = 0;
    for (int i = 0; i < 100 && i < g_model.history_index; i++) {
        uint32_t idx = (g_model.history_index - 1 - i) % 1000;
        sum_latency += g_model.history[idx].latency_us;
        count++;
    }
    features->features[9] = count > 0 ? (float)sum_latency / (float)count / 10000.0f : 0.5f;
    
    /* Fill remaining features with derived values */
    for (int i = 10; i < AI_INPUT_SIZE; i++) {
        features->features[i] = features->features[i % 10] * 0.5f;
    }
}

/* Helper: ReLU activation */
static inline float relu(float x) {
    return x > 0.0f ? x : 0.0f;
}

/* Helper: Softmax for output layer */
static void softmax(float *values, int size) {
    float max_val = values[0];
    for (int i = 1; i < size; i++) {
        if (values[i] > max_val) max_val = values[i];
    }
    
    float sum = 0.0f;
    for (int i = 0; i < size; i++) {
        values[i] = expf(values[i] - max_val);
        sum += values[i];
    }
    
    for (int i = 0; i < size; i++) {
        values[i] /= sum;
    }
}

/* Helper: Forward pass through neural network */
static void forward_pass(const feature_vector_t *input, float *output) {
    float hidden[AI_HIDDEN_SIZE];
    
    /* Input -> Hidden layer */
    for (int h = 0; h < AI_HIDDEN_SIZE; h++) {
        float sum = g_model.bias_hidden[h] * g_model.scale_hidden;
        for (int i = 0; i < AI_INPUT_SIZE; i++) {
            sum += input->features[i] * 
                   (g_model.weights_input_hidden[i][h] / 127.0f) * 
                   g_model.scale_input;
        }
        hidden[h] = relu(sum);
    }
    
    /* Hidden -> Output layer */
    for (int o = 0; o < AI_OUTPUT_SIZE; o++) {
        float sum = g_model.bias_output[o] * g_model.scale_output;
        for (int h = 0; h < AI_HIDDEN_SIZE; h++) {
            sum += hidden[h] * 
                   (g_model.weights_hidden_output[h][o] / 127.0f) *
                   g_model.scale_hidden;
        }
        output[o] = sum;
    }
    
    /* Apply softmax to get probabilities */
    softmax(output, AI_OUTPUT_SIZE);
}

/* Initialize AI buffer system */
int ai_buffer_init(bool learning_enabled) {
    pthread_mutex_lock(&g_lock);
    
    if (g_initialized) {
        pthread_mutex_unlock(&g_lock);
        return AI_SUCCESS;
    }
    
    /* Initialize model with random weights (Xavier initialization) */
    srand(time(NULL));
    float scale = sqrtf(2.0f / (AI_INPUT_SIZE + AI_HIDDEN_SIZE));
    
    for (int i = 0; i < AI_INPUT_SIZE; i++) {
        for (int h = 0; h < AI_HIDDEN_SIZE; h++) {
            float weight = ((float)rand() / RAND_MAX - 0.5f) * 2.0f * scale;
            g_model.weights_input_hidden[i][h] = (int8_t)(weight * 127.0f);
        }
    }
    
    scale = sqrtf(2.0f / (AI_HIDDEN_SIZE + AI_OUTPUT_SIZE));
    for (int h = 0; h < AI_HIDDEN_SIZE; h++) {
        for (int o = 0; o < AI_OUTPUT_SIZE; o++) {
            float weight = ((float)rand() / RAND_MAX - 0.5f) * 2.0f * scale;
            g_model.weights_hidden_output[h][o] = (int8_t)(weight * 127.0f);
        }
    }
    
    /* Initialize biases to small values */
    for (int h = 0; h < AI_HIDDEN_SIZE; h++) {
        g_model.bias_hidden[h] = (int8_t)((rand() % 20) - 10);
    }
    for (int o = 0; o < AI_OUTPUT_SIZE; o++) {
        g_model.bias_output[o] = (int8_t)((rand() % 20) - 10);
    }
    
    /* Set scaling factors */
    g_model.scale_input = 1.0f;
    g_model.scale_hidden = 1.0f;
    g_model.scale_output = 1.0f;
    
    /* Initialize statistics */
    g_model.requests_processed = 0;
    g_model.successful_predictions = 0;
    g_model.failed_predictions = 0;
    g_model.avg_latency_us = 0;
    g_model.history_index = 0;
    
    /* Configuration */
    g_model.learning_enabled = learning_enabled;
    g_model.learning_rate = 0.01f;
    g_model.batch_size = 10;
    
    g_initialized = true;
    pthread_mutex_unlock(&g_lock);
    
    return AI_SUCCESS;
}

/* Shutdown AI buffer system */
void ai_buffer_shutdown(void) {
    pthread_mutex_lock(&g_lock);
    g_initialized = false;
    memset(&g_model, 0, sizeof(ai_model_t));
    pthread_mutex_unlock(&g_lock);
}

/* Process request through AI */
int ai_buffer_process_request(const comm_request_t *request, ai_prediction_t *prediction) {
    if (!g_initialized) {
        return AI_ERR_NOT_INITIALIZED;
    }
    
    if (!request || !prediction) {
        return AI_ERR_INVALID_ARG;
    }
    
    pthread_mutex_lock(&g_lock);
    
    /* Extract features */
    feature_vector_t features;
    extract_features(request, &features);
    
    /* Run neural network */
    float output[AI_OUTPUT_SIZE];
    forward_pass(&features, output);
    
    /* Interpret output */
    int max_idx = 0;
    float max_prob = output[0];
    for (int i = 1; i < 6; i++) { /* First 6 outputs are decisions */
        if (output[i] > max_prob) {
            max_prob = output[i];
            max_idx = i;
        }
    }
    
    prediction->decision = (ai_decision_t)max_idx;
    prediction->confidence = max_prob;
    
    /* Estimate latency from output */
    prediction->estimated_latency_us = (uint32_t)(output[6] * 10000.0f);
    
    /* Should batch? */
    prediction->should_batch = output[7] > 0.5f;
    prediction->batch_delay_us = prediction->should_batch ? 
                                 (uint32_t)(output[8] * 1000.0f) : 0;
    
    /* Update statistics */
    g_model.requests_processed++;
    
    pthread_mutex_unlock(&g_lock);
    
    return AI_SUCCESS;
}

/* Provide feedback for learning */
void ai_buffer_feedback(const comm_request_t *request,
                        const ai_prediction_t *prediction,
                        uint32_t actual_latency_us,
                        bool success) {
    if (!g_initialized || !g_model.learning_enabled) {
        return;
    }
    
    pthread_mutex_lock(&g_lock);
    
    /* Record in history */
    uint32_t idx = g_model.history_index % 1000;
    g_model.history[idx].request_pattern = (request->type << 24) | 
                                           (request->device_id & 0xFFFFFF);
    g_model.history[idx].decision = prediction->decision;
    g_model.history[idx].latency_us = actual_latency_us;
    g_model.history[idx].success = success;
    g_model.history_index++;
    
    /* Update statistics */
    if (success) {
        g_model.successful_predictions++;
    } else {
        g_model.failed_predictions++;
    }
    
    /* Update average latency (exponential moving average) */
    if (g_model.avg_latency_us == 0) {
        g_model.avg_latency_us = actual_latency_us;
    } else {
        g_model.avg_latency_us = (g_model.avg_latency_us * 9 + actual_latency_us) / 10;
    }
    
    /* TODO: Implement online learning weight updates here */
    /* For now, we just collect statistics */
    
    pthread_mutex_unlock(&g_lock);
}

/* Get statistics */
void ai_buffer_get_stats(uint64_t *requests, float *accuracy, uint32_t *avg_latency) {
    pthread_mutex_lock(&g_lock);
    
    if (requests) *requests = g_model.requests_processed;
    
    if (accuracy) {
        uint64_t total = g_model.successful_predictions + g_model.failed_predictions;
        *accuracy = total > 0 ? 
                    (float)g_model.successful_predictions / (float)total : 0.0f;
    }
    
    if (avg_latency) *avg_latency = g_model.avg_latency_us;
    
    pthread_mutex_unlock(&g_lock);
}

/* Save model to disk */
int ai_buffer_save_model(const char *path) {
    if (!g_initialized || !path) {
        return AI_ERR_INVALID_ARG;
    }
    
    pthread_mutex_lock(&g_lock);
    
    FILE *f = fopen(path, "wb");
    if (!f) {
        pthread_mutex_unlock(&g_lock);
        return AI_ERR_IO_ERROR;
    }
    
    /* Write model structure */
    size_t written = fwrite(&g_model, sizeof(ai_model_t), 1, f);
    fclose(f);
    
    pthread_mutex_unlock(&g_lock);
    
    return written == 1 ? AI_SUCCESS : AI_ERR_IO_ERROR;
}

/* Load model from disk */
int ai_buffer_load_model(const char *path) {
    if (!path) {
        return AI_ERR_INVALID_ARG;
    }
    
    pthread_mutex_lock(&g_lock);
    
    FILE *f = fopen(path, "rb");
    if (!f) {
        pthread_mutex_unlock(&g_lock);
        return AI_ERR_IO_ERROR;
    }
    
    /* Read model structure */
    size_t read = fread(&g_model, sizeof(ai_model_t), 1, f);
    fclose(f);
    
    if (read != 1) {
        pthread_mutex_unlock(&g_lock);
        return AI_ERR_MODEL_CORRUPT;
    }
    
    g_initialized = true;
    
    pthread_mutex_unlock(&g_lock);
    
    return AI_SUCCESS;
}

/* Predict batching strategy */
int ai_buffer_predict_batch(const comm_request_t *requests,
                             uint32_t count,
                             uint32_t *batch_groups,
                             uint32_t *num_groups) {
    if (!g_initialized || !requests || !batch_groups || !num_groups) {
        return AI_ERR_INVALID_ARG;
    }
    
    /* Simple batching: group by request type and device */
    uint32_t group_id = 0;
    *num_groups = 0;
    
    for (uint32_t i = 0; i < count; i++) {
        bool found_group = false;
        
        for (uint32_t j = 0; j < i; j++) {
            if (requests[i].type == requests[j].type &&
                requests[i].device_id == requests[j].device_id) {
                batch_groups[i] = batch_groups[j];
                found_group = true;
                break;
            }
        }
        
        if (!found_group) {
            batch_groups[i] = group_id++;
            (*num_groups)++;
        }
    }
    
    return AI_SUCCESS;
}

/* Optimize request */
int ai_buffer_optimize_request(const comm_request_t *request,
                                comm_request_t *optimized) {
    if (!g_initialized || !request || !optimized) {
        return AI_ERR_INVALID_ARG;
    }
    
    /* Copy request */
    memcpy(optimized, request, sizeof(comm_request_t));
    
    /* Apply optimizations based on request type */
    switch (request->type) {
        case REQ_IO_READ:
        case REQ_IO_WRITE:
            /* Align size to cache line */
            if (optimized->size < 64) {
                optimized->size = 64;
            } else {
                optimized->size = (optimized->size + 63) & ~63;
            }
            break;
            
        case REQ_DMA_ALLOC:
            /* Align to page boundary */
            optimized->size = (optimized->size + 4095) & ~4095;
            break;
            
        default:
            break;
    }
    
    return AI_SUCCESS;
}

/* Predict failure probability */
int ai_buffer_predict_failure(const comm_request_t *request,
                               float *failure_probability) {
    if (!g_initialized || !request || !failure_probability) {
        return AI_ERR_INVALID_ARG;
    }
    
    pthread_mutex_lock(&g_lock);
    
    /* Analyze historical data for similar requests */
    uint32_t failures = 0;
    uint32_t total = 0;
    
    for (uint32_t i = 0; i < g_model.history_index && i < 1000; i++) {
        uint32_t pattern = g_model.history[i].request_pattern;
        uint8_t hist_type = (pattern >> 24) & 0xFF;
        
        if (hist_type == request->type) {
            total++;
            if (!g_model.history[i].success) {
                failures++;
            }
        }
    }
    
    *failure_probability = total > 0 ? (float)failures / (float)total : 0.5f;
    
    pthread_mutex_unlock(&g_lock);
    
    return AI_SUCCESS;
}
