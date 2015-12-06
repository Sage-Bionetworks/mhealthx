% Written by Soheil Bahrampour
% August 2012

function feature = FeatureExtractionSDF(data, partition, numSymbol, PiMatrixFlag)

stateProbVecStore = zeros(numSymbol,size(data,2));
featureAsVectorizedMorphMatrix = zeros(numSymbol*numSymbol,size(data,2));

for ii=1:size(data,2)
    symbolSeq = SymbolGen(data(:,ii),partition);  % symbole generation
    [morphMatrix,PVec] = AnalyzeSymbolSeq(symbolSeq', numSymbol, PiMatrixFlag); % morphMatrix is the estimated Morph Matrix, Pvec is the eigenvector corresponding to the eigenvalue 1
    if ~PiMatrixFlag
        stateProbVecStore(:,ii) = PVec;
    else
        b = morphMatrix';
        b = b(:);
        featureAsVectorizedMorphMatrix(:,ii) = b;
    end
end

if ~PiMatrixFlag
    feature = stateProbVecStore;
else
    feature = featureAsVectorizedMorphMatrix;
end
