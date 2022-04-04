%% Simulink model name
model='system_model.m';

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
np = 4;
sys = tfest(data,np);
figure(1)
bode(sys)
figure(2)
opt = stepDataOptions('StepAmplitude',175);
step(sys,opt)
%hold on
%plot(temp(2,:) - temp(2,1))
%hold off

num = sys.Numerator;
den = sys.Denominator;
G = tf(num,den);
kp = 1;

Ni_vel = 6; % prioritize fast response rather
alpha_vel = 0.05; % than small overshoot
pm_vel = 65;

rhoi_vel = rad2deg(-atan(1/Ni_vel));
rhom_vel = rad2deg(asin((1-alpha_vel)/(1+alpha_vel)));
rhoG_vel = pm_vel - rhoi_vel - 180 - rhom_vel;

% find new crossover freq from bode plot
bode(Gbal*Kp*CI)
%wc_vel = 3.7;

%td_vel = 1/(wc_vel*sqrt(alpha_vel));
%ti_vel = Ni_vel*1/wc_vel;
%CD_vel = (td_vel*s + 1)/(alpha_vel*td_vel*s + 1);
%CI_vel = (ti_vel*s + 1)/(ti_vel*s);

% find Kp2 from bode plot
%bode(Gbal*Kp*CI*CD_bal*CI2_bal);
%Kp_vel = 1/db2mag(12);

%Gcl_vel = (Gvel2*Kp_vel*CI_vel)/(1 + Gvel2*Kp_vel*CI_vel*CD_vel);


%sys1 = norm1(G);

%figure(3)
%step(kp*G/(1+kp*G),opt)
%hold on
%step(kp*sys1/(1+kp*sys1),opt)