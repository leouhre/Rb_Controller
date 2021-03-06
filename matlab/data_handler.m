clear all
[temps, time, voltage] = data_loader('C:\Users\leouh\Documents\DTU\6th_semester\Rb_cell\collect_data\180_pid_2\data\');

temps{5} = temps{1};
for k = 1:length(temps{2})
    temps{5}(k) = (temps{5}(k) + temps{2}(k))/2; 
end

figure()
plot(time, temps{5}, 'LineWidth', 1.5)
hold on
plot(time, temps{1}, 'LineWidth', 1.5)
plot(time, temps{2}, 'LineWidth', 1.5)
plot(time, temps{3}, 'LineWidth', 1.5)
plot(time, temps{4}, 'LineWidth', 1.5)
legend('avg', 'left glass', 'right glass', 'mid heater', 'outer heater', 'Location', 'southeast');

figure()
plot(time, voltage, 'LineWidth', 1.5)