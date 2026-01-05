# Makefile for Port Forwarding Module

CC = gcc
CFLAGS = -Wall -Wextra -O2 -fPIC -pthread
LDFLAGS = -shared -pthread

# Targets
TARGET_LIB = libportforward.so
TARGET_TEST = port_forward_test

# Sources
SRC = port_forward.c
OBJ = $(SRC:.c=.o)
TEST_SRC = port_forward_test.c
TEST_OBJ = $(TEST_SRC:.c=.o)

# Default target
all: $(TARGET_LIB)

# Build shared library
$(TARGET_LIB): $(OBJ)
	$(CC) $(LDFLAGS) -o $@ $^

# Build object files
%.o: %.c port_forward.h
	$(CC) $(CFLAGS) -c $< -o $@

# Build test program
test: $(TARGET_TEST)

$(TARGET_TEST): $(TEST_OBJ) $(TARGET_LIB)
	$(CC) -o $@ $< -L. -lportforward -pthread

# Clean
clean:
	rm -f $(OBJ) $(TEST_OBJ) $(TARGET_LIB) $(TARGET_TEST)

# Install
install: $(TARGET_LIB)
	install -d $(DESTDIR)/usr/lib
	install -m 755 $(TARGET_LIB) $(DESTDIR)/usr/lib/
	install -d $(DESTDIR)/usr/include/parrot_winkernel
	install -m 644 port_forward.h $(DESTDIR)/usr/include/parrot_winkernel/

# Uninstall
uninstall:
	rm -f $(DESTDIR)/usr/lib/$(TARGET_LIB)
	rm -f $(DESTDIR)/usr/include/parrot_winkernel/port_forward.h

.PHONY: all test clean install uninstall
