clear all

% Get step response from data file and save in variable 'temp'
fileID = fopen('step_response/sensor5.txt', 'r');
formatSpec = '%d %f';
sizeA = [2 Inf];
temp = fscanf(fileID,formatSpec,sizeA);
fclose(fileID);

% Create input/output vectors for the tfest function
% Remember to subtract room temperature temp(2,1)
u = transpose([zeros(1,length(temp)),17*ones(1,length(temp))]);
y = transpose([zeros(1,length(temp)),temp(2,:) - temp(2,1)]);

% Estimate the transfer function for the system (np = number of poles)
data = iddata(y,u,1);
np = 6;
sys = tfest(data,np);
figure(1)
bode(sys)
figure(2)
opt = stepDataOptions('StepAmplitude',17);
step(sys,opt)
%hold on
%plot(temp(2,:) - temp(2,1))
%hold off
