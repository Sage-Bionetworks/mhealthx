% Written by Soheil Bahrampour
% August 2012

function partition = PartitionGeneration(partitionData,numSymbol)

[m,n] = size(partitionData);
data = reshape(partitionData,m*n,1);  %change into long vector
partition = maxEntropyPartition(data,numSymbol);

