CC = gcc
CFLAGS = -Wall -pthread

monitor: main.c system_resources.c process_monitor.c
	$(CC) $(CFLAGS) main.c system_resources.c process_monitor.c -o monitor

clean:
	rm -f monitor
