% create a Raspberry Pi module
%r = raspi();

% get temperature from user
prompt = "Temperature?\n";

T = string(input(prompt));

% run Python script on Raspberry Pi creating data.txt
%system(r,'python3 ~/Desktop/Rb_Controller/pid_Test.py ' + T)
system('python3 pid_Test.py ' + T)
