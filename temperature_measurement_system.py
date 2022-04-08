# Import functionality of RTD measurement device
# import lucidIo
from lucidIo.LucidControlRT8 import LucidControlRT8
from lucidIo.Values import ValueTMS2
from lucidIo.Values import ValueTMS4
from lucidIo import IoReturn

print("Connecting to /dev/ttyACM", end="")
for x in range(2):
	print(str(x) + "...")
	rt8 = LucidControlRT8('/dev/ttyACM' + str(x))

	try:
		if (rt8.open() == False):
			print('LucidControl device not found at port ' + str(x))
			rt8.close()
			print("Connecting to /dev/ttyACM", end="")
		else:
			# Identify device
			ret = rt8.identify(0)
			if ret == IoReturn.IoReturn.IO_RETURN_OK:
				print('Device Class: ' + str(rt8.getDeviceClassName()))
				print('Device Type: ' + str(rt8.getDeviceTypeName()))
				#print('Serial No.: ' + str(rt8.getDeviceSnr()))
				#print('Firmware Rev.: ' + str(rt8.getRevisionFw()))
				#print('Hardware Rev.: ' + str(rt8.getRevisionHw()))
				print('Successfully connected to port ' + str(rt8.portName))
				break
			else:
				print('Identify Error')
				rt8.close()
				if x < 1:
					print("Connecting to /dev/ttyACM", end="")
				else:	
					print('Try re-inserting the USB cable')
					exit()
	except:
		print('LucidControl device not found at port ' + str(x))
		rt8.close()
		if x < 1:
			print("Connecting to /dev/ttyACM", end="")
		#print('Identify Error')
		#rt8.close()
		else:
			print('Try re-inserting the USB cable')
			exit()