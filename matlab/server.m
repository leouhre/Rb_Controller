clear all

r = raspi('169.254.45.126','pi','raspberry');

%t = tcpserver("192.168.137.1",4000,"ConnectionChangedFcn",@connectionFcn);
t = tcpserver("localhost",4000,"ConnectionChangedFcn",@connectionFcn);

system(r,'python3 ~/Desktop/Rb_Controller/client.py &')

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
    disp(data)
end