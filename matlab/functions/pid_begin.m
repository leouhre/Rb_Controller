function [outputArg1,outputArg2] = pid_begin(inputArg1,inputArg2)
%PID_BEGIN Summary of this function goes here
%   Detailed explanation goes here

system(r,'python ~/Desktop/Rb_Controller/calibrate.py')

outputArg1 = inputArg1;
outputArg2 = inputArg2;
end

