% Estimates the Morph matrix and its eigenvector corresponding to eigenvalue 1 by counting
% Written by Soheil Bahrampour
% August 2012

function [morphMatrix, PVec] = AnalyzeSymbolSeq(symbolSeq,numStates,morphMatrixFlag)

morphMatrix = zeros(numStates,numStates);
PVec = zeros(1,numStates);

for jj = 1:size(symbolSeq,2)-1
    PVec(symbolSeq(1,jj))=1+PVec(symbolSeq(1,jj));
    if (morphMatrixFlag)
        morphMatrix(symbolSeq(1,jj+1),symbolSeq(1,jj))=1+morphMatrix(symbolSeq(1,jj+1),symbolSeq(1,jj));
    end
end


PVec = PVec/sum(PVec);  % normalizing the computed vector

%normalize each row of Matrix to make it a stochastic matrix
if (morphMatrixFlag)
    for i=1:numStates
        rowSum = sum(morphMatrix(i,:));
        if(rowSum==0)
            morphMatrix(i,:) = PVec;
        else
            morphMatrix(i,:) = morphMatrix(i,:)/rowSum;     
        end
    end
end





