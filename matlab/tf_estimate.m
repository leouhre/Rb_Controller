% Get step response from data file and save in variable 'temp'
fileID = fopen('step_response/sensor5.txt', 'r');
formatSpec = '%d %f';
sizeA = [2 Inf];
temp = fscanf(fileID,formatSpec,sizeA);
fclose(fileID);

% Create input/output vectors for the tfest() function
% Remember to subtract room temperature, temp(2,1)
u = transpose([zeros(1,length(temp)),17*ones(1,length(temp))]);
y = transpose([zeros(1,length(temp)),temp(2,:) - temp(2,1)]);

% Uncomment following to see input/output data
%figure(1)
%plot(u)
%hold on
%plot(y)
%xlabel('time (s)')
%ylabel('temperature (degree C)')

% Estimate the transfer function for the system (np = number of poles)
data = iddata(y,u,1);
np = 2;
nz = 0;
sys = tfest(data,np,nz);

% To validate the system transfer function, try simulating a 17V response
%figure(2)
%opt = stepDataOptions('StepAmplitude',17);
%step(sys,opt)
%hold on
%plot(y(length(temp):length(y)))

% Get numerator and denominator for Simulink model
num = sys.Numerator;
den = sys.Denominator;
G = tf(num,den);

% These are the parameters to play with in order to obtain the optimal
% controller
Ni = 11; 
pm = 50;

% Calculate the phase shift due to the integrator
rho_i = rad2deg(-atan(1/Ni));
rho_G = pm - rho_i - 180;

% Find the crossover frequency of the system to be controlled
wc = getGainCrossover(G,1);

% Find the integrator time constant
ti = Ni*1/wc;

% The following lines will automatically find the proportional gain from the bode plot
[mag,phase,wout] = bode(G);
% Shift phase to start at 0 degrees
if phase(1,1,1) > 0
    for i = 1:length(wout)
        phase(1,1,i) = phase(1,1,i) - 360;
    end
end
% Find the index at which the phase shift is equal to rho_G
k = find(abs(phase(1,1,:) - rho_G) < 5, 1, 'first');
% Proportional gain is the inverse of the system gain at index k
kp = 1/mag(1,1,min(k));
% Set saturation limit
sat_limit = 22;
set_temp = 200 - temp(2,1);

model='system_model.slx';
h = sim(model,1000);

