#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

#include "system_resources.h"
#include "process_monitor.h"

void show_resources()
{
    pthread_t cpu_thread;
    pthread_t memory_thread;
    pthread_t disk_thread;
    pthread_t uptime_thread;
    pthread_t os_thread;

    reset_completed_threads();

    pthread_create(&cpu_thread, NULL, cpu_usage, NULL);
    pthread_create(&memory_thread, NULL, memory_usage, NULL);
    pthread_create(&disk_thread, NULL, disk_usage, NULL);
    pthread_create(&uptime_thread, NULL, uptime, NULL);
    pthread_create(&os_thread, NULL, os_info, NULL);

    pthread_join(cpu_thread, NULL);
    pthread_join(memory_thread, NULL);
    pthread_join(disk_thread, NULL);
    pthread_join(uptime_thread, NULL);
    pthread_join(os_thread, NULL);

    printf("\nThreads completed: %d/5\n", get_completed_threads());
}

int main()
{
    int choice;

    while (1)
    {
        printf("\n");
        printf("====================================\n");
        printf("       LINUX SYSTEM MONITOR\n");
        printf("====================================\n");
        printf("1. Process Monitoring\n");
        printf("2. System Resources\n");
        printf("3. Refresh\n");
        printf("4. Exit\n");
        printf("====================================\n");
        printf("Enter choice: ");

        scanf("%d", &choice);

        if (choice == 1)
        {
            show_processes();
        }
        else if (choice == 2)
        {
            printf("\n");
            show_resources();
        }
        else if (choice == 3)
        {
            printf("\033[2J\033[H");
            printf("Refreshing...\n\n");
            show_resources();
        }
        else if (choice == 4)
        {
            printf("\nExiting program...\n");
            break;
        }
        else
        {
            printf("\nInvalid choice. Try again.\n");
        }
    }

    return 0;
}
