function [sys1] = norm1(sy)
    [num,den] = tfdata(sy);
    a = 0;
    m = size(den{1},2);
    for n = m: -1:1
        if a == 0
            a = den{1}(n);
        end
    end
    num1 = num{1}/a;
    den1 = den{1}/a;
    sys1 = tf(num1,den1);
end