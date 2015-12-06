% Performs maximum entropy partitioning on a given data
% Written by Soheil Bahrampour
% August 2012

function partition = maxEntropyPartition(data,numSymbol)
x = sort(data);
k = max(size(x));
partition = zeros(1, numSymbol-1);
for i=1:numSymbol-1
    partition(1,i) = x(floor(i*k/numSymbol));
end
