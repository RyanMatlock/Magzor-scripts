/*
 * File: i2c_adapter_rpi.cpp
 * Author: Sonny Sung
 * Contact: sonny.sung.cs [@T] gmail [DOT] com
 * 
 * Created: June, 27, 2013
 * 
 * Description:
 * I2C Adapter for the Raspberry Pi.
 * Based class off of i2c_adapter.h
 * Manages read and write operations on the RPI.
 * Uses the wiringPi library developed by Drogon, http://wiringpi.com/.
 * Singleton class and relatively thread safe using pthread's mutex (not fully tested).
 */
#include "i2c_adapter_rpi.h"
#include <time.h>
#include <string.h>

static uint16_t crc_table [256] = {

0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5,
0x60c6, 0x70e7, 0x8108, 0x9129, 0xa14a, 0xb16b,
0xc18c, 0xd1ad, 0xe1ce, 0xf1ef, 0x1231, 0x0210,
0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c,
0xf3ff, 0xe3de, 0x2462, 0x3443, 0x0420, 0x1401,
0x64e6, 0x74c7, 0x44a4, 0x5485, 0xa56a, 0xb54b,
0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6,
0x5695, 0x46b4, 0xb75b, 0xa77a, 0x9719, 0x8738,
0xf7df, 0xe7fe, 0xd79d, 0xc7bc, 0x48c4, 0x58e5,
0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969,
0xa90a, 0xb92b, 0x5af5, 0x4ad4, 0x7ab7, 0x6a96,
0x1a71, 0x0a50, 0x3a33, 0x2a12, 0xdbfd, 0xcbdc,
0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03,
0x0c60, 0x1c41, 0xedae, 0xfd8f, 0xcdec, 0xddcd,
0xad2a, 0xbd0b, 0x8d68, 0x9d49, 0x7e97, 0x6eb6,
0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a,
0x9f59, 0x8f78, 0x9188, 0x81a9, 0xb1ca, 0xa1eb,
0xd10c, 0xc12d, 0xf14e, 0xe16f, 0x1080, 0x00a1,
0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c,
0xe37f, 0xf35e, 0x02b1, 0x1290, 0x22f3, 0x32d2,
0x4235, 0x5214, 0x6277, 0x7256, 0xb5ea, 0xa5cb,
0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447,
0x5424, 0x4405, 0xa7db, 0xb7fa, 0x8799, 0x97b8,
0xe75f, 0xf77e, 0xc71d, 0xd73c, 0x26d3, 0x36f2,
0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9,
0xb98a, 0xa9ab, 0x5844, 0x4865, 0x7806, 0x6827,
0x18c0, 0x08e1, 0x3882, 0x28a3, 0xcb7d, 0xdb5c,
0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0,
0x2ab3, 0x3a92, 0xfd2e, 0xed0f, 0xdd6c, 0xcd4d,
0xbdaa, 0xad8b, 0x9de8, 0x8dc9, 0x7c26, 0x6c07,
0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba,
0x8fd9, 0x9ff8, 0x6e17, 0x7e36, 0x4e55, 0x5e74,
0x2e93, 0x3eb2, 0x0ed1, 0x1ef0
};

I2C_Adapter_RPI* I2C_Adapter_RPI::smInstance = NULL;
pthread_mutex_t I2C_Adapter_RPI::smMutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t I2C_Adapter_RPI::aMutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t I2C_Adapter_RPI::rwMutex = PTHREAD_MUTEX_INITIALIZER;
bool I2C_Adapter_RPI::debug_mode = true;

I2C_Adapter_RPI::I2C_Adapter_RPI(){
    for (int i = 0; i < 128; i++) {
        fd[i] = -1;
    }	
}

I2C_Adapter_RPI* I2C_Adapter_RPI::getInstance(){ 
    
    pthread_mutex_lock(&smMutex);	//Get lock on getInstance mutex
    
    if (smInstance == NULL){
        
        smInstance = new I2C_Adapter_RPI();
    }
    
    pthread_mutex_unlock(&smMutex);	//Release lock on getInstance mutex
    
    return smInstance;
}

void I2C_Adapter_RPI::setDebug(bool b){
    I2C_Adapter_RPI::debug_mode = b;
}

bool I2C_Adapter_RPI::attach_fd(uint8_t addr){
    if((0 <= addr) & (addr < 128)){
        
        pthread_mutex_lock(&aMutex);			//Lock mutex for address acquire
        
        fd[addr] = wiringPiI2CSetup(addr);
        
        pthread_mutex_unlock(&aMutex);			//Unlock mutex for address acquire
        
        if(fd[addr] == -1){
            if(debug_mode){
                printf("Couldn't get device %u fd.\n", addr);
            }
            return true;
        }
        else{
            if(debug_mode){
                printf("Got device %u fd.\n", addr);
            }
            return false;
        }
    }	
    else{
        if(debug_mode){
            printf("Address %u is out of I2C range.\n", addr);
        }
        return false;
    }
}


