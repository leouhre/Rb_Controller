function [temps, time, voltage] = data_loader(path)

temps = cell(5,1);

% Get step response from data file and save in variable 'temp'
for i = 1:4
    fileID = fopen([path, 'sensor', char(string(i - 1)), '.txt'], 'r');
    formatSpec = '%f';
    sizeA = [1,Inf];
    temps{i} = fscanf(fileID,formatSpec,sizeA);
end

fileID = fopen([path, 'time.txt'], 'r');
time = fscanf(fileID,formatSpec,sizeA);

fileID = fopen([path, 'voltage.txt'], 'r');
voltage = fscanf(fileID,formatSpec,sizeA);