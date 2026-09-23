#ifndef SYSTEM_RESOURCES_H
#define SYSTEM_RESOURCES_H

void *cpu_usage(void *arg);
void *memory_usage(void *arg);
void *disk_usage(void *arg);
void *uptime(void *arg);
void *os_info(void *arg);

int get_completed_threads();
void reset_completed_threads();

#endif
