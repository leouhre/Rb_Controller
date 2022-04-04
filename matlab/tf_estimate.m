load('step_response/sensor5.txt');

%fileID = fopen('step_response/sensor7.txt', 'r');

%formatSpec = '%d %f';

%sizeA = [2 Inf];

%A = fscanf(fileID,formatSpec,sizeA);

%fclose(fileID);

x = zeros(length(sensor5),1);

x = (zeros(length(sensor5),1),17*ones(length(sensor5),1));

A = [ones(length(sensor5),1)*sensor5(1,2),sensor5(:,2)];

data = iddata(sensor5(:,2),x,1);

tfestimate(x,A(2,:))