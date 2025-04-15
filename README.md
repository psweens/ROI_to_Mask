# 🧩 ROI-Based 3D Binary Mask Generation Using ImageJ (Fiji) + JPype

This repository provides a script for converting ROI annotations (stored in ZIP format) into **3D binary masks** corresponding to `.tiff` image stacks. It uses:

- [ImageJ/Fiji](https://imagej.net/software/fiji/) via [imagej.py](https://github.com/imagej/pyimagej) for loading images and ROIs  
- `JPype` to interface directly with Java classes like `RoiDecoder`  
- `NumPy` for binary mask manipulation  
- Outputs masks and calculates **segmented volume estimates** based on voxel size

---

## 🧠 Workflow Summary

1. 🖼️ **Load Image & ROIs**
   - Reads 3D `.tiff` stacks
   - Extracts slice-specific ROIs from `.zip` files using ImageJ's Java backend

2. 🎭 **Generate Binary Masks**
   - Converts each ROI into a 2D mask and places it in the correct slice of a 3D mask
   - Handles ROI boundaries and clipping to image size

3. 📏 **Volume Calculation**
   - Computes total segmented volume using a predefined voxel size

---

## 📂 Input Requirements

| File Type | Description |
|----------|-------------|
| `.tiff`  | A 3D microscopy image (multi-slice stack) |
| `.zip`   | An ROI archive from ImageJ (ROIs mapped to slices) |

For every image named `sample.tiff`, there should be a corresponding `sample.zip` file with its ROI annotations.

---

## 🧱 Requirements

Install dependencies:

```bash
pip install imagej numpy jpype1
```

You must have **Java 8+** installed and Fiji will be automatically downloaded via:

```python
ij = imagej.init("sc.fiji:fiji", mode="headless")
```

---

## ▶️ How to Run

### 1. Set Paths

Edit the following variables at the top of the script:

```python
tiff_folder = "/path/to/your/tiffs"
roi_folder = "/path/to/your/rois"
output_folder = "/path/to/save/masks"
voxel_volume = 20 * 20 * 20 * 1e-9  # mm³
```

### 2. Run the Script

```bash
python generate_3d_masks.py
```

Each image will generate:
- A binary mask saved as `<original_name>_mask.tif`
- A volume estimate printed in CSV format

---

## 📤 Output

| Output File               | Description                         |
|---------------------------|-------------------------------------|
| `*_mask.tif`              | Binary mask with segmented regions  |
| `CSV summary` (stdout)    | Prints per-image segmented volumes  |

---

## 🧪 Example Use Case

This script is ideal for:
- Converting manually annotated ROIs into usable 3D masks
- Quantifying total segmented volume in `.tiff` stacks
- Preprocessing for deep learning or morphometric analysis

---

## 📬 Contact

Open an issue or contact the repository maintainer for questions or feature requests.
