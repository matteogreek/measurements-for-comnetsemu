# Twamp for ComNetsEmu

## How to use

1.  Move inside the *twamp* directory located in the *examples* folder
2. Run the shell script called *build_image.sh* to build the Docker image

	```
	$ bash ./build_image.sh
	```
3. Run *topology.py* to create the network topology and launch twamp protocol

	```
	$ sudo python3 ./topology.py
	```
	
## How it was built

### Main Function

The main function consists of a Python implementation of the **Two-Way Active Measurement Protocol (TWAMP)** as defined in [RFC5357](https://tools.ietf.org/html/rfc5357).
The implementation of the twamp protocol used can be found here: https://github.com/nokia/twampy.

### Containerization 

To containerize the Python script we create the *Dockerfile* for the respective Docker image.
Then we create the image with the command shown below found inside the file called *build_image.sh*

```
$ docker build -t twamp --file ./Dockerfile
```

###  Network Topology Emulation

After the containerization process we can emulate with **ComNetsEmu** a network topology to run the twamp protocol  
The emulated topology is the following:

![image](/util/topology.PNG)
