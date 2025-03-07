import os
import imagej
import numpy as np
from zipfile import ZipFile
from jpype import JClass, JString

# ----------------------------
# Configuration / Folder Paths
# ----------------------------
tiff_folder = "/path/to/your/tiffs"
roi_folder  = "/path/to/your/rois"
output_folder = "/path/to/save/masks"

# Predefined voxel volume (e.g., for voxel size 20x20x20 in mm, here converted to mm³)
voxel_volume = 20 * 20 * 20 * 1e-9  # mm^3

# ----------------------------
# Initialize ImageJ in headless mode
# ----------------------------
ij = imagej.init("sc.fiji:fiji", mode="headless")

# ----------------------------
# Define helper function to load ROIs from a ZIP file
# ----------------------------
RoiDecoder = JClass("ij.io.RoiDecoder")

def load_rois_from_zip(roi_zip_path):
    """
    Reads all ROI files from the given zip archive and decodes them using ImageJ's RoiDecoder.
    Returns a list of ROI objects.
    """
    rois = []
    with ZipFile(roi_zip_path, 'r') as zip_ref:
        for roi_filename in zip_ref.namelist():
            data = zip_ref.read(roi_filename)
            decoder = RoiDecoder(data, JString(roi_filename))
            roi = decoder.getRoi()
            if roi is not None:
                rois.append(roi)
    return rois

# ----------------------------
# Collect results for CSV-like output
# ----------------------------
results_summary = []

# ----------------------------
# Process each TIFF file in alphabetical order
# ----------------------------
tiff_files = sorted([f for f in os.listdir(tiff_folder) if f.lower().endswith((".tif", ".tiff"))])
for filename in tiff_files:
    image_path = os.path.join(tiff_folder, filename)
    base_name = os.path.splitext(filename)[0]
    roi_zip_path = os.path.join(roi_folder, base_name + ".zip")

    if not os.path.exists(roi_zip_path):
        print(f"ROI file not found for image '{filename}', skipping.")
        continue

    # Load the 3D TIFF image and create an empty binary mask.
    imp = ij.io().open(image_path)
    img = ij.py.from_java(imp)  # Expected shape: (slices, height, width)
    mask = np.zeros_like(img, dtype=np.uint8)

    # Load the ROIs from the ZIP file.
    rois = load_rois_from_zip(roi_zip_path)
    print(f"Processing '{filename}': {len(rois)} ROI(s) found.")

    # Process each ROI.
    for roi in rois:
        # Get the slice index (default to 1 if not provided)
        try:
            slice_index = roi.getPosition()  # Expected to be 1-indexed.
        except AttributeError:
            slice_index = 1
        z = slice_index - 1  # Convert to 0-index.
        if z < 0 or z >= mask.shape[0]:
            # If the ROI slice is outside the image, skip it.
            continue

        # Get the bounding rectangle of the ROI.
        bounds = roi.getBounds()
        x0, y0, w, h = bounds.x, bounds.y, bounds.width, bounds.height

        # Get the ROI mask from the ROI (a ByteProcessor).
        ip = roi.getMask()
        if ip is None:
            # For some ROI types (like point ROIs), skip if no mask is available.
            continue

        # Manually convert the ByteProcessor to a NumPy array.
        # The mask is of shape (h, w)
        roi_mask_2d = np.array(ip.getPixels(), dtype=np.uint8).reshape((h, w))

        # Get the corresponding image slice.
        mask_slice = mask[z]
        img_h, img_w = mask_slice.shape

        # Clip the ROI bounding box to the image boundaries.
        start_x = max(x0, 0)
        start_y = max(y0, 0)
        end_x = min(x0 + w, img_w)
        end_y = min(y0 + h, img_h)
        if start_x >= end_x or start_y >= end_y:
            # ROI is completely outside the image.
            continue

        # Compute the offsets into the ROI mask.
        offset_x = start_x - x0
        offset_y = start_y - y0
        roi_clip_w = end_x - start_x
        roi_clip_h = end_y - start_y

        # Extract the corresponding region from the ROI mask.
        roi_mask_cropped = roi_mask_2d[offset_y:offset_y+roi_clip_h, offset_x:offset_x+roi_clip_w]

        # Insert the ROI mask into the corresponding region of the image mask.
        submask = mask_slice[start_y:end_y, start_x:end_x]
        submask[roi_mask_cropped > 0] = 255
        mask_slice[start_y:end_y, start_x:end_x] = submask

    # Save the binary mask image.
    mask_save_path = os.path.join(output_folder, base_name + "_mask.tif")
    mask_imp = ij.py.to_java(mask)
    ij.io().save(mask_imp, mask_save_path)

    # Calculate the segmented volume.
    segmented_voxel_count = np.sum(mask > 0)
    segmented_volume = segmented_voxel_count * voxel_volume

    results_summary.append((filename, segmented_volume))
    print(f"Processed '{filename}': Segmented volume = {segmented_volume}")

# Print CSV-formatted summary.
print("\nCSV Summary (filename,segmented_volume):")
print("filename,segmented_volume")
for fname, vol in results_summary:
    print(f"{fname},{vol}")
