# USB Device Loader - Proof of Concept

## Overview
This is a minimal proof-of-concept demonstrating how to load a Windows USB device driver on Linux.

## What It Does
1. Loads a Windows .sys driver file
2. Provides minimal Windows kernel API stubs (IoCreateDevice, ExAllocatePool, etc.)
3. Calls the driver's DriverEntry function
4. Simulates device enumeration

## Building

```bash
gcc -o usb_driver_loader usb_driver_loader.c -ldl -pthread
```

## Running

```bash
./usb_driver_loader <path_to_driver.so>
```

**Note**: For this PoC, the driver must be in .so (ELF) format. A real implementation would parse PE/COFF (.sys) format.

## Expected Output

```
╔════════════════════════════════════════════════════╗
║  Windows USB Driver Loader - Proof of Concept     ║
║  ParrotWinKernel Project                          ║
╚════════════════════════════════════════════════════╝

=== Loading PE Driver ===
Path: /path/to/driver.so
Driver loaded successfully!

=== Calling DriverEntry ===
Driver Object: 0x...
Calling DriverEntry function at 0x...
[STUB] IoCreateDevice called
       DeviceExtensionSize: 256
       DeviceType: 0x22
[STUB] IoRegisterDeviceInterface called
DriverEntry returned: 0x00000000 (SUCCESS)

=== Simulating Device Events ===
Simulating USB device plug...
Device enumeration complete.
Devices managed: 1

=== Driver Running ===
Press Ctrl+C to exit
In production, this would run as a daemon...

=== Cleanup ===
Unloading driver...
Cleanup complete.

╔════════════════════════════════════════════════════╗
║  Proof of Concept Complete                        ║
╚════════════════════════════════════════════════════╝
```

## Limitations

This is a **proof of concept** with significant limitations:

1. **No PE Parsing**: Expects .so files, not real .sys files
2. **Stub APIs Only**: Windows kernel APIs return success without actual functionality
3. **No Device Communication**: Doesn't actually talk to hardware
4. **No Error Handling**: Minimal error checking
5. **No IRP Handling**: Doesn't process I/O requests

## Real Implementation Needs

To make this production-ready:

1. **PE/COFF Parser**: Parse Windows .sys driver format
2. **Complete ntoskrnl APIs**: Implement full Windows kernel API set
3. **Device Bridge**: Connect to actual Linux device nodes
4. **IRP Processing**: Handle I/O request packets
5. **Memory Management**: Proper pool allocation, MDLs
6. **Synchronization**: Locks, events, DPCs
7. **Power Management**: Handle device power states
8. **PnP Support**: Plug and play event handling

## Testing

To test with a real driver, you would need to:

1. Extract a Windows .sys driver
2. Convert it to .so format (or implement PE parser)
3. Ensure all ntoskrnl APIs it uses are stubbed
4. Run this loader
5. Verify DriverEntry is called successfully

## Next Steps

See the main USE_CASES.md document for the full implementation roadmap.
