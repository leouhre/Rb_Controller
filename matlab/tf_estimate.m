close all
clear all

step_amplitude = 2.5; %V
fs = 2; %Hz
Ts = 1/fs; %s

% Get step response from data file and save in variable 'temp'
fileID = fopen('step_response/sensor0.txt', 'r');
formatSpec = '%f';
sizeA = [1,Inf];
temp_at_heater = fscanf(fileID,formatSpec,sizeA);
fclose(fileID);

% Get step response from data file and save in variable 'temp'
fileID = fopen('step_response/sensor1.txt', 'r');
formatSpec = '%f';
sizeA = [1,Inf];
temp_solo = fscanf(fileID,formatSpec,sizeA);
fclose(fileID);


for i = 1:min(length(temp_at_heater),length(temp_solo))
    temp(i) = (temp_at_heater(i) + temp_solo(i))/2;
end

% Create input/output vectors for the tfest() function
% Remember to subtract room temperature (min(temp))
u = transpose([zeros(1,length(temp)),step_amplitude*ones(1,length(temp))]);
y = transpose([zeros(1,length(temp)),temp - temp(1)]);

% Uncomment following to see input/output data
figure(1)
plot(u)
hold on
plot(y)
xlabel('time (s)')
ylabel('temperature (degree C)')
hold off

% Estimate the transfer function for the system
% Set sample period Ts for iddata()
data = iddata(y,u,Ts);
np = 3;
nz = 1;
s = tf('s');
sys = tfest(data,np,nz);
%sys2 = (-1/db2mag(60.1-16.5))*((s-0.1228)*(s+0.0011))/((s+0.006)*(s+0.0372)*(s+0.0006))
%sys2 = tfest(data,3,1);
%sys3 = tfest(data,3,2);

% To validate the system transfer function, try simulating a 15V response
figure(2)
opt = stepDataOptions('StepAmplitude',step_amplitude);
step(sys,opt)
hold on
%step(sys2,opt)
%step(sys3,opt)
plot(downsample(y(length(temp):length(y)),fs))
xlim([0 length(temp)/2 + 100])
legend('Estimated system', 'Measured data')
%legend('2 poles, 1 zero', '3 poles, 1 zeros', '3 poles, 2 zeros', 'Measured data')
hold off
%%

% Get numerator and denominator for Simulink model
num = sys.Numerator;
den = sys.Denominator;
G = tf(num,den);

% These are the parameters to play with in order to obtain the optimal
% controller
Ni = 5; 
pm = 65;
alpha = 0.8;

D_active = 1; % PI-Lead controller
%D_active = 0; % PI controller
I_active = 1; % PI controller
%I_active = 0; % P controller

% Calculate the negative phase contribution at the new crossover frequency 
% due to the integrator as well as the positive contribution from the 
% differentiator. Finally, calculate the phase shift at which the new 
% crossover frequency is placed. 
rho_i = rad2deg(-atan(1/Ni));
if D_active == 1
    rho_m = rad2deg(asin((1-alpha)/(1+alpha)));
else
    rho_m = 0;
end
rho_G = pm - rho_i - rho_m - 180;

% Find the new crossover frequency. Since the system contains 2 poles and 1
% zero, a phase shift equal to rho_G is never reached. The Ni value might 
% be chosen to be < 1 to obtain a larger phase shift contribution from 
% the integrator, or a desired crossover frequency can be chosen, since
% the system won't be unstable (in theory) for any frequencies. 
%wc = 3; % PI-Lead and PI controller
%wc = 9; % P controller
[mag0,phase0,wout0] = bode(sys);
k0 = find(phase0(:) > rho_G, 1, 'last');
wc = wout0(k0);

% Find the time constants of the controllers and define the transfer
% functions of the controller parts
ti = Ni*1/wc;
td = 1/(wc*sqrt(alpha));

%%

CD = tf([td 1], [alpha*td 1]);
%CD = (td*s + 1)/(alpha*td*s + 1);
%CD = td*s + 1;
CI = tf([ti 1],[ti 0]);
%CI = (ti*s + 1)/(ti*s);

% The following lines will automatically find the proportional gain from 
% the bode plot of the open loop controller. Test with "wout(k)" to see
% that the gain found is actually at f = wc. Otherwise inspect "wout" to
% see if the margin of the find() command should be smaller/larger.
%[mag,phase,wout] = bode(G*CD*CI,{wc/10,10*wc}); % PI-Lead controller
[mag,phase,wout] = bode(G*CI,{wc/10,10*wc}); % PI controller
k = find(wout < wc, 1, 'last');
kp = 1/mag(k)
ki = kp/ti
kd = kp*td

%%
if D_active == 1
    G_ol = kp*G*CD; % PI-Lead controller
    %G_cl = kp*G*CD*CI/(1+kp*G*CD*CI); % PI-Lead controller
else
    G_ol = kp*G;
end
if I_active == 1
    G_ol = G_ol*CI; % PI-controller
    %G_cl = kp*G*CI/(1+kp*G*CI); % PI controller
end
G_cl = G_ol/(1 + G_ol);


%% Assessment

% For the simulation step input
set_temp = 180;
model='system_model_2';

figure(3)
step(G_cl)
figure(4)
bode(G,CI,CD,{0.001,1})
hold on
margin(G_ol,{0.001,1})
legend()
title("Bode plot of PI controller");
grid on
hold off

h = sim(model,3000);
plot(h)

%load_system(model);
%open_system(model);

%op = [0];
%ios(1) = linio(strcat(model,'/kp'),1,'openinput');
%ios(2) = linio(strcat(model, '/output'),1,'openoutput');
%setlinio(model,ios);
%sys2 = linearize(model,ios,op);
%[num2,den2] = ss2tf(sys2.A,sys2.B,sys2.C,sys2.D);
%Gtotal = minreal(tf(num2, den2));
