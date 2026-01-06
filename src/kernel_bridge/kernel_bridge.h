/*
 * Kernel Bridge: Windows-Linux Hybrid Communication Layer
 * 
 * This bridges Windows driver calls to Linux kernel operations,
 * using the AI buffer for intelligent request handling.
 */

#ifndef KERNEL_BRIDGE_H
#define KERNEL_BRIDGE_H

#include <stdint.h>
#include <stdbool.h>
#include "../ai_buffer/ai_buffer.h"

/* Bridge operation modes */
typedef enum {
    BRIDGE_MODE_PASSTHROUGH,    /* Direct pass-through, no AI */
    BRIDGE_MODE_AI_ASSISTED,    /* AI suggests, human confirms */
    BRIDGE_MODE_AI_AUTONOMOUS,  /* AI handles everything */
    BRIDGE_MODE_LEARNING        /* AI learns from operations */
} bridge_mode_t;

/* Chipset types we support */
typedef enum {
    CHIPSET_INTEL,
    CHIPSET_AMD,
    CHIPSET_NVIDIA,
    CHIPSET_QUALCOMM,
    CHIPSET_UNKNOWN
} chipset_type_t;

/* Bridge configuration */
typedef struct {
    bridge_mode_t mode;
    bool ai_enabled;
    uint32_t max_pending_requests;
    uint32_t batch_timeout_ms;
    chipset_type_t chipset_type;
} bridge_config_t;

/* Bridge statistics */
typedef struct {
    uint64_t total_requests;
    uint64_t windows_to_linux;
    uint64_t linux_to_windows;
    uint64_t ai_optimized;
    uint64_t ai_batched;
    uint64_t failures;
    uint32_t avg_latency_us;
    float ai_accuracy;
} bridge_stats_t;

/* Device context for chipset drivers */
typedef struct {
    uint32_t device_id;
    chipset_type_t chipset_type;
    void *windows_device_object;
    void *linux_device_handle;
    bool ai_managed;
    uint32_t active_requests;
} device_context_t;

/* API Functions */

/**
 * bridge_init - Initialize the kernel bridge
 * @config: Bridge configuration
 * 
 * Returns: 0 on success, negative on error
 */
int bridge_init(const bridge_config_t *config);

/**
 * bridge_shutdown - Shutdown kernel bridge
 */
void bridge_shutdown(void);

/**
 * bridge_register_device - Register a chipset device
 * @device_id: Device identifier
 * @chipset_type: Type of chipset
 * @windows_device: Windows DEVICE_OBJECT pointer
 * @linux_device: Linux device handle
 * 
 * Returns: Device context pointer on success, NULL on error
 */
device_context_t* bridge_register_device(uint32_t device_id,
                                         chipset_type_t chipset_type,
                                         void *windows_device,
                                         void *linux_device);

/**
 * bridge_unregister_device - Unregister a device
 * @ctx: Device context
 */
void bridge_unregister_device(device_context_t *ctx);

/**
 * bridge_forward_request - Forward request from Windows to Linux
 * @ctx: Device context
 * @request: Request to forward
 * 
 * Returns: 0 on success, negative on error
 */
int bridge_forward_request(device_context_t *ctx, const comm_request_t *request);

/**
 * bridge_send_response - Send response from Linux to Windows
 * @ctx: Device context
 * @data: Response data
 * @size: Response size
 * 
 * Returns: 0 on success, negative on error
 */
int bridge_send_response(device_context_t *ctx, const uint8_t *data, uint32_t size);

/**
 * bridge_get_stats - Get bridge statistics
 * @stats: Output statistics structure
 */
void bridge_get_stats(bridge_stats_t *stats);

/**
 * bridge_set_mode - Change bridge operation mode
 * @mode: New mode
 * 
 * Returns: 0 on success, negative on error
 */
int bridge_set_mode(bridge_mode_t mode);

/* Chipset-specific operations */

/**
 * bridge_chipset_init - Initialize chipset-specific handling
 * @chipset_type: Type of chipset
 * 
 * Returns: 0 on success, negative on error
 */
int bridge_chipset_init(chipset_type_t chipset_type);

/**
 * bridge_chipset_configure - Configure chipset parameters
 * @ctx: Device context
 * @param: Parameter name
 * @value: Parameter value
 * 
 * Returns: 0 on success, negative on error
 */
int bridge_chipset_configure(device_context_t *ctx, const char *param, uint32_t value);

/**
 * bridge_chipset_power_state - Set chipset power state
 * @ctx: Device context
 * @state: Power state (0=D0, 3=D3)
 * 
 * Returns: 0 on success, negative on error
 */
int bridge_chipset_power_state(device_context_t *ctx, uint32_t state);

/* Error codes */
#define BRIDGE_SUCCESS          0
#define BRIDGE_ERR_NOT_INIT     -1
#define BRIDGE_ERR_INVALID_ARG  -2
#define BRIDGE_ERR_NO_MEMORY    -3
#define BRIDGE_ERR_DEVICE       -4
#define BRIDGE_ERR_TIMEOUT      -5
#define BRIDGE_ERR_AI_FAILURE   -6

#endif /* KERNEL_BRIDGE_H */
