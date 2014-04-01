







































































    	for (int i = 0; i < 128; i++) {
        	fd[i] = -1;
    	}	



    	
    	pthread_mutex_lock(&smMutex);	//Get lock on getInstance mutex
    	
    	if (smInstance == NULL){
        	
        	smInstance = new I2C_Adapter_RPI();
    	}
    	
    	pthread_mutex_unlock(&smMutex);	//Release lock on getInstance mutex
    	
    	return smInstance;



    	I2C_Adapter_RPI::debug_mode = b;



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


