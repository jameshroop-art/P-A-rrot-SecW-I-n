# Makefile for ParrotWinKernel Complete System

CC = gcc
CFLAGS = -Wall -Wextra -O2 -pthread -g
LDFLAGS = -pthread -lm

# Directories
AI_DIR = ai_buffer
BRIDGE_DIR = kernel_bridge
CHIPSET_DIR = chipset_drivers

# Source files
AI_SRC = $(AI_DIR)/ai_buffer.c
BRIDGE_SRC = $(BRIDGE_DIR)/kernel_bridge.c
CHIPSET_SRC = $(CHIPSET_DIR)/chipset_driver.c
DEMO_SRC = demo_main.c

# Object files
AI_OBJ = $(AI_SRC:.c=.o)
BRIDGE_OBJ = $(BRIDGE_SRC:.c=.o)
CHIPSET_OBJ = $(CHIPSET_SRC:.c=.o)
DEMO_OBJ = $(DEMO_SRC:.c=.o)

ALL_OBJ = $(AI_OBJ) $(BRIDGE_OBJ) $(CHIPSET_OBJ) $(DEMO_OBJ)

# Target
TARGET = parrot_winkernel_demo

# Default target
all: $(TARGET)

# Build demo
$(TARGET): $(ALL_OBJ)
	@echo "Linking $@..."
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)
	@echo "✓ Build complete: $(TARGET)"

# Compile C files
%.o: %.c
	@echo "Compiling $<..."
	$(CC) $(CFLAGS) -c $< -o $@

# Clean
clean:
	@echo "Cleaning build artifacts..."
	rm -f $(ALL_OBJ) $(TARGET)
	@echo "✓ Clean complete"

# Run demo
run: $(TARGET)
	@echo "Running ParrotWinKernel Demo..."
	@echo ""
	./$(TARGET)

# Install (requires root)
install: $(TARGET)
	@echo "Installing ParrotWinKernel..."
	install -d /opt/parrot_winkernel/bin
	install -m 755 $(TARGET) /opt/parrot_winkernel/bin/
	install -d /opt/parrot_winkernel/drivers
	@echo "✓ Installation complete"
	@echo ""
	@echo "To run: /opt/parrot_winkernel/bin/$(TARGET)"

# Uninstall
uninstall:
	@echo "Uninstalling ParrotWinKernel..."
	rm -rf /opt/parrot_winkernel
	@echo "✓ Uninstall complete"

# Help
help:
	@echo "ParrotWinKernel Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all        - Build everything (default)"
	@echo "  clean      - Remove build artifacts"
	@echo "  run        - Build and run demo"
	@echo "  install    - Install to system (requires root)"
	@echo "  uninstall  - Remove from system (requires root)"
	@echo "  help       - Show this help"
	@echo ""
	@echo "Components:"
	@echo "  - AI Communication Buffer (ai_buffer/)"
	@echo "  - Kernel Bridge (kernel_bridge/)"
	@echo "  - Chipset Drivers (chipset_drivers/)"
	@echo "  - Demo Application (demo_main.c)"

.PHONY: all clean run install uninstall help
