t = tcpclient('169.254.45.126', 50000);
data = uint8(1:10);
write(t,data)
clear t;
