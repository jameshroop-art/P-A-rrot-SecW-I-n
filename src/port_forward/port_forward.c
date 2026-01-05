/*
 * Port Forwarding Manager Implementation
 * 
 * Core implementation of the port forwarding subsystem for ParrotWinKernel.
 * Handles rule management, packet forwarding, NAT/PAT, and driver integration.
 */

#include "port_forward.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <pthread.h>
#include <time.h>
#include <errno.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>

/* Internal structures */
typedef struct pf_context {
    pf_config_t config;
    pf_rule_t *rules[PF_MAX_RULES];
    uint32_t rule_count;
    uint32_t next_rule_id;
    pf_stats_t stats;
    pthread_mutex_t lock;
    bool initialized;
    
    /* Callbacks */
    pf_packet_callback_t packet_callback;
    void *packet_ctx;
    pf_event_callback_t event_callback;
    void *event_ctx;
    
    /* Driver registry */
    struct {
        uint32_t driver_id;
        void *driver_ctx;
        bool active;
    } drivers[256];
    uint32_t driver_count;
} pf_context_t;

/* Global context */
static pf_context_t g_pf_ctx = {0};

/* Helper functions */
static inline uint64_t get_timestamp(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + ts.tv_nsec;
}

static pf_rule_t* find_rule_by_id(uint32_t rule_id) {
    for (uint32_t i = 0; i < g_pf_ctx.rule_count; i++) {
        if (g_pf_ctx.rules[i] && g_pf_ctx.rules[i]->id == rule_id) {
            return g_pf_ctx.rules[i];
        }
    }
    return NULL;
}

static int find_rule_index(uint32_t rule_id) {
    for (uint32_t i = 0; i < g_pf_ctx.rule_count; i++) {
        if (g_pf_ctx.rules[i] && g_pf_ctx.rules[i]->id == rule_id) {
            return i;
        }
    }
    return -1;
}

static void fire_event(uint32_t rule_id, const char *event) {
    if (g_pf_ctx.event_callback) {
        g_pf_ctx.event_callback(g_pf_ctx.event_ctx, rule_id, event);
    }
}

/* Core API Implementation */

int pf_init(const pf_config_t *config) {
    if (g_pf_ctx.initialized) {
        return PF_ERR_EXISTS;
    }
    
    if (!config) {
        return PF_ERR_INVALID;
    }
    
    memset(&g_pf_ctx, 0, sizeof(g_pf_ctx));
    memcpy(&g_pf_ctx.config, config, sizeof(pf_config_t));
    
    if (pthread_mutex_init(&g_pf_ctx.lock, NULL) != 0) {
        return PF_ERR_INVALID;
    }
    
    g_pf_ctx.next_rule_id = 1;
    g_pf_ctx.initialized = true;
    
    return PF_SUCCESS;
}

void pf_shutdown(void) {
    if (!g_pf_ctx.initialized) {
        return;
    }
    
    pthread_mutex_lock(&g_pf_ctx.lock);
    
    /* Free all rules */
    for (uint32_t i = 0; i < g_pf_ctx.rule_count; i++) {
        if (g_pf_ctx.rules[i]) {
            free(g_pf_ctx.rules[i]);
            g_pf_ctx.rules[i] = NULL;
        }
    }
    
    g_pf_ctx.rule_count = 0;
    g_pf_ctx.initialized = false;
    
    pthread_mutex_unlock(&g_pf_ctx.lock);
    pthread_mutex_destroy(&g_pf_ctx.lock);
}

