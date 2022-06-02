# Rb_Controller

This project was developed on a Raspberry Pi model 2B running Raspberry Pi OS (VERSION?). The official 7" touch display was used.

## Installation

* Install Raspberry Pi OS on SD card
* Rotate display in settings
* Connect via Ethernet to internet
* For convenience, install virtual keyboard 
	```sh
	sudo apt install matchbox-keyboard
	```
* Setup static ip address using this [guide](https://raspberrypi-guide.github.io/networking/set-up-static-ip-address)
* Install python v. 3.10.4 or newer. There is a guide [here](https://allurcode.com/install-latest-version-of-python-on-raspberry-pi/). 
	OBS. DO NOT MAKE THE NEW VERSION DEFAULT
* Virtual environment [setup](https://docs.python.org/3/tutorial/venv.html) 
	OBS. Use python3.10.4 to create virtual environment
* Activate the virtaul environment
	```sh
	source .venv/RbController/bin/activate
	```
* Verify that 
	```sh
	python --version

 	```
	and 
	```sh
	pip --version
	```
	are using `python3.10.4`. Otherwise, try the same with `python3 --version` and `pip3 --version` and use these from now on.
* Clone the repo
	```sh
	cd /home/pi/
	git clone https://github.com/leouhre/Rb_Controller.git
	```
* Update pip and install requirements.txt
	```sh
	python -m pip install --upgrade pip
	cd /home/pi/Rb_Controller
	pip install -r requirements.txt
* I had to fix pip by going into `~/Python3.10.4/` and run `./configure`, then `make` and then `sudo make install`. Then re-run `pip install -r requirements`. This step takes ~1hr.
* Move `99-ea-psu.rules`, `99-lucidIo.rules` and `backlight-permissions.rules` to `/etc/udev/rules.d/` and restart `udev` with
	```sh
	mv 99-ea-psu.rules /home/pi/Rb_Controller/installation /etc/udev/rules.d/
	mv 99-lucidIo.rules /home/pi/Rb_Controller/installation /etc/udev/rules.d/
	mv backlight-permissions.rules /home/pi/Rb_Controller/installation /etc/udev/rules.d/
	sudo service udev restart
	``` 
* Final step: Make an executable on desktop