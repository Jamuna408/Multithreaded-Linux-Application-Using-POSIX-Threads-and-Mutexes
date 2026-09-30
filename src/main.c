#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

#include "../include/system_resources.h"
#include "../include/process_monitor.h"
#include "../include/race_demo.h"

void display_dashboard()
{
    while (1)
    {
        update_uptime();

        pthread_mutex_lock(&data_mutex);

        double cpu = cpu_usage;
        double memory = memory_usage;
        double disk = disk_usage;
        double uptime = system_uptime;

        int total_processes = process_count;

        unsigned long long received =
            network_received;

        unsigned long long transmitted =
            network_transmitted;

        int pids[MAX_PROCESSES];

        int displayed_pids = total_processes;

        if (displayed_pids > MAX_PROCESSES)
        {
            displayed_pids = MAX_PROCESSES;
        }

        for (int i = 0; i < displayed_pids; i++)
        {
            pids[i] = process_ids[i];
        }

        pthread_mutex_unlock(&data_mutex);


        int hours = (int)uptime / 3600;

        int minutes =
            ((int)uptime % 3600) / 60;

        int seconds =
            (int)uptime % 60;


        printf("\033[2J");
        printf("\033[H");


        printf("==================================================\n");
        printf("             LINUX SYSTEM MONITOR\n");
        printf("==================================================\n\n");


        printf("THREAD INFORMATION\n");
        printf("------------------------------\n");

        printf("CPU Thread ID      : %lu\n",
               (unsigned long)cpu_thread_id);

        printf("Memory Thread ID   : %lu\n",
               (unsigned long)memory_thread_id);

        printf("Disk Thread ID     : %lu\n",
               (unsigned long)disk_thread_id);

        printf("Process Thread ID  : %lu\n",
               (unsigned long)process_thread_id);

        printf("Network Thread ID  : %lu\n",
               (unsigned long)network_thread_id);


        printf("\nSYSTEM INFORMATION\n");
        printf("------------------------------\n");

        printf("CPU Usage          : %.2f %%\n",
               cpu);

        printf("Memory Usage       : %.2f %%\n",
               memory);

        printf("Disk Usage         : %.2f %%\n",
               disk);

        printf("System Uptime      : %02d:%02d:%02d\n",
               hours,
               minutes,
               seconds);


        printf("\nNETWORK INFORMATION\n");
        printf("------------------------------\n");

        printf("Received Bytes     : %llu\n",
               received);

        printf("Transmitted Bytes  : %llu\n",
               transmitted);


        printf("\nPROCESS MONITOR\n");
        printf("------------------------------\n");

        printf("Total Processes    : %d\n",
               total_processes);

        printf("First 10 PIDs      : ");

        for (int i = 0; i < displayed_pids; i++)
        {
            printf("%d ", pids[i]);
        }

        printf("\n");


        printf("\nMUTEX PROTECTION   : ENABLED\n");
        printf("STATUS             : Monitoring...\n");

        printf("\nPress Ctrl+C to exit.\n");

        sleep(2);
    }
}


int main()
{
    printf("Starting Linux System Monitor...\n");


    pthread_create(
        &cpu_thread_id,
        NULL,
        cpu_thread,
        NULL
    );


    pthread_create(
        &memory_thread_id,
        NULL,
        memory_thread,
        NULL
    );


    pthread_create(
        &disk_thread_id,
        NULL,
        disk_thread,
        NULL
    );


    pthread_create(
        &process_thread_id,
        NULL,
        process_thread,
        NULL
    );


    pthread_create(
        &network_thread_id,
        NULL,
        network_thread,
        NULL
    );

run_race_demo();
    display_dashboard();

    return 0;
}
