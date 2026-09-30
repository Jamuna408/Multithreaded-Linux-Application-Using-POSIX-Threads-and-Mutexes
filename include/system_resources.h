#ifndef SYSTEM_RESOURCES_H
#define SYSTEM_RESOURCES_H

#include <pthread.h>


extern double cpu_usage;
extern double memory_usage;
extern double disk_usage;

extern unsigned long long network_received;
extern unsigned long long network_transmitted;

extern double system_uptime;


extern pthread_t cpu_thread_id;
extern pthread_t memory_thread_id;
extern pthread_t disk_thread_id;
extern pthread_t network_thread_id;


extern pthread_mutex_t data_mutex;


void *cpu_thread(void *arg);
void *memory_thread(void *arg);
void *disk_thread(void *arg);
void *network_thread(void *arg);

void update_uptime();

#endif
