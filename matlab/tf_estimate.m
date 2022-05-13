close all

% Get step response from data file and save in variable 'temp'
fileID = fopen('step_response/sensor0.txt', 'r');
formatSpec = '%f';
sizeA = [1,Inf];
temp = fscanf(fileID,formatSpec,sizeA);
% Use only every 10th sample since fs = 10Hz
temp = temp(1 : 20 : end);
fclose(fileID);

% Create input/output vectors for the tfest() function
% Remember to subtract room temperature, temp(2,1)
u = transpose([zeros(1,length(temp)),15*ones(1,length(temp))]);
y = transpose([zeros(1,length(temp)),temp - temp(1)]);

% Uncomment following to see input/output data
figure(1)
plot(u)
hold on
plot(y)
xlabel('time (s)')
ylabel('temperature (degree C)')
hold off

% Estimate the transfer function for the system (np = number of poles)
data = iddata(y,u,1);
np = 2;
nz = 1;
sys = tfest(data,np,nz);

% To validate the system transfer function, try simulating a 15V response
figure(2)
opt = stepDataOptions('StepAmplitude',15);
step(sys,opt)
hold on
plot(y(length(temp):length(y)))
hold off

% Get numerator and denominator for Simulink model
num = sys.Numerator;
den = sys.Denominator;
G = tf(num,den);

%%

% These are the parameters to play with in order to obtain the optimal
% controller
Ni = 5; 
pm = 60;
alpha = 0.2;
fs = 10;
Ts = 1/fs;

% Calculate the phase shift due to the integrator
rho_i = rad2deg(-atan(1/Ni));
rhom = rad2deg(asin((1-alpha)/(1+alpha)));
rho_G = pm - rho_i - 180;

% Find the crossover frequency of the system to be controlled
%wc = getGainCrossover(G,1);
wc = 1;

% Find the integrator time constant
s = tf('s');
ti = Ni*1/wc;
td = 1/(wc*sqrt(alpha));
CD = tf([td 1], [alpha*td 1]);
%CD = (td*s + 1)/(alpha*td*s + 1);
CI = tf([ti 1],[ti 0]);
%CI = (ti*s + 1)/(ti*s);

% The following lines will automatically find the proportional gain from the bode plot
[mag,phase,wout] = bode(G*CD*CI);
% Shift phase to start at 0 degrees
if phase(1,1,1) > 0
    for i = 1:length(wout)
        phase(1,1,i) = phase(1,1,i) - 360;
    end
end
% Find the index at which the phase shift is equal to rho_G. For a 2 pole/1
% zero system the phase change will never be > 90 degrees. Thus, it is a
% stable system no matter the gain
k = find(abs(phase(1,1,:) - rho_G) < 5, 1, 'first');
if ~isempty(k)    
    % Proportional gain is the inverse of the system gain at index k
    kp = 1/mag(1,1,min(k));
else
    kp = db2mag(20);
end
kp = 13.6772 + 5;
% Set saturation limit
sat_limit = 22;
set_temp = 200 - temp(1);

model='system_model_2';
load_system(model);
open_system(model);

op = [0];
ios(1) = linio(strcat(model,'/kp'),1,'openinput');
ios(2) = linio(strcat(model, '/output'),1,'openoutput');
setlinio(model,ios);
sys2 = linearize(model,ios,op);
[num2,den2] = ss2tf(sys2.A,sys2.B,sys2.C,sys2.D);
Gtotal = minreal(tf(num2, den2));

h = sim(model,1000);
plot(h)