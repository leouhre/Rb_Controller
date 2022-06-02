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
Verify that 
	```sh
	python --version

 	```
and 
	```
	pip --version
	```
are using python3.10.4. Otherwise, try the same with (`python3 --version`) and (`pip --version`).
* Clone the repo
	```sh
	cd /home/pi/
	git clone https://github.com/leouhre/Rb_Controller.git
	```
* Update pip and install requirements.txt
	```sh
	python -m pip install --upgrade pip
	cd ~/Rb_Controller
	pip install -r requirements.txt
* I had to fix pip by going into ~/Python3.10.4/ and run './configure' then 'make' and then 'sudo make install' 
  and then re-run pip install requirements (this step takes ~1hr)
- Move 99-ea-psu.rules (git folder /installation) to /etc/udev/rules.d/
- Move 99-lucidIo.rules (git folder /installation) to /etc/udev/rules.d/ and restart udev with sudo service udev restart
- In order to install matplotlib, run:
  sudo apt-get install libjpeg-dev
  sudo apt-get install zlib1g-dev
  sudo apt-get install libpng-dev
- pip install matplotlib
- follow the matlab setup (configure existing OS) and enable I2C
  some packages might not successfully install:
	userland
	wiringpi
	tornado
	nnpy
	py-nanomsg

%%% skip these steps 
- in matlab terminal: r = raspi("192.168.137.132","pi","raspberry") FAILS
- install userland manually (https://snapcraft.io/install/rpi-userland/raspbian)
- in matlab terminal: r = raspi("192.168.137.132","pi","raspberry") FAILS
- install nanomsg manually:
	cd ~/
	wget https://github.com/nanomsg/nanomsg/archive/refs/tags/1.2.tar.gz
	tar -xvzf 1.2.tar.gz
	cd nanomsg-1.2
	then follow instructions in README.md:
    % mkdir build
    % cd build
    % cmake ..
    % cmake --build .
    % ctest .
    % sudo cmake --build . --target install
    % sudo ldconfig (if on Linux)
- in matlab terminal: r = raspi("192.168.137.132","pi","raspberry") FAILS
- sudo pip install nnpy (remember to install on python3.9 and not the newly installed python3.10.4)
%%% 

- install userland manually (https://snapcraft.io/install/rpi-userland/raspbian)
- in ~/opt/ run: sudo git clone https://github.com/raspberrypi/userland 
  and then in matlab: raspi.internal.updateServer('192.168.137.132','pi','raspberry') 
  (https://se.mathworks.com/matlabcentral/answers/1599884-not-able-to-install-userland-wiringpi-in-rasi-via-matlab-support-package-for-raspi)
- in matlab, test that everything works: r = raspi("192.168.137.132","pi","raspberry")
- now try: system(r,'export DISPLAY=:0 & ~/.venv/RbController/bin/python3 ~/Rb_Controller/main.py');
	possible errors:
		check that pathes are correct
		check that ~/.venv/RbController/bin/python3 actually points to python3.10.4. If not, run
			cd ~/.venv/RbController/bin
			source activate
			sudo rm python3
			sudo ln -s /usr/local/bin/python3.10 python3
- ADJUST BRIGHTNESS: cd /sys/class/backlight/10-0045/; sudo nano brightness;
- ADJUST BRIGHTNESS2: 
	- pip install rpi-backlight
	- echo 'SUBSYSTEM=="backlight",RUN+="/bin/chmod 666 /sys/class/backlight/10-0045/brightness /sys/class/backlight/10-0045/bl_power"' | sudo tee -a /etc/udev/rules.d/backlight-permissions.rules
	- pip install wheel
	- pip install pygobject

- pip install pathlib and PyInputPlus (for using filemover.py)


* 
*
*
*
*
*

run "python3 --version" to check if version is 3.10. If not, upgrade to 3.10.
run "python3 -m venv ~/Desktop/python_venv" to create virtual environment
run "python3 -m pip install --upgrade pip" to upgrade pip to newest version
run "pip install -r requirements.txt" to install dependencies. This may take some time
when running python scripts from terminal, make sure to activate environment by running 
	"source ~/Desktop/python_venv/bin/activate" 
