fileID = fopen('step_response/sensor7.txt', 'r');

formatSpec = '%d %f';

sizeA = [2 Inf];

A = fscanf(fileID,formatSpec,sizeA);

fclose(fileID);

x = 17*ones(1,length(A));

data = iddata(A(2,:),x)

tfestimate(x,A(2,:))