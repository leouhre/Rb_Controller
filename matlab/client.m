t = tcpclient('localhost', 50000);
data = uint8(1:10);
write(t,data)
read(t,char)
