clear all
close all
count = 0;
file_id = "time.txt";
f = fopen(file_id);
while ~feof(f) 
    fgetl(f);
    count = count + 1;
end
fclose(f);
f = fopen(file_id);
n = count;
time = zeros(1,n);
for i = 1:n
    time(i) = str2double(fgetl(f));
end
time(1) = 0;
fclose(f);
data = cell(8,n);
for i = 1:9
    count = 1;
    file_id = strcat(sprintf("sensor%d.txt",i-1));
    f = fopen(file_id);
    while ~feof(f) 
        data{i,count} = str2double(fgetl(f));
        count = count + 1;
    end
    fclose(f);
end
temps = cell2mat(data);
figure(1)
hold on
colors = ["blue" "blue" "red" "red" "green" "green" "magenta" "magenta"];
for i = 1:9
    if i < 9
        plot(time,temps(i,:),'DisplayName',sprintf("sensor%d",i-1),color=colors(i))
    else
        plot(time,temps(i,:),'DisplayName',"average",color="black")
    end
end
ylim([155 205])
xlim([120 1200])
grid on
xlabel("time [s]");
ylabel("temperature [°C]");
legend('Location','southeast')