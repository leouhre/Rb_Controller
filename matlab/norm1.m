%% Renormalize a t r a n s f e r func t i on to 1
% take s a t r a n s f e r func t i on (TF) as input
% returns a TF where the term with the lowe s t potency
% in the denominator i s normalized
function [sys1] = norm1(sy)
    [num,den] = tfdata(sy); % Extract polynomium vectors
    a = 0; % initialize a
    m = size(den{1},2); % get size of denominator polynomial
    for n = m:-1:1 % iterate the denominator
        if a == 0 % as long as the term with
            a = den{1}(n) ; % the lowest potency is zero.
        end
    end
    num1 = num{1}/ a ; % rescale the numerator and
    den1 = den {1}/ a ; % denominator
    sys1 = tf(num1,den1) ; % generate the output transfer function
end