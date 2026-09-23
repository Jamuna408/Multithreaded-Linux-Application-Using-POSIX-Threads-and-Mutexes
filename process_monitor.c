#include <stdio.h>
#include <stdlib.h>
#include "process_monitor.h"

void show_processes()
{
    printf("\n");
    printf("============================================\n");
    printf("          RUNNING PROCESSES\n");
    printf("============================================\n");

    system("ps -eo pid,stat,comm,%cpu,%mem --sort=-%cpu | head -n 11");
}
