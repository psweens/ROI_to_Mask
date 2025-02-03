function calculate_ROI_volume(roi_path, outputdir, totalZSlices)
    % calculate_ROI_volume:
    % Reads *.zip files in "roi_path"; each zip can contain multiple ROIs.
    % Each ROI's name starts with 4 digits indicating the slice index
    % (e.g. "0010-..." => slice 10). 
    % Builds a 3D mask [600 x 600 x totalZSlices], writes it out as a 
    % multi-page TIFF, and computes total ROI volume.
    %
    % Usage:
    %   calculate_ROI_volume('path/to/zips', 'path/to/output', 50)
    %
    % Inputs:
    %   roi_path     - folder containing .zip files of ROIs
    %   outputdir    - folder to which 3D TIFFs and volumes are written
    %   totalZSlices - total number of Z-slices in the original image stack
    
    % ---------------------------------------------------------------------
    % 1) Get list of .zip files and ensure output directory exists
    % ---------------------------------------------------------------------
    files = dir(fullfile(roi_path, '*.zip'));
    if ~exist(outputdir, 'dir')
        mkdir(outputdir);
    end
    
    % ---------------------------------------------------------------------
    % 2) Define voxel volume if desired (example: 20um x 20um x 4um in mm^3)
    % ---------------------------------------------------------------------
    voxelVolume_mm3 = 20 * 20 * 4 * 1e-9;  % (um^3 -> mm^3)
    
    % ---------------------------------------------------------------------
    % 3) Loop through each .zip file in the folder
    % ---------------------------------------------------------------------
    for i = 1:length(files)
        % Full path to the current zip
        ROIaddress = fullfile(roi_path, files(i).name);
        
        % Read all .roi entries from this zip
        sROI = ReadImageJROI(ROIaddress);

        % Pre-allocate a 3D stack of [600 x 600 x totalZSlices]
        binStack = false(600, 600, totalZSlices);

        % We'll count total pixels to compute volume
        totalPixels = 0;

        % -----------------------------------------------------------------
        % 4) Process each ROI in the zip
        % -----------------------------------------------------------------
        for j = 1:numel(sROI)
            % Check if it’s a polygon ROI with coordinates
            if isfield(sROI{j}, 'mnCoordinates') && isfield(sROI{j}, 'strName')
                % Parse the Z-slice index from the first 4 chars of the ROI name
                roiName = sROI{j}.strName;  % e.g. "0010-anything"
                if length(roiName) >= 4
                    sliceIndex = str2double(roiName(1:4));
                else
                    sliceIndex = NaN;
                end
                
                % Only proceed if we have a valid slice index in [1, totalZSlices]
                if ~isnan(sliceIndex) && sliceIndex >= 1 && sliceIndex <= totalZSlices
                    % Create a 2D mask from the ROI polygon
                    xCoords = sROI{j}.mnCoordinates(:,1);
                    yCoords = sROI{j}.mnCoordinates(:,2);
                    binmask = poly2mask(xCoords, yCoords, 600, 600);

                    % Accumulate pixel count
                    totalPixels = totalPixels + sum(binmask(:));
                    
                    % Place into the 3D stack at the correct Z-slice (logical OR)
                    binStack(:,:,sliceIndex) = binStack(:,:,sliceIndex) | binmask;
                end
            end
        end

        % -----------------------------------------------------------------
        % 5) Compute volume (pixels × voxel volume)
        % -----------------------------------------------------------------
        volume_mm3 = totalPixels * voxelVolume_mm3;

        % -----------------------------------------------------------------
        % 6) Clean file name (optional) + display volume
        % -----------------------------------------------------------------
        cleanFileName = strrep(files(i).name, 'RoiSet_', '');
        cleanFileName = strrep(cleanFileName, '.zip', '');
        cleanFileName = strrep(cleanFileName, 'selection3D', 'ROI');
        
        disp([cleanFileName, ', Volume (mm^3) = ', num2str(volume_mm3)]);

        % -----------------------------------------------------------------
        % 7) Write out the 3D stack as a multi-page TIFF
        % -----------------------------------------------------------------
        outTiffPath = fullfile(outputdir, [cleanFileName '.tiff']);
        
        for z = 1:totalZSlices
            if z == 1
                % Overwrite (or create) the file on the first slice
                imwrite(binStack(:,:,z), outTiffPath, 'tiff', 'Compression', 'none');
            else
                % Append subsequent slices
                imwrite(binStack(:,:,z), outTiffPath, 'tiff', ...
                        'Compression', 'none', 'WriteMode', 'append');
            end
        end
        
        % Optionally confirm the file was written
        %fprintf('Saved 3D mask to: %s\n', outTiffPath);
    end

    % Done with all .zip files
end
