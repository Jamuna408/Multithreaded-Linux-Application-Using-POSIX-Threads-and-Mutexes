# Multithreaded Linux Application Using POSIX Threads and Mutexes

## Project Overview

This project is a Linux System Monitoring Application developed using the C programming language.

The application provides information about running processes and important system resources. It also demonstrates operating system concepts such as multithreading, mutex synchronization, shared resources, critical sections, and race-condition prevention.

## Features

- Process monitoring
- CPU usage monitoring
- RAM usage monitoring
- Disk usage monitoring
- System uptime monitoring
- Operating system information
- Kernel version information
- POSIX thread creation and synchronization
- Mutex-based protection of shared data
- Menu-based user interface
- Refresh option for system information

## Multithreading

The system resource monitoring module uses five POSIX threads.

| Thread | Task |
|---|---|
| CPU Thread | Monitors CPU usage |
| Memory Thread | Monitors RAM usage |
| Disk Thread | Monitors disk usage |
| Uptime Thread | Displays system uptime |
| OS Thread | Displays OS and kernel information |

Threads are created using `pthread_create()` and the main program waits for them using `pthread_join()`.

## Mutex and Synchronization

The application uses a POSIX mutex to protect shared data accessed by multiple threads.

The shared variable `completed_threads` keeps track of how many monitoring threads have completed their tasks.

The mutex protects this shared resource from simultaneous access and helps prevent race conditions.

## Project Structure

```text
Multithreaded-Linux-Application-Using-POSIX-Threads-and-Mutexes/
│
├── docs/
│   ├── OS Abstract.pdf
│   └── Operating Systems Project PPT.pdf
│
├── include/
│   ├── process_monitor.h
│   └── system_resources.h
│
├── src/
│   ├── main.c
│   ├── process_monitor.c
│   └── system_resources.c
│
├── .gitignore
├── Makefile
└── README.md
