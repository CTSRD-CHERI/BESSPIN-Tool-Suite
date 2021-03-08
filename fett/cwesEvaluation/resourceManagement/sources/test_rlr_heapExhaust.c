#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>

#if (defined(testgenOnFreeRTOS) && defined(testgenQEMU))
    #define MALLOC_SIZE_MAX 0x008F 
    #define MALLOC_SIZE_MIN 0x0000
#else
    #define MALLOC_SIZE_MAX 0xFFFF 
    #define MALLOC_SIZE_MIN 0xF000
#endif

#define PERCENT_FREE 100 // Free 1 in 100 allocations

#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
    #include "FreeRTOS.h"
    #define MALLOC pvPortMalloc
    #define FREE vPortFree
#else
    #define MALLOC malloc
    #define FREE free
#endif

static char * exhaustHeap (void); 

// --------------- FreeRTOS Test ---------------
#ifdef testgenOnFreeRTOS
    #define NUM_OF_TEST_PARTS 1

    void main() {
        printf("\n<OSIMAGE=FreeRTOS>\n");
        #if TESTGEN_TEST_PART == 1
            exhaustHeap();
            printf("\n<END-OF-MAIN>\n");
        #else
            printf("\n<INVALID> Part[%d] not in [1,%d].\n",TESTGEN_TEST_PART,NUM_OF_TEST_PARTS);
        #endif
        return;
    }

// --------------- Debian && FreeBSD test ---------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))
#include "unbufferStdout.h"
    int main(void);

    int main() {
        unbufferStdout();
        exhaustHeap();
        printf("\n<END-OF-MAIN>\n");
        return 0;
    }

#endif //ifdef testgenOnFreeRTOS

static char * exhaustHeap (void) {
    char * dump;
    size_t xSizeToMalloc;
    char valToWrite;

    srand(RM_SEED); //RM_SEED is written in fett/cwesEvaluation/build.py

    while(1) {
        xSizeToMalloc = (size_t) ((rand() % (MALLOC_SIZE_MAX-MALLOC_SIZE_MIN+1)) + MALLOC_SIZE_MIN);
        dump = (char *) MALLOC(xSizeToMalloc * sizeof(char));
        valToWrite = (char) (rand()%256); 
        memset (dump, valToWrite, xSizeToMalloc * sizeof(char)); 
        if (!(rand()%PERCENT_FREE)) {
            FREE(dump);
        }
    }

    return dump;
}
