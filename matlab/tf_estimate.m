fileID = fopen('/step_response/sensor6.txt', 'r');

formatSpec = '%d %f';

sizeA = [2 Inf];

A = fscanf(fileID,formatSpec,sizeA)

