#include <stdio.h>
#include <pthread.h>

#include "../include/race_demo.h"

#define NUMBER_OF_THREADS 2
#define INCREMENTS 1000000

int counter = 0;

pthread_mutex_t counter_mutex =
    PTHREAD_MUTEX_INITIALIZER;

void *increment_without_mutex(void *arg)
{
    (void)arg;

    for (int i = 0; i < INCREMENTS; i++)
    {
        counter++;
    }

    return NULL;
}

void *increment_with_mutex(void *arg)
{
    (void)arg;

    for (int i = 0; i < INCREMENTS; i++)
    {
        pthread_mutex_lock(&counter_mutex);

        counter++;

        pthread_mutex_unlock(&counter_mutex);
    }

    return NULL;
}

void run_race_demo()
{
    pthread_t thread1;
    pthread_t thread2;

    printf("\n============================================\n");
    printf("          RACE CONDITION DEMO\n");
    printf("============================================\n");

    counter = 0;

    printf("\nWITHOUT MUTEX\n");
    printf("------------------------------\n");

    pthread_create(
        &thread1,
        NULL,
        increment_without_mutex,
        NULL
    );

    pthread_create(
        &thread2,
        NULL,
        increment_without_mutex,
        NULL
    );

    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    printf("Expected Counter : %d\n",
           NUMBER_OF_THREADS * INCREMENTS);

    printf("Actual Counter   : %d\n",
           counter);

    counter = 0;

    printf("\nWITH MUTEX\n");
    printf("------------------------------\n");

    pthread_create(
        &thread1,
        NULL,
        increment_with_mutex,
        NULL
    );

    pthread_create(
        &thread2,
        NULL,
        increment_with_mutex,
        NULL
    );

    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    printf("Expected Counter : %d\n",
           NUMBER_OF_THREADS * INCREMENTS);

    printf("Actual Counter   : %d\n",
           counter);

    printf("\n============================================\n");
    printf("              DEMO COMPLETE\n");
    printf("============================================\n");
}
