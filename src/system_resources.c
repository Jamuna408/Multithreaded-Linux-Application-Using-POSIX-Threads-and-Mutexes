#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "system_resources.h"

/* Mutex protects shared data and output */
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

/* Shared resource used by all threads */
int completed_threads = 0;

/* Thread 1: monitors CPU usage */
void *cpu_usage(void *arg)
{
    pthread_mutex_lock(&mutex);

    printf("CPU Usage       : ");
    fflush(stdout);
    system("top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'");

    completed_threads++;

    pthread_mutex_unlock(&mutex);

    return NULL;
}

/* Thread 2: monitors RAM usage */
void *memory_usage(void *arg)
{
    pthread_mutex_lock(&mutex);

    printf("RAM Usage       : ");
    fflush(stdout);
    system("free -h | awk '/Mem:/ {print $3 \" / \" $2}'");

    completed_threads++;

    pthread_mutex_unlock(&mutex);

    return NULL;
}

/* Thread 3: monitors disk usage */
void *disk_usage(void *arg)
{
    pthread_mutex_lock(&mutex);

    printf("Disk Usage      : ");
    fflush(stdout);
    system("df -h / | awk 'NR==2 {print $5}'");

    completed_threads++;

    pthread_mutex_unlock(&mutex);

    return NULL;
}

/* Thread 4: monitors system uptime */
void *uptime(void *arg)
{
    pthread_mutex_lock(&mutex);

    printf("System Uptime   : ");
    fflush(stdout);
    system("uptime -p");

    completed_threads++;

    pthread_mutex_unlock(&mutex);

    return NULL;
}

/* Thread 5: monitors OS and kernel information */
void *os_info(void *arg)
{
    pthread_mutex_lock(&mutex);

    printf("Operating System : ");
    fflush(stdout);
    system("grep PRETTY_NAME /etc/os-release | cut -d= -f2-");

    printf("Kernel Version   : ");
    fflush(stdout);
    system("uname -r");

    completed_threads++;

    pthread_mutex_unlock(&mutex);

    return NULL;
}

int get_completed_threads()
{
    int value;

    pthread_mutex_lock(&mutex);

    value = completed_threads;

    pthread_mutex_unlock(&mutex);

    return value;
}

void reset_completed_threads()
{
    pthread_mutex_lock(&mutex);

    completed_threads = 0;

    pthread_mutex_unlock(&mutex);
}
