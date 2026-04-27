
#pragma once

#include "Types.h"
#include "Point.h"

#include <fcntl.h>
#include <sys/stat.h>
#include <vector>
#include <semaphore.h>

class Memory {
public:
    #pragma pack(push, 1)
    struct  InitData {
        i32 cityCount;
        i32 method;

        bool gpu; 
        bool benchmark; 

        char padding[6];
        
        Point pts[0];
    };
    #pragma pack(pop)

    #pragma pack(push, 1)
    struct BatchData {
        #pragma pack(push, 1)
        struct Header {
            i32 batchSize;
            i32 minPathIndex;
        };
        #pragma pack(pop)

        Header header;
        u16 indices[];
    };
    #pragma pack(pop)

    /*
    ipcInfo[0]: shm name
    ipcInfo[1]: shm size
    ipcInfo[2]: sem init name
    ipcInfo[3]: sem data available name
    ipcInfo[4]: sem data consumed name
    */
    Memory(char* ipcInfo[]);
    ~Memory();

    void awaitInitData();
    void disposeInitData();
    void awaitDataConsumed();
    void postDataAvailable();

    void newBatch();
    void setBatchSize(i32 size);
    void setMinPathIndex(i32 index);

    bool nextPath();
    void setNextPathIndex(u16 index);

    InitData* getInitData();
    u16& operator[](u32 n);

private:
    i32 shmBytes;
    i32 maxPaths;

    i32 pathCount;
    i32 index;

    void* region;
    BatchData* batchData;
    InitData* initData;

    sem_t* semInit;
    sem_t* semDataAvailable;
    sem_t* semDataConsumed;

    void openShm(char* shmName);
    void openSem(sem_t*& sem, char* semName);
};