int pf_add_rule(const pf_rule_t *rule) {
    if (!g_pf_ctx.initialized) {
        return PF_ERR_DISABLED;
    }
    
    if (!rule) {
        return PF_ERR_INVALID;
    }
    
    pthread_mutex_lock(&g_pf_ctx.lock);
    
    if (g_pf_ctx.rule_count >= g_pf_ctx.config.max_rules) {
        pthread_mutex_unlock(&g_pf_ctx.lock);
        return PF_ERR_LIMIT;
    }
    
    /* Allocate new rule */
    pf_rule_t *new_rule = (pf_rule_t*)malloc(sizeof(pf_rule_t));
    if (!new_rule) {
        pthread_mutex_unlock(&g_pf_ctx.lock);
        return PF_ERR_NO_MEM;
    }
    
    /* Copy rule and assign ID */
    memcpy(new_rule, rule, sizeof(pf_rule_t));
    new_rule->id = g_pf_ctx.next_rule_id++;
    new_rule->packets_forwarded = 0;
    new_rule->bytes_forwarded = 0;
    new_rule->last_activity = 0;
    
    /* Add to rules array */
    g_pf_ctx.rules[g_pf_ctx.rule_count++] = new_rule;
    g_pf_ctx.stats.total_rules++;
    
    uint32_t rule_id = new_rule->id;
    
    pthread_mutex_unlock(&g_pf_ctx.lock);
    
    fire_event(rule_id, "rule_added");
    
    return rule_id;
}

int pf_remove_rule(uint32_t rule_id) {
    if (!g_pf_ctx.initialized) {
        return PF_ERR_DISABLED;
    }
    
    pthread_mutex_lock(&g_pf_ctx.lock);
    
    int idx = find_rule_index(rule_id);
    if (idx < 0) {
        pthread_mutex_unlock(&g_pf_ctx.lock);
        return PF_ERR_NOT_FOUND;
    }
    
    /* Free rule */
    free(g_pf_ctx.rules[idx]);
    
    /* Shift remaining rules */
    for (uint32_t i = idx; i < g_pf_ctx.rule_count - 1; i++) {
        g_pf_ctx.rules[i] = g_pf_ctx.rules[i + 1];
    }
    
    g_pf_ctx.rules[--g_pf_ctx.rule_count] = NULL;
    g_pf_ctx.stats.total_rules--;
    
    pthread_mutex_unlock(&g_pf_ctx.lock);
    
    fire_event(rule_id, "rule_removed");
    
    return PF_SUCCESS;
}

int pf_update_rule(uint32_t rule_id, const pf_rule_t *rule) {
    if (!g_pf_ctx.initialized) {
        return PF_ERR_DISABLED;
    }
    
    if (!rule) {
        return PF_ERR_INVALID;
    }
    
    pthread_mutex_lock(&g_pf_ctx.lock);
    
    pf_rule_t *existing = find_rule_by_id(rule_id);
    if (!existing) {
        pthread_mutex_unlock(&g_pf_ctx.lock);
        return PF_ERR_NOT_FOUND;
    }
    
    /* Preserve statistics */
    uint64_t packets = existing->packets_forwarded;
    uint64_t bytes = existing->bytes_forwarded;
    uint64_t activity = existing->last_activity;
    
    /* Update rule */
    memcpy(existing, rule, sizeof(pf_rule_t));
    existing->id = rule_id;
    existing->packets_forwarded = packets;
    existing->bytes_forwarded = bytes;
    existing->last_activity = activity;
    
    pthread_mutex_unlock(&g_pf_ctx.lock);
    
    fire_event(rule_id, "rule_updated");
    
    return PF_SUCCESS;
}

int pf_get_rule(uint32_t rule_id, pf_rule_t *rule) {
    if (!g_pf_ctx.initialized) {
        return PF_ERR_DISABLED;
    }
    
    if (!rule) {
        return PF_ERR_INVALID;
    }
    
    pthread_mutex_lock(&g_pf_ctx.lock);
    
    pf_rule_t *existing = find_rule_by_id(rule_id);
    if (!existing) {
        pthread_mutex_unlock(&g_pf_ctx.lock);
        return PF_ERR_NOT_FOUND;
    }
    
    memcpy(rule, existing, sizeof(pf_rule_t));
    
    pthread_mutex_unlock(&g_pf_ctx.lock);
    
    return PF_SUCCESS;
}

