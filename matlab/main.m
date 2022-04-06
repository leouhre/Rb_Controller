% Create a Raspberry Pi module
r = raspi();

t = tcpserver("192.168.137.1",4000,"ConnectionChangedFcn",@connectionFcn);

% Get temperature from user
prompt = "Temperature?\n";

T = string(input(prompt));

% Run Python script on Raspberry Pi creating data.txt
system(r,'python3 ~/Desktop/Rb_Controller/pid_Test.py ' + T)

% Run while loop until message is recieved from RPi
data = '';
while ~strcmp(data,'ready')    
    while 1
        nBytes = t.NumBytesAvailable;
        if nBytes > 0
            break;
        end
    end
    data = read(t,nBytes,'string');
end

%continue script...