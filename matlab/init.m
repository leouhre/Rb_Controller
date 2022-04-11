function [status] = init

r = raspi('192.168.137.173','pi','raspberry');

%t = tcpserver("192.168.137.1",4000,"ConnectionChangedFcn",@connectionFcn);
t = tcpserver("localhost",4000,"ConnectionChangedFcn",@connectionFcn,"Timeout",10);

system(r,'python ~/Desktop/Rb_Controller/main_test.py &')

status = read(t,6,'string');

% Run while loop until message is recieved from RPi
%data = '';
%while ~strcmp(data,'success')
%    while 1
%        nBytes = t.NumBytesAvailable;
%        if nBytes > 0
%            break;
%        end
%    end
%    data = read(t,nBytes,'string');
    %disp(data)
%    status = data;
%end