int pf_list_rules(pf_rule_t *rules, uint32_t max_rules, uint32_t *count) {
    if (!g_pf_ctx.initialized) {
        return PF_ERR_DISABLED;
    }
    
    if (!rules || !count) {
        return PF_ERR_INVALID;
    }
    
    pthread_mutex_lock(&g_pf_ctx.lock);
    
    uint32_t n = g_pf_ctx.rule_count < max_rules ? g_pf_ctx.rule_count : max_rules;
    
    for (uint32_t i = 0; i < n; i++) {
        memcpy(&rules[i], g_pf_ctx.rules[i], sizeof(pf_rule_t));
    }
    
    *count = n;
    
    pthread_mutex_unlock(&g_pf_ctx.lock);
    
    return PF_SUCCESS;
}

int pf_enable_rule(uint32_t rule_id) {
    if (!g_pf_ctx.initialized) {
        return PF_ERR_DISABLED;
    }
    
    pthread_mutex_lock(&g_pf_ctx.lock);
    
    pf_rule_t *rule = find_rule_by_id(rule_id);
    if (!rule) {
        pthread_mutex_unlock(&g_pf_ctx.lock);
        return PF_ERR_NOT_FOUND;
    }
    
    rule->flags |= PF_FLAG_ENABLED;
    
    pthread_mutex_unlock(&g_pf_ctx.lock);
    
    fire_event(rule_id, "rule_enabled");
    
    return PF_SUCCESS;
}

int pf_disable_rule(uint32_t rule_id) {
    if (!g_pf_ctx.initialized) {
        return PF_ERR_DISABLED;
    }
    
    pthread_mutex_lock(&g_pf_ctx.lock);
    
    pf_rule_t *rule = find_rule_by_id(rule_id);
    if (!rule) {
        pthread_mutex_unlock(&g_pf_ctx.lock);
        return PF_ERR_NOT_FOUND;
    }
    
    rule->flags &= ~PF_FLAG_ENABLED;
    
    pthread_mutex_unlock(&g_pf_ctx.lock);
    
    fire_event(rule_id, "rule_disabled");
    
    return PF_SUCCESS;
}

int pf_get_stats(pf_stats_t *stats) {
    if (!g_pf_ctx.initialized) {
        return PF_ERR_DISABLED;
    }
    
    if (!stats) {
        return PF_ERR_INVALID;
    }
    
    pthread_mutex_lock(&g_pf_ctx.lock);
    memcpy(stats, &g_pf_ctx.stats, sizeof(pf_stats_t));
    pthread_mutex_unlock(&g_pf_ctx.lock);
    
    return PF_SUCCESS;
}

int pf_reset_stats(void) {
    if (!g_pf_ctx.initialized) {
        return PF_ERR_DISABLED;
    }
    
    pthread_mutex_lock(&g_pf_ctx.lock);
    
    memset(&g_pf_ctx.stats, 0, sizeof(pf_stats_t));
    g_pf_ctx.stats.total_rules = g_pf_ctx.rule_count;
    
    /* Reset per-rule stats */
    for (uint32_t i = 0; i < g_pf_ctx.rule_count; i++) {
        if (g_pf_ctx.rules[i]) {
            g_pf_ctx.rules[i]->packets_forwarded = 0;
            g_pf_ctx.rules[i]->bytes_forwarded = 0;
            g_pf_ctx.rules[i]->last_activity = 0;
        }
    }
    
    pthread_mutex_unlock(&g_pf_ctx.lock);
    
    return PF_SUCCESS;
}

int pf_register_packet_callback(pf_packet_callback_t callback, void *ctx) {
    if (!g_pf_ctx.initialized) {
        return PF_ERR_DISABLED;
    }
    
    pthread_mutex_lock(&g_pf_ctx.lock);
    g_pf_ctx.packet_callback = callback;
    g_pf_ctx.packet_ctx = ctx;
    pthread_mutex_unlock(&g_pf_ctx.lock);
    
    return PF_SUCCESS;
}

