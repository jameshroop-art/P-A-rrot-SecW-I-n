/*
 * ParrotWinKernel - Chipset Driver Manager
 * 
 * Copyright (c) 2026 James H Roop. All Rights Reserved.
 * 
 * EXPRESSION OF CREATIVE WORK:
 * This work embodies the Expression of James H Roop's original plan and theory 
 * of implementation. The creative intellectual property includes the IMPLEMENTATION, 
 * ARCHITECTURE, DESIGN, and SOLUTION as the creative Expression of the plan and 
 * theoretical framework.
 * 
 * NO PROPRIETARY INFORMATION USED: This work contains NO proprietary information 
 * from Microsoft, Linux, Debian, Parrot, or any other entities. Everything is 
 * SIMULATED based on publicly available specifications and original creative 
 * expression. Future development will proceed without proprietary information.
 * 
 * While individual code segments may reference publicly available specifications
 * or reverse-engineered interfaces, the creative expression, methodology,
 * and integrated solution are entirely original and protected works.
 * 
 * This creative property includes but is not limited to:
 * - The AI-assisted communication buffer architecture
 * - The integration methodology between Windows and Linux kernels
 * - The specific implementation of the hybrid driver system
 * - The novel approach to cross-kernel driver compatibility
 * - The design patterns and architectural decisions
 * - The unique combination and integration of technologies
 * 
 * NO OWNERSHIP CLAIM is made over:
 * - Public specifications (Windows API, Linux kernel interfaces)
 * - Standard algorithms or publicly known techniques
 * - Third-party code or libraries used
 * 
 * This file is part of ParrotWinKernel, a Windows driver compatibility
 * layer for Linux with AI-assisted communication buffering.
 * 
 * Permission to use, copy, modify, and distribute this software is
 * granted under the terms specified in the LICENSE file in the root
 * directory of this project.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
 * See LICENSE file for full terms and conditions.
 * 
 * ---
 * 
 * Chipset Driver Manager
 * 
 * Handles Windows chipset drivers and their integration with Linux kernel
 * through the AI-powered bridge.
 */

#ifndef CHIPSET_DRIVER_H
#define CHIPSET_DRIVER_H

#include <stdint.h>
#include <stdbool.h>
#include "../kernel_bridge/kernel_bridge.h"

/* Chipset driver information */
typedef struct {
    char name[64];
    char vendor[64];
    uint32_t vendor_id;
    uint32_t device_id;
    chipset_type_t chipset_type;
    char driver_path[256];
    bool loaded;
    void *driver_handle;
    device_context_t *bridge_context;
} chipset_driver_t;

/* Driver capabilities */
typedef struct {
    bool supports_dma;
    bool supports_msi;
    bool supports_power_management;
    bool supports_pcie;
    uint32_t max_transfer_size;
    uint32_t alignment_requirement;
} driver_capabilities_t;

/* API Functions */

/**
 * chipset_init - Initialize chipset driver subsystem
 * 
 * Returns: 0 on success, negative on error
 */
int chipset_init(void);

/**
 * chipset_shutdown - Shutdown chipset driver subsystem
 */
void chipset_shutdown(void);

/**
 * chipset_detect - Detect installed chipsets
 * @drivers: Output array of detected drivers
 * @max_drivers: Maximum drivers to detect
 * @count: Output count of detected drivers
 * 
 * Returns: 0 on success, negative on error
 */
int chipset_detect(chipset_driver_t *drivers, uint32_t max_drivers, uint32_t *count);

/**
 * chipset_load_driver - Load a chipset driver
 * @driver: Driver to load
 * 
 * Returns: 0 on success, negative on error
 */
int chipset_load_driver(chipset_driver_t *driver);

/**
 * chipset_unload_driver - Unload a chipset driver
 * @driver: Driver to unload
 */
void chipset_unload_driver(chipset_driver_t *driver);

/**
 * chipset_get_capabilities - Get driver capabilities
 * @driver: Driver to query
 * @caps: Output capabilities
 * 
 * Returns: 0 on success, negative on error
 */
int chipset_get_capabilities(const chipset_driver_t *driver, driver_capabilities_t *caps);

/**
 * chipset_configure - Configure chipset parameters
 * @driver: Driver to configure
 * @param: Parameter name
 * @value: Parameter value
 * 
 * Returns: 0 on success, negative on error
 */
int chipset_configure(chipset_driver_t *driver, const char *param, uint32_t value);

/**
 * chipset_read_register - Read chipset register
 * @driver: Driver context
 * @offset: Register offset
 * @value: Output value
 * 
 * Returns: 0 on success, negative on error
 */
int chipset_read_register(chipset_driver_t *driver, uint32_t offset, uint32_t *value);

/**
 * chipset_write_register - Write chipset register
 * @driver: Driver context
 * @offset: Register offset
 * @value: Value to write
 * 
 * Returns: 0 on success, negative on error
 */
int chipset_write_register(chipset_driver_t *driver, uint32_t offset, uint32_t value);

/**
 * chipset_power_management - Control chipset power state
 * @driver: Driver context
 * @state: Power state (0=D0 full power, 3=D3 off)
 * 
 * Returns: 0 on success, negative on error
 */
int chipset_power_management(chipset_driver_t *driver, uint32_t state);

/* Error codes */
#define CHIPSET_SUCCESS          0
#define CHIPSET_ERR_NOT_INIT     -1
#define CHIPSET_ERR_INVALID_ARG  -2
#define CHIPSET_ERR_NO_MEMORY    -3
#define CHIPSET_ERR_NOT_FOUND    -4
#define CHIPSET_ERR_LOAD_FAILED  -5
#define CHIPSET_ERR_IO_ERROR     -6

#endif /* CHIPSET_DRIVER_H */
