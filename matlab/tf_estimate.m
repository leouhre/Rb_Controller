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
%figure(1)
%plot(u)
%hold on
%plot(y)
%xlabel('time (s)')
%ylabel('temperature (degree C)')
%hold off

% Estimate the transfer function for the system (np = number of poles)
data = iddata(y,u,1);
np = 2;
nz = 1;
sys = tfest(data,np,nz);
%sys2 = tfest(data,1,0);
%sys3 = tfest(data,2,0);

% To validate the system transfer function, try simulating a 15V response
%figure(2)
%opt = stepDataOptions('StepAmplitude',15);
%step(sys,opt)
%hold on
%step(sys2,opt)
%step(sys3,opt)
%plot(y(length(temp):length(y)))
%legend('2 poles, 1 zero', '1 pole, 0 zeros', '2 poles, 0 zeros', 'Measured data')
%hold off
%%

% Get numerator and denominator for Simulink model
num = sys.Numerator;
den = sys.Denominator;
G = tf(num,den);

% These are the parameters to play with in order to obtain the optimal
% controller
Ni = 10; 
pm = 50;
alpha = 0.1;
fs = 3;
Ts = 1/fs;

% Calculate the negative phase contribution at the new crossover frequency 
% due to the integrator as well as the positive contribution from the 
% differentiator. Finally, calculate the phase shift at which the new 
% crossover frequency is placed. 
rho_i = rad2deg(-atan(1/Ni));
rho_m = rad2deg(asin((1-alpha)/(1+alpha)));
rho_G = pm - rho_i - rho_m - 180;

% Find the new crossover frequency. Since the system contains 2 poles and 1
% zero, a phase shift equal to rho_G is never reached. The Ni value might 
% be chosen to be < 1 to obtain a larger phase shift contribution from 
% the integrator, or a desired crossover frequency can be chosen, since
% the system won't be unstable (in theory) for any frequencies. 
wc = 3; % PI-Lead and PI controller
%wc = 9; % P controller

% Find the time constants of the controllers and define the transfer
% functions of the controller parts
s = tf('s');
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
%[mag,phase,wout] = bode(G*CD*CI,{0.01,30}); % PI-Lead controller
[mag,phase,wout] = bode(G*CI,{0.01,30}); % PI controller
k = find(abs(wout(:) - wc) < 0.2, 1, 'first');
kp = 1/mag(1,1,k);
%D_active = 1; % PI-Lead controller
D_active = 0; % PI controller
I_active = 1; % PI controller
%I_active = 0; % P controller
if D_active == 1
    G_ol = kp*G*CI*CD; % PI-Lead controller
    G_cl = kp*G*CD*CI/(1+kp*G*CD*CI); % PI-Lead controller
else  
    G_ol = kp*G*CI; % PI-controller
    G_cl = kp*G*CI/(1+kp*G*CI); % PI controller
end

%% Assessment

% For the simulation step input
set_temp = 200 - temp(1);
model='system_model_2';

figure()
step(G_cl)
figure()
bode(G,CI,CD,{0.01,10})
hold on
margin(G_ol,{0.01,10})
legend()
title("Bode plot of PI controller");
grid on
hold off

h = sim(model,1000);
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

% Find the index at which the phase shift is equal to rho_G. For a 2 pole/1
% zero system the phase change will never be > 90 degrees. Thus, it is a
% stable system no matter the gain
%k = find(abs(phase(1,1,:) - rho_G) < 5, 1, 'first');
%if ~isempty(k)    
    % Proportional gain is the inverse of the system gain at index k
%    kp = 1/mag(1,1,min(k));
%else
%    kp = db2mag(20);
%end
%kp = db2mag(-24);