clear all
t = tcpserver("192.168.137.1",4000,"ConnectionChangedFcn",@connectionFcn);

pause(5)

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