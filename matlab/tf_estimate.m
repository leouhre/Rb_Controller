%% Simulink model name
model='system_model.m';

s=tf('s');

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
%figure(1)
%bode(sys)
%figure(2)
opt = stepDataOptions('StepAmplitude',175);
%step(sys,opt)
%hold on
%plot(temp(2,:) - temp(2,1))
%hold off

num = sys.Numerator;
den = sys.Denominator;
G = tf(num,den);

Ni = 6; % prioritize fast response rather
alpha = 0.05; % than small overshoot
pm = 65;

rhoi = rad2deg(-atan(1/Ni));
rhom = rad2deg(asin((1-alpha)/(1+alpha)));
rhoG = pm - rhoi - 180 - rhom;

% find new crossover freq from bode plot
% bode(G)
wc = getGainCrossover(G,1);

td = 1/(wc*sqrt(alpha));
ti = Ni*1/wc;
CD = (td*s + 1)/(alpha*td*s + 1);
CI = (ti*s + 1)/(ti*s);
CI_num = cell2mat(CI.Numerator);
CI_den = cell2mat(CI.Denominator);

% find Kp2 from bode plot
%bode(Gbal*Kp*CI*CD_bal*CI2_bal);
 %kp = db2mag(30);
kp = 5;

%Gcl_vel = (Gvel2*Kp_vel*CI_vel)/(1 + Gvel2*Kp_vel*CI_vel*CD_vel);


%sys1 = norm1(G);

%figure(3)
%step(kp*G/(1+kp*G),opt)
%hold on
%step(kp*sys1/(1+kp*sys1),opt)