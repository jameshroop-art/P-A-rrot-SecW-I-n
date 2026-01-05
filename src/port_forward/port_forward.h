/*
 * Port Forwarding Manager for ParrotWinKernel
 * 
 * This module provides port forwarding capabilities for Windows drivers
 * running on the compatibility layer, enabling network traffic redirection
 * and NAT/PAT support.
 */

#ifndef _PORT_FORWARD_H
#define _PORT_FORWARD_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Port forwarding protocol types */
typedef enum {
    PF_PROTO_TCP = 6,
    PF_PROTO_UDP = 17,
    PF_PROTO_SCTP = 132,
    PF_PROTO_ANY = 0
} pf_protocol_t;

/* Port forwarding rule flags */
#define PF_FLAG_ENABLED     0x0001
#define PF_FLAG_PERSISTENT  0x0002
#define PF_FLAG_NAT         0x0004
#define PF_FLAG_PAT         0x0008
#define PF_FLAG_UPNP        0x0010
#define PF_FLAG_BIDIRECTIONAL 0x0020

/* Maximum limits */
#define PF_MAX_RULES        1024
#define PF_MAX_NAME_LEN     64
#define PF_MAX_ADDR_LEN     46  /* IPv6 address string length */

/* Port forwarding rule structure */
typedef struct pf_rule {
    uint32_t id;                        /* Unique rule ID */
    char name[PF_MAX_NAME_LEN];         /* Rule name */
    
    /* Source configuration */
    char src_addr[PF_MAX_ADDR_LEN];     /* Source IP address (0.0.0.0 = any) */
    uint16_t src_port;                   /* Source port */
    
    /* Destination configuration */
    char dst_addr[PF_MAX_ADDR_LEN];     /* Destination IP address */
    uint16_t dst_port;                   /* Destination port */
    
    /* Protocol and flags */
    pf_protocol_t protocol;              /* Protocol (TCP/UDP/ANY) */
    uint32_t flags;                      /* Rule flags */
    
    /* Statistics */
    uint64_t packets_forwarded;          /* Total packets forwarded */
    uint64_t bytes_forwarded;            /* Total bytes forwarded */
    uint64_t last_activity;              /* Timestamp of last activity */
    
    /* Driver association */
    void *driver_context;                /* Associated Windows driver context */
    uint32_t driver_id;                  /* Driver ID */
} pf_rule_t;

/* Port forwarding configuration */
typedef struct pf_config {
    bool nat_enabled;                    /* NAT enabled */
    bool pat_enabled;                    /* PAT (Port Address Translation) enabled */
    bool upnp_enabled;                   /* UPnP enabled */
    bool natp_enabled;                   /* NAT-PMP enabled */
    uint16_t upnp_port;                  /* UPnP discovery port */
    uint32_t timeout_tcp;                /* TCP connection timeout (seconds) */
    uint32_t timeout_udp;                /* UDP connection timeout (seconds) */
    uint32_t max_rules;                  /* Maximum number of rules */
} pf_config_t;

/* Port forwarding statistics */
typedef struct pf_stats {
    uint64_t total_rules;                /* Total active rules */
    uint64_t total_packets;              /* Total packets forwarded */
    uint64_t total_bytes;                /* Total bytes forwarded */
    uint64_t dropped_packets;            /* Dropped packets */
    uint64_t errors;                     /* Total errors */
} pf_stats_t;

/* Callback function types */
typedef int (*pf_packet_callback_t)(void *ctx, const uint8_t *packet, size_t len);
typedef void (*pf_event_callback_t)(void *ctx, uint32_t rule_id, const char *event);

/* Core API functions */

/**
 * pf_init - Initialize port forwarding subsystem
 * @config: Configuration parameters
 * 
 * Returns: 0 on success, negative error code on failure
 */
int pf_init(const pf_config_t *config);

/**
 * pf_shutdown - Shutdown port forwarding subsystem
 */
void pf_shutdown(void);

/**
 * pf_add_rule - Add a port forwarding rule
 * @rule: Rule to add
 * 
 * Returns: Rule ID on success, negative error code on failure
 */
int pf_add_rule(const pf_rule_t *rule);

/**
 * pf_remove_rule - Remove a port forwarding rule
 * @rule_id: Rule ID to remove
 * 
 * Returns: 0 on success, negative error code on failure
 */
int pf_remove_rule(uint32_t rule_id);

/**
 * pf_update_rule - Update an existing rule
 * @rule_id: Rule ID to update
 * @rule: New rule configuration
 * 
 * Returns: 0 on success, negative error code on failure
 */
int pf_update_rule(uint32_t rule_id, const pf_rule_t *rule);

