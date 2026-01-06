# Makefile for USB Driver Loader PoC

CC = gcc
CFLAGS = -Wall -Wextra -O2 -pthread
LDFLAGS = -ldl -pthread

TARGET = usb_driver_loader
SRC = usb_driver_loader.c

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f $(TARGET)

test: $(TARGET)
	@echo "To test, run: ./$(TARGET) <driver.so>"
	@echo "Note: Requires a Windows driver converted to .so format"

.PHONY: all clean test