int pf_register_event_callback(pf_event_callback_t callback, void *ctx) {
    if (!g_pf_ctx.initialized) {
        return PF_ERR_DISABLED;
    }
    
    pthread_mutex_lock(&g_pf_ctx.lock);
    g_pf_ctx.event_callback = callback;
    g_pf_ctx.event_ctx = ctx;
    pthread_mutex_unlock(&g_pf_ctx.lock);
    
    return PF_SUCCESS;
}

/* NAT/PAT Implementation */

int pf_nat_translate(const char *src_addr, char *dst_addr) {
    if (!g_pf_ctx.initialized || !g_pf_ctx.config.nat_enabled) {
        return PF_ERR_DISABLED;
    }
    
    if (!src_addr || !dst_addr) {
        return PF_ERR_INVALID;
    }
    
    /* Simple NAT translation - in production this would use iptables/nftables */
    pthread_mutex_lock(&g_pf_ctx.lock);
    
    /* Find matching rule */
    for (uint32_t i = 0; i < g_pf_ctx.rule_count; i++) {
        pf_rule_t *rule = g_pf_ctx.rules[i];
        if (rule && (rule->flags & PF_FLAG_ENABLED) && (rule->flags & PF_FLAG_NAT)) {
            if (strcmp(rule->src_addr, src_addr) == 0 || strcmp(rule->src_addr, "0.0.0.0") == 0) {
                strncpy(dst_addr, rule->dst_addr, PF_MAX_ADDR_LEN - 1);
                dst_addr[PF_MAX_ADDR_LEN - 1] = '\0';
                pthread_mutex_unlock(&g_pf_ctx.lock);
                return PF_SUCCESS;
            }
        }
    }
    
    pthread_mutex_unlock(&g_pf_ctx.lock);
    return PF_ERR_NOT_FOUND;
}

int pf_pat_translate(uint16_t src_port, uint16_t *dst_port) {
    if (!g_pf_ctx.initialized || !g_pf_ctx.config.pat_enabled) {
        return PF_ERR_DISABLED;
    }
    
    if (!dst_port) {
        return PF_ERR_INVALID;
    }
    
    pthread_mutex_lock(&g_pf_ctx.lock);
    
    /* Find matching rule */
    for (uint32_t i = 0; i < g_pf_ctx.rule_count; i++) {
        pf_rule_t *rule = g_pf_ctx.rules[i];
        if (rule && (rule->flags & PF_FLAG_ENABLED) && (rule->flags & PF_FLAG_PAT)) {
            if (rule->src_port == src_port || rule->src_port == 0) {
                *dst_port = rule->dst_port;
                pthread_mutex_unlock(&g_pf_ctx.lock);
                return PF_SUCCESS;
            }
        }
    }
    
    pthread_mutex_unlock(&g_pf_ctx.lock);
    return PF_ERR_NOT_FOUND;
}

/* UPnP/NAT-PMP Implementation */

int pf_upnp_add_mapping(uint16_t external_port, uint16_t internal_port,
                        pf_protocol_t protocol, uint32_t duration) {
    if (!g_pf_ctx.initialized || !g_pf_ctx.config.upnp_enabled) {
        return PF_ERR_DISABLED;
    }
    
    /* Create a rule for UPnP mapping */
    pf_rule_t rule = {0};
    snprintf(rule.name, PF_MAX_NAME_LEN, "upnp_%u_%u", external_port, internal_port);
    strncpy(rule.src_addr, "0.0.0.0", PF_MAX_ADDR_LEN);
    rule.src_port = external_port;
    strncpy(rule.dst_addr, "127.0.0.1", PF_MAX_ADDR_LEN);
    rule.dst_port = internal_port;
    rule.protocol = protocol;
    rule.flags = PF_FLAG_ENABLED | PF_FLAG_UPNP;
    
    if (duration == 0) {
        rule.flags |= PF_FLAG_PERSISTENT;
    }
    
    return pf_add_rule(&rule);
}

