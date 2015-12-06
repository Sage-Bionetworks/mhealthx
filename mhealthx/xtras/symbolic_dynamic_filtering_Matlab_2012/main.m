% main function for SDF Feature Extraction
% Written by Soheil Bahrampour
% August 2012

clc
clear all
close all

%% Parameters 
numSymbol = 10;
morphMatrixFlag = 0; %if 1, use vectorized version of Morph matrix as a long feature vector; else use the eigenvector of Morph Matrix corresponding to eigenvalue 1

%% load Data which consists of trainData and testData
% Each column contains a time-series. 
load Data

%% Feature Extraction
%Partition Generation based on Maximum Entropy
partition = PartitionGeneration(trainData,numSymbol);

% Feature Extraction using SDF
% Each column contains the extracted features for the corresponding time-series
featuresTrain = FeatureExtractionSDF(trainData, partition, numSymbol, morphMatrixFlag);
featuresTest = FeatureExtractionSDF(testData, partition, numSymbol, morphMatrixFlag);

