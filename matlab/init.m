function [status,r,t] = init

r = raspi('192.168.137.173','pi','raspberry');

%t = tcpserver("192.168.137.1",4000,"ConnectionChangedFcn",@connectionFcn);
t = tcpserver("localhost",4000,"ConnectionChangedFcn",@connectionFcn,"Timeout",10);

%system(r,'~/Desktop/python_venv/bin/python ~/Desktop/Rb_Controller/main_test.py');
system('python C:\Users\leouh\Documents\Rb_Controller\main_test.py &')

status = read(t,5,'string');
if isempty(status)
    status = 'The Raspberry Pi was unable to make the necessary connections. Check the USB ports and try again.';
end


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