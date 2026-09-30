# Linux System Monitor

A multithreaded Linux system monitoring application developed using C, POSIX threads, and mutex synchronization.

## Project Description

Linux System Monitor monitors important system resources in real time using multiple POSIX threads.

The application monitors:

- CPU usage
- Memory usage
- Disk usage
- Network activity
- Running processes and PIDs
- System uptime

The project also demonstrates race conditions and shows how mutex synchronization prevents incorrect access to shared resources.

## Operating System Concepts

This project demonstrates:

- POSIX threads
- Concurrent execution
- Shared resources
- Critical sections
- Mutex synchronization
- Race conditions
- Mutual exclusion
- Process monitoring

## Threads

The application uses five monitoring threads:

1. CPU Thread
2. Memory Thread
3. Disk Thread
4. Process Thread
5. Network Thread

## Project Structure

```text
linux-system-monitor/
├── Makefile
├── README.md
├── include/
│   ├── system_resources.h
│   ├── process_monitor.h
│   └── race_demo.h
└── src/
    ├── main.c
    ├── system_resources.c
    ├── process_monitor.c
    └── race_demo.c
