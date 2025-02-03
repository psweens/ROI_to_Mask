clc
clear
close

% Define the folder containing .zip files of ROIs
zip_folder = '/home/sweene01/Dropbox/Code/MATLAB/RSOM/exROI/test/';

% Define the folder where the 3D mask outputs will be saved
output_folder = '/home/sweene01/Dropbox/Code/MATLAB/RSOM/exROI/test_output/';

% Define the total no. of z-slices
z_total = 700;

% Run the function calculate_ROI_volume to iterate through all .zip files in
% 'zip_folder', create 3D binary masks with a total of 'z_total' slices 
% (Z-dimension) and save them to 'output_folder'.
calculate_ROI_volume(zip_folder, output_folder, z_total);
