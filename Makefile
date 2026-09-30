CC = gcc

CFLAGS = -Wall -Wextra -Iinclude

TARGET = monitor

SOURCES = src/main.c \
          src/system_resources.c \
          src/process_monitor.c \
          src/race_demo.c

all:
	$(CC) $(CFLAGS) $(SOURCES) -o $(TARGET) -pthread

clean:
	rm -f $(TARGET) race_demo
