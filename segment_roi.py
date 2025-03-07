import imagej
import numpy as np

# Initialize ImageJ using the Fiji distribution.
ij = imagej.init('sc.fiji:fiji')

# ----------------------------
# Configuration / File Paths
# ----------------------------
image_path = "path/to/your/image.tif"       # Update with your 3D TIFF image path.
roi_zip_path = "path/to/your/rois.zip"        # Update with your ROI .zip file path.
mask_save_path = "path/to/your/output_mask.tif"  # Update with your desired output path.

# Define the voxel volume (in cubic units, e.g., if voxel is 1x1x1, then volume = 1.0)
voxel_volume = 1.0

# ----------------------------
# Step 1. Load the 3D TIFF image
# ----------------------------
imp = ij.io().open(image_path)
img = ij.py.from_java(imp)  # Expecting an array with shape (slices, height, width)
print("Image shape:", img.shape)

# Create an empty binary mask (0: background, 255: ROI)
mask = np.zeros_like(img, dtype=np.uint8)

# ----------------------------
# Step 2. Load the 3D ROI .zip file using ROI Manager
# ----------------------------
# Open the ROI Manager window.
ij.IJ.run("ROI Manager...", "")

# Get the ROI Manager instance.
rm = ij.plugin.frame.RoiManager.getInstance()
if rm is None:
    raise RuntimeError("ROI Manager instance could not be obtained.")

# Load the ROI zip file.
rm.runCommand("Open", roi_zip_path)
rois = rm.getRoisAsArray()
print("Number of ROIs loaded:", len(rois))

# ----------------------------
# Step 3. Create a 3D binary mask from the ROIs.
# ----------------------------
# For each ROI, determine its slice and draw it on the mask.
for roi in rois:
    # Determine the slice index. This example assumes that each ROI’s getPosition() method 
    # returns a 1-indexed slice number.
    try:
        slice_index = roi.getPosition()
    except AttributeError:
        slice_index = 1  # Fallback: assign to first slice if no position info available.
    z = slice_index - 1  # Convert to 0-indexed.

    # Get the ROI bounding rectangle.
    bounds = roi.getBounds()
    x0, y0, w, h = bounds.x, bounds.y, bounds.width, bounds.height

    # Create a coordinate grid over the bounding rectangle.
    ys, xs = np.mgrid[y0:y0+h, x0:x0+w]

    # Determine which points are inside the ROI.
    inside = np.vectorize(lambda x, y: roi.contains(x, y))(xs, ys)

    # Set pixels inside the ROI to 255 (binary mask value).
    mask[z, y0:y0+h, x0:x0+w][inside] = 255

# ----------------------------
# Step 4. Save the binary mask image
# ----------------------------
# Convert the NumPy mask array to an ImageJ image.
mask_imp = ij.py.to_java(mask)
ij.io().save(mask_imp, mask_save_path)

# ----------------------------
# Step 5. Calculate the segmented volume
# ----------------------------
# Count the number of voxels where the mask is 255.
segmented_voxel_count = np.sum(mask > 0)
segmented_volume = segmented_voxel_count * voxel_volume

# ----------------------------
# Final Output: Print image filename and segmented volume
# ----------------------------
print("Image filename:", image_path)
print("Segmented volume:", segmented_volume)
