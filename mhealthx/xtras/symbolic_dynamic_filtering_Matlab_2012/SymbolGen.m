% Generates the symbole sequence (symData) of a given times series (rawData) using given partition
% Written by Soheil Bahrampour
% August 2012

function symData = SymbolGen(rawData,partition)

partition=[partition inf];
symData=zeros(size(rawData,1),1);
for ii = 1:size(rawData,1)
    for s=1:length(partition)
        if(partition(s)>rawData(ii,1))
            symData(ii,1)=s;
            break
        end        
    end
end


