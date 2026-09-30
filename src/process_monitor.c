#include <stdio.h>
#include <pthread.h>
#include <unistd.h>
#include <stdlib.h>
#include <dirent.h>
#include <ctype.h>

#include "../include/process_monitor.h"
#include "../include/system_resources.h"


int process_count = 0;
int process_ids[MAX_PROCESSES];

pthread_t process_thread_id;


/* PROCESS THREAD */
void *process_thread(void *arg)
{
    (void)arg;

    while (1)
    {
        DIR *directory = opendir("/proc");

        if (directory != NULL)
        {
            struct dirent *entry;

            int count = 0;
            int total_count = 0;

            while ((entry = readdir(directory)) != NULL)
            {
                int is_number = 1;

                for (int i = 0;
                     entry->d_name[i] != '\0';
                     i++)
                {
                    if (!isdigit(entry->d_name[i]))
                    {
                        is_number = 0;
                        break;
                    }
                }

                if (is_number)
                {
                    total_count++;

                    if (count < MAX_PROCESSES)
                    {
                        process_ids[count] =
                            atoi(entry->d_name);

                        count++;
                    }
                }
            }

            closedir(directory);

            pthread_mutex_lock(&data_mutex);

            process_count = total_count;

            pthread_mutex_unlock(&data_mutex);
        }

        sleep(1);
    }

    return NULL;
}
