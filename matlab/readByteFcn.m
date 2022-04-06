function readByteFcn(src,~)
data = read(src,src.NumBytesAvailable);
disp(data)
end