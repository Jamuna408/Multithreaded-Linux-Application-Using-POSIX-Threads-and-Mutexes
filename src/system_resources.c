#include <stdio.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/statvfs.h>
#include <string.h>

#include "../include/system_resources.h"


double cpu_usage = 0.0;
double memory_usage = 0.0;
double disk_usage = 0.0;

unsigned long long network_received = 0;
unsigned long long network_transmitted = 0;

double system_uptime = 0.0;


pthread_t cpu_thread_id;
pthread_t memory_thread_id;
pthread_t disk_thread_id;
pthread_t network_thread_id;


pthread_mutex_t data_mutex = PTHREAD_MUTEX_INITIALIZER;


/* CPU THREAD */
void *cpu_thread(void *arg)
{
    (void)arg;

    while (1)
    {
        FILE *file = fopen("/proc/stat", "r");

        if (file != NULL)
        {
            unsigned long long user1, nice1;
            unsigned long long system1, idle1;

            unsigned long long user2, nice2;
            unsigned long long system2, idle2;

            fscanf(file,
                   "cpu %llu %llu %llu %llu",
                   &user1,
                   &nice1,
                   &system1,
                   &idle1);

            fclose(file);

            sleep(1);

            file = fopen("/proc/stat", "r");

            if (file != NULL)
            {
                fscanf(file,
                       "cpu %llu %llu %llu %llu",
                       &user2,
                       &nice2,
                       &system2,
                       &idle2);

                fclose(file);

                unsigned long long total1 =
                    user1 + nice1 + system1 + idle1;

                unsigned long long total2 =
                    user2 + nice2 + system2 + idle2;

                unsigned long long total_diff =
                    total2 - total1;

                unsigned long long idle_diff =
                    idle2 - idle1;

                if (total_diff > 0)
                {
                    double usage =
                        100.0 *
                        (1.0 -
                        ((double)idle_diff / total_diff));

                    pthread_mutex_lock(&data_mutex);

                    cpu_usage = usage;

                    pthread_mutex_unlock(&data_mutex);
                }
            }
        }
    }

    return NULL;
}


/* MEMORY THREAD */
void *memory_thread(void *arg)
{
    (void)arg;

    while (1)
    {
        FILE *file = fopen("/proc/meminfo", "r");

        if (file != NULL)
        {
            unsigned long long total_memory;
            unsigned long long free_memory;

            fscanf(file,
                   "MemTotal: %llu kB\n",
                   &total_memory);

            fscanf(file,
                   "MemFree: %llu kB",
                   &free_memory);

            fclose(file);

            if (total_memory > 0)
            {
                double usage =
                    100.0 *
                    (1.0 -
                    ((double)free_memory /
                    total_memory));

                pthread_mutex_lock(&data_mutex);

                memory_usage = usage;

                pthread_mutex_unlock(&data_mutex);
            }
        }

        sleep(1);
    }

    return NULL;
}


/* DISK THREAD */
void *disk_thread(void *arg)
{
    (void)arg;

    while (1)
    {
        struct statvfs disk;

        if (statvfs("/", &disk) == 0)
        {
            unsigned long long total =
                disk.f_blocks * disk.f_frsize;

            unsigned long long free_space =
                disk.f_bfree * disk.f_frsize;

            if (total > 0)
            {
                double usage =
                    100.0 *
                    (1.0 -
                    ((double)free_space /
                    total));

                pthread_mutex_lock(&data_mutex);

                disk_usage = usage;

                pthread_mutex_unlock(&data_mutex);
            }
        }

        sleep(1);
    }

    return NULL;
}


/* NETWORK THREAD */
void *network_thread(void *arg)
{
    (void)arg;

    while (1)
    {
        FILE *file = fopen("/proc/net/dev", "r");

        if (file != NULL)
        {
            char line[512];

            unsigned long long total_received = 0;
            unsigned long long total_transmitted = 0;

            while (fgets(line, sizeof(line), file))
            {
                char *colon = strchr(line, ':');

                if (colon != NULL)
                {
                    unsigned long long received;
                    unsigned long long transmitted;

                    if (sscanf(
                        colon + 1,
                        " %llu %*u %*u %*u %*u %*u %*u %*u %llu",
                        &received,
                        &transmitted) == 2)
                    {
                        total_received += received;
                        total_transmitted += transmitted;
                    }
                }
            }

            fclose(file);

            pthread_mutex_lock(&data_mutex);

            network_received = total_received;
            network_transmitted = total_transmitted;

            pthread_mutex_unlock(&data_mutex);
        }

        sleep(1);
    }

    return NULL;
}


/* SYSTEM UPTIME */
void update_uptime()
{
    FILE *file = fopen("/proc/uptime", "r");

    if (file != NULL)
    {
        double uptime;

        fscanf(file, "%lf", &uptime);

        fclose(file);

        pthread_mutex_lock(&data_mutex);

        system_uptime = uptime;

        pthread_mutex_unlock(&data_mutex);
    }
}
