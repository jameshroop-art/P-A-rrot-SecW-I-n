/*
 * Port Forwarding Test Program
 * 
 * Simple test program to verify port forwarding functionality
 */

#include "port_forward.h"
#include <stdio.h>
#include <string.h>
#include <assert.h>

/* Test callback for packets */
static int test_packet_callback(void *ctx, const uint8_t *packet, size_t len) {
    printf("Packet callback: received %zu bytes\n", len);
    return 0;
}

/* Test callback for events */
static void test_event_callback(void *ctx, uint32_t rule_id, const char *event) {
    printf("Event callback: rule %u - %s\n", rule_id, event);
}

int main(void) {
    int ret;
    pf_config_t config = {0};
    pf_rule_t rule = {0};
    pf_stats_t stats = {0};
    
    printf("Port Forwarding Test Program\n");
    printf("=============================\n\n");
    
    /* Initialize */
    printf("1. Initializing port forwarding subsystem...\n");
    config.nat_enabled = true;
    config.pat_enabled = true;
    config.upnp_enabled = true;
    config.natp_enabled = false;
    config.upnp_port = 1900;
    config.timeout_tcp = 3600;
    config.timeout_udp = 300;
    config.max_rules = 100;
    
    ret = pf_init(&config);
    assert(ret == PF_SUCCESS);
    printf("   ✓ Initialization successful\n\n");
    
    /* Register callbacks */
    printf("2. Registering callbacks...\n");
    pf_register_packet_callback(test_packet_callback, NULL);
    pf_register_event_callback(test_event_callback, NULL);
    printf("   ✓ Callbacks registered\n\n");
    
    /* Add a rule */
    printf("3. Adding port forwarding rule...\n");
    strncpy(rule.name, "Test SSH Forward", PF_MAX_NAME_LEN - 1);
    strncpy(rule.src_addr, "0.0.0.0", PF_MAX_ADDR_LEN - 1);
    rule.src_port = 2222;
    strncpy(rule.dst_addr, "192.168.1.100", PF_MAX_ADDR_LEN - 1);
    rule.dst_port = 22;
    rule.protocol = PF_PROTO_TCP;
    rule.flags = PF_FLAG_ENABLED | PF_FLAG_NAT | PF_FLAG_PAT;
    
    ret = pf_add_rule(&rule);
    assert(ret > 0);
    printf("   ✓ Rule added with ID: %d\n\n", ret);
    
    uint32_t rule_id = ret;
    
    /* Get rule */
    printf("4. Retrieving rule...\n");
    pf_rule_t retrieved_rule = {0};
    ret = pf_get_rule(rule_id, &retrieved_rule);
    assert(ret == PF_SUCCESS);
    printf("   ✓ Rule retrieved: %s (%s:%u -> %s:%u)\n\n",
           retrieved_rule.name,
           retrieved_rule.src_addr, retrieved_rule.src_port,
           retrieved_rule.dst_addr, retrieved_rule.dst_port);
    
    /* List rules */
    printf("5. Listing all rules...\n");
    pf_rule_t rules[10];
    uint32_t count;
    ret = pf_list_rules(rules, 10, &count);
    assert(ret == PF_SUCCESS);
    printf("   ✓ Total rules: %u\n\n", count);
    
    /* Test NAT translation */
    printf("6. Testing NAT translation...\n");
    char translated_addr[PF_MAX_ADDR_LEN];
    ret = pf_nat_translate("0.0.0.0", translated_addr);
    if (ret == PF_SUCCESS) {
        printf("   ✓ NAT translation: 0.0.0.0 -> %s\n\n", translated_addr);
    } else {
        printf("   ⚠ NAT translation not found\n\n");
    }
    
    /* Test PAT translation */
    printf("7. Testing PAT translation...\n");
    uint16_t translated_port;
    ret = pf_pat_translate(2222, &translated_port);
    if (ret == PF_SUCCESS) {
        printf("   ✓ PAT translation: 2222 -> %u\n\n", translated_port);
    } else {
        printf("   ⚠ PAT translation not found\n\n");
    }
    
    /* Test UPnP mapping */
    printf("8. Adding UPnP mapping...\n");
    ret = pf_upnp_add_mapping(8080, 80, PF_PROTO_TCP, 3600);
    assert(ret > 0);
    printf("   ✓ UPnP mapping added with ID: %d\n\n", ret);
    
    /* Register driver */
    printf("9. Registering Windows driver...\n");
    ret = pf_driver_register(1, NULL);
    assert(ret == PF_SUCCESS);
    printf("   ✓ Driver registered\n\n");
    
    /* Forward a packet */
    printf("10. Forwarding test packet...\n");
    uint8_t test_packet[64] = {0};
    memset(test_packet, 0xAB, sizeof(test_packet));
    ret = pf_driver_forward_packet(1, test_packet, sizeof(test_packet));
    assert(ret == PF_SUCCESS);
    printf("   ✓ Packet forwarded\n\n");
    
    /* Get statistics */
    printf("11. Retrieving statistics...\n");
    ret = pf_get_stats(&stats);
    assert(ret == PF_SUCCESS);
    printf("   ✓ Statistics:\n");
    printf("      - Total rules: %lu\n", stats.total_rules);
    printf("      - Total packets: %lu\n", stats.total_packets);
    printf("      - Total bytes: %lu\n", stats.total_bytes);
    printf("      - Dropped packets: %lu\n", stats.dropped_packets);
    printf("      - Errors: %lu\n\n", stats.errors);
    
    /* Disable rule */
    printf("12. Disabling rule...\n");
    ret = pf_disable_rule(rule_id);
    assert(ret == PF_SUCCESS);
    printf("   ✓ Rule disabled\n\n");
    
    /* Enable rule */
    printf("13. Enabling rule...\n");
    ret = pf_enable_rule(rule_id);
    assert(ret == PF_SUCCESS);
    printf("   ✓ Rule enabled\n\n");
    
    /* Unregister driver */
    printf("14. Unregistering driver...\n");
    ret = pf_driver_unregister(1);
    assert(ret == PF_SUCCESS);
    printf("   ✓ Driver unregistered\n\n");
    
    /* Remove rule */
    printf("15. Removing rule...\n");
    ret = pf_remove_rule(rule_id);
    assert(ret == PF_SUCCESS);
    printf("   ✓ Rule removed\n\n");
    
    /* Shutdown */
    printf("16. Shutting down...\n");
    pf_shutdown();
    printf("   ✓ Shutdown complete\n\n");
    
    printf("=============================\n");
    printf("All tests passed! ✓\n");
    
    return 0;
}