int pf_upnp_remove_mapping(uint16_t external_port, pf_protocol_t protocol) {
    if (!g_pf_ctx.initialized || !g_pf_ctx.config.upnp_enabled) {
        return PF_ERR_DISABLED;
    }
    
    pthread_mutex_lock(&g_pf_ctx.lock);
    
    /* Find and remove UPnP mapping */
    for (uint32_t i = 0; i < g_pf_ctx.rule_count; i++) {
        pf_rule_t *rule = g_pf_ctx.rules[i];
        if (rule && (rule->flags & PF_FLAG_UPNP) && 
            rule->src_port == external_port && rule->protocol == protocol) {
            uint32_t rule_id = rule->id;
            pthread_mutex_unlock(&g_pf_ctx.lock);
            return pf_remove_rule(rule_id);
        }
    }
    
    pthread_mutex_unlock(&g_pf_ctx.lock);
    return PF_ERR_NOT_FOUND;
}

/* Driver Integration */

int pf_driver_register(uint32_t driver_id, void *driver_ctx) {
    if (!g_pf_ctx.initialized) {
        return PF_ERR_DISABLED;
    }
    
    pthread_mutex_lock(&g_pf_ctx.lock);
    
    /* Find free slot */
    for (uint32_t i = 0; i < 256; i++) {
        if (!g_pf_ctx.drivers[i].active) {
            g_pf_ctx.drivers[i].driver_id = driver_id;
            g_pf_ctx.drivers[i].driver_ctx = driver_ctx;
            g_pf_ctx.drivers[i].active = true;
            g_pf_ctx.driver_count++;
            pthread_mutex_unlock(&g_pf_ctx.lock);
            return PF_SUCCESS;
        }
    }
    
    pthread_mutex_unlock(&g_pf_ctx.lock);
    return PF_ERR_LIMIT;
}

int pf_driver_unregister(uint32_t driver_id) {
    if (!g_pf_ctx.initialized) {
        return PF_ERR_DISABLED;
    }
    
    pthread_mutex_lock(&g_pf_ctx.lock);
    
    for (uint32_t i = 0; i < 256; i++) {
        if (g_pf_ctx.drivers[i].active && g_pf_ctx.drivers[i].driver_id == driver_id) {
            g_pf_ctx.drivers[i].active = false;
            g_pf_ctx.drivers[i].driver_id = 0;
            g_pf_ctx.drivers[i].driver_ctx = NULL;
            g_pf_ctx.driver_count--;
            pthread_mutex_unlock(&g_pf_ctx.lock);
            return PF_SUCCESS;
        }
    }
    
    pthread_mutex_unlock(&g_pf_ctx.lock);
    return PF_ERR_NOT_FOUND;
}

int pf_driver_forward_packet(uint32_t driver_id, const uint8_t *packet, size_t len) {
    if (!g_pf_ctx.initialized) {
        return PF_ERR_DISABLED;
    }
    
    if (!packet || len == 0) {
        return PF_ERR_INVALID;
    }
    
    pthread_mutex_lock(&g_pf_ctx.lock);
    
    /* Verify driver is registered */
    bool found = false;
    for (uint32_t i = 0; i < 256; i++) {
        if (g_pf_ctx.drivers[i].active && g_pf_ctx.drivers[i].driver_id == driver_id) {
            found = true;
            break;
        }
    }
    
    if (!found) {
        pthread_mutex_unlock(&g_pf_ctx.lock);
        return PF_ERR_NOT_FOUND;
    }
    
    /* Update statistics */
    g_pf_ctx.stats.total_packets++;
    g_pf_ctx.stats.total_bytes += len;
    
    /* Call packet callback if registered */
    if (g_pf_ctx.packet_callback) {
        int ret = g_pf_ctx.packet_callback(g_pf_ctx.packet_ctx, packet, len);
        if (ret != 0) {
            g_pf_ctx.stats.dropped_packets++;
            pthread_mutex_unlock(&g_pf_ctx.lock);
            return ret;
        }
    }
    
    pthread_mutex_unlock(&g_pf_ctx.lock);
    
    return PF_SUCCESS;
}
