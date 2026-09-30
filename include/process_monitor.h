#ifndef PROCESS_MONITOR_H
#define PROCESS_MONITOR_H

#include <pthread.h>

#define MAX_PROCESSES 10


extern int process_count;
extern int process_ids[MAX_PROCESSES];

extern pthread_t process_thread_id;


void *process_thread(void *arg);

#endif