/**
 * pf_get_rule - Get rule by ID
 * @rule_id: Rule ID
 * @rule: Output buffer for rule
 * 
 * Returns: 0 on success, negative error code on failure
 */
int pf_get_rule(uint32_t rule_id, pf_rule_t *rule);

/**
 * pf_list_rules - List all active rules
 * @rules: Output buffer for rules
 * @max_rules: Maximum number of rules to return
 * @count: Output parameter for actual number of rules
 * 
 * Returns: 0 on success, negative error code on failure
 */
int pf_list_rules(pf_rule_t *rules, uint32_t max_rules, uint32_t *count);

/**
 * pf_enable_rule - Enable a rule
 * @rule_id: Rule ID to enable
 * 
 * Returns: 0 on success, negative error code on failure
 */
int pf_enable_rule(uint32_t rule_id);

/**
 * pf_disable_rule - Disable a rule
 * @rule_id: Rule ID to disable
 * 
 * Returns: 0 on success, negative error code on failure
 */
int pf_disable_rule(uint32_t rule_id);

/**
 * pf_get_stats - Get port forwarding statistics
 * @stats: Output buffer for statistics
 * 
 * Returns: 0 on success, negative error code on failure
 */
int pf_get_stats(pf_stats_t *stats);

/**
 * pf_reset_stats - Reset statistics counters
 * 
 * Returns: 0 on success, negative error code on failure
 */
int pf_reset_stats(void);

/**
 * pf_register_packet_callback - Register packet callback
 * @callback: Callback function
 * @ctx: User context
 * 
 * Returns: 0 on success, negative error code on failure
 */
int pf_register_packet_callback(pf_packet_callback_t callback, void *ctx);

/**
 * pf_register_event_callback - Register event callback
 * @callback: Callback function
 * @ctx: User context
 * 
 * Returns: 0 on success, negative error code on failure
 */
int pf_register_event_callback(pf_event_callback_t callback, void *ctx);

/* NAT/PAT specific functions */

/**
 * pf_nat_translate - Translate address using NAT
 * @src_addr: Source address
 * @dst_addr: Destination address (output)
 * 
 * Returns: 0 on success, negative error code on failure
 */
int pf_nat_translate(const char *src_addr, char *dst_addr);

/**
 * pf_pat_translate - Translate port using PAT
 * @src_port: Source port
 * @dst_port: Destination port (output)
 * 
 * Returns: 0 on success, negative error code on failure
 */
int pf_pat_translate(uint16_t src_port, uint16_t *dst_port);

/* UPnP/NAT-PMP functions */

/**
 * pf_upnp_add_mapping - Add UPnP port mapping
 * @external_port: External port
 * @internal_port: Internal port
 * @protocol: Protocol (TCP/UDP)
 * @duration: Lease duration in seconds (0 = permanent)
 * 
 * Returns: 0 on success, negative error code on failure
 */
int pf_upnp_add_mapping(uint16_t external_port, uint16_t internal_port,
                        pf_protocol_t protocol, uint32_t duration);

/**
 * pf_upnp_remove_mapping - Remove UPnP port mapping
 * @external_port: External port
 * @protocol: Protocol
 * 
 * Returns: 0 on success, negative error code on failure
 */
int pf_upnp_remove_mapping(uint16_t external_port, pf_protocol_t protocol);

/* Driver integration functions */

/**
 * pf_driver_register - Register a Windows driver with port forwarding
 * @driver_id: Driver ID
 * @driver_ctx: Driver context
 * 
 * Returns: 0 on success, negative error code on failure
 */
int pf_driver_register(uint32_t driver_id, void *driver_ctx);

/**
 * pf_driver_unregister - Unregister a Windows driver
 * @driver_id: Driver ID
 * 
 * Returns: 0 on success, negative error code on failure
 */
int pf_driver_unregister(uint32_t driver_id);

/**
 * pf_driver_forward_packet - Forward packet from Windows driver
 * @driver_id: Driver ID
 * @packet: Packet data
 * @len: Packet length
 * 
 * Returns: 0 on success, negative error code on failure
 */
int pf_driver_forward_packet(uint32_t driver_id, const uint8_t *packet, size_t len);

/* Error codes */
#define PF_SUCCESS          0
#define PF_ERR_INVALID      -1
#define PF_ERR_NO_MEM       -2
#define PF_ERR_NOT_FOUND    -3
#define PF_ERR_EXISTS       -4
#define PF_ERR_LIMIT        -5
#define PF_ERR_DISABLED     -6
#define PF_ERR_PERMISSION   -7
#define PF_ERR_NETWORK      -8

#endif /* _PORT_FORWARD_H */
