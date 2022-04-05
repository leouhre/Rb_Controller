% Create a Raspberry Pi module
%r = raspi(raspberrypi,pi,raspberry);

% Get temperature from user
prompt = "Temperature?\n";

T = string(input(prompt));

% Run Python script on Raspberry Pi creating data.txt
%system(r,'python3 ~/Desktop/Rb_Controller/pid_Test.py ' + T)
system('python3 pid_Test.py ' + T)

input("good?");