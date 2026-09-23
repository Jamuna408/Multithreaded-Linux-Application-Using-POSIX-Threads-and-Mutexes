CC = gcc
CFLAGS = -Wall -pthread -Iinclude

monitor: src/main.c src/system_resources.c src/process_monitor.c
	$(CC) $(CFLAGS) src/main.c src/system_resources.c src/process_monitor.c -o monitor

clean:
	rm -f monitor