void I2C_Adapter_RPI::checksum(unsigned char *d, uint8_t length, unsigned char *cs )
{ 
   unsigned int count;
   unsigned int crc = 0xffff;
   unsigned int temp;

   for (count = 0; count < length; ++count)
   {
     temp = (*d++ ^ (crc >> 8)) & 0xff;
     crc = crc_table[temp] ^ (crc << 8);
   }
   
   crc = (crc ^ 0x0000);
   
   cs[0] = (crc >> 8 ) & 0xFF;
   cs[1] = crc & 0xFF;
   
   //printf("CRC: 0x%02x 0x%02x\n", cs[0], cs[1]);
   
   return;
} 

            
int I2C_Adapter_RPI::writeI2C(uint8_t addr, unsigned char *w, uint8_t count){	
    unsigned char checksum_array[2];
    
    this->checksum(w, count, checksum_array);
    
    unsigned char checksum[2];
    
    uint8_t write_attempts = 0;
    
    while(1){
        this->writeReadI2C(addr, w, count, checksum, 2);
        
        if( (checksum[0] == checksum_array[0]) & (checksum[1] == checksum_array[1]) ){
            return count;
        }
        else if(write_attempts > ATTEMPTS){
            errorNum ++;
            printf("Error: Packet#%u CRC check failed -- max(5) attempts reached... giving up!\n", packetNum);
            return 0;
        }
        errorNum ++;
        write_attempts ++;
        printf("Error: P#%u CRC check failed -- attempt %d. I2C error rate: %f\n", packetNum, write_attempts, 100*((float)errorNum / (float)packetNum));
        
    }
}

int I2C_Adapter_RPI::writeI2C_no_checksum(uint8_t addr, unsigned char *w, uint8_t count){
    pthread_mutex_lock(&rwMutex); 	//Lock readwrite mutex
    packetNum++;
    
    if(fd[addr] == -1)
        attach_fd(addr);

    if(debug_mode){
        printf("Write(0x%02x) P#%u: ", addr, packetNum);
        for(int i = 0; i< count; i++){
            printf("0x%02x ", w[i]);
        }	
        printf("\n");
    }
    
    int ret = write(fd[addr], w, count);	
    pthread_mutex_unlock(&rwMutex); 	//Unlock readwrite mutex
    
    return ret;	//Returns the number of bytes written
}

int I2C_Adapter_RPI::readI2C(uint8_t addr, unsigned char *r, uint8_t count){
    pthread_mutex_lock(&rwMutex); 	//Lock readwrite mutex
    packetNum++;
    
    if(fd[addr] == -1)
        attach_fd(addr);
        
    int ret = read(fd[addr], r, count);
    
    if(debug_mode){
        printf("Read (0x%02x) P#%u: ", addr, packetNum);	
        for(int i = 0; i< count; i++){
            printf("0x%02x ", r[i]);
        }	
        printf("\n");
    }
    pthread_mutex_unlock(&rwMutex); 	//Unlock readwrite mutex
    
    return ret;	//Returns the number of bytes read
}

int I2C_Adapter_RPI::writeReadI2C(uint8_t addr, unsigned char *w, uint8_t wcount, unsigned char *r, uint8_t rcount, unsigned int readDelay){	
    pthread_mutex_lock(&rwMutex); 	//Lock readwrite mutex
    packetNum++;
    
    if(fd[addr] == -1){
        attach_fd(addr);
    }
    
    if(debug_mode){
        printf("Write(0x%02x) P#%u: ", addr, packetNum);
        for(int i = 0; i< wcount; i++){
            printf("0x%02x ", w[i]);
        }
        printf("\n");
    }

    write(fd[addr], w, wcount);
    
    if(readDelay != 0)				//Sets a delay between the write and read. Useful if the device needs to prepare data
        usleep(readDelay);		//Delays in milliseconds, BE CAREFUL WHEN USING: delay will hold the i2c bus until that duration is over
    
    int ret = read(fd[addr], r, rcount);
    
    if(debug_mode){
        printf("Read (0x%02x) P#%u: ", addr, packetNum);	
        for(int i = 0; i< rcount; i++){
            printf("0x%02x ", r[i]);
        }	
        printf("\n");
    }
        
    pthread_mutex_unlock(&rwMutex); 	//Unlock readwrite mutex
    
    return ret;	//Returns the number of bytes written
    
}

int I2C_Adapter_RPI::writeReadI2C_checksum(uint8_t addr, unsigned char *w, uint8_t wcount, unsigned char *r, uint8_t rcount, unsigned int readDelay){	
    unsigned char checksum_array[2];
    
    this->checksum(w, wcount, checksum_array);
    
    unsigned char* r_checksum = new unsigned char[rcount + 2];
    
    uint8_t write_attempts = 0;
    
    while(1){
        this->writeReadI2C(addr, w, wcount, r_checksum, rcount + 2, readDelay);
        
        if( (r_checksum[rcount] == checksum_array[0]) & (r_checksum[rcount+1] == checksum_array[1]) ){
            //memcpy( r, r_checksum, rcount * sizeof(unsigned char) );
            for(int i = 0; i < rcount; i ++){
                r[i] = r_checksum[i];
            }
            return rcount;
        }
        else if(write_attempts > ATTEMPTS){
            errorNum ++;
            printf("Error: Packet#%u CRC check failed -- max(5) attempts reached... giving up!\n", packetNum);
            return 0;
        }
        errorNum ++;
        write_attempts ++;
        printf("Error: P#%u CRC check failed -- attempt %d. I2C error rate: %f\n", packetNum, write_attempts, 100*((float)errorNum / (float)packetNum));
        
    }
}

