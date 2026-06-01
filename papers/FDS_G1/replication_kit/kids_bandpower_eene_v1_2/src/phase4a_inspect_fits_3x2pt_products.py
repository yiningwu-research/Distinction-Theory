import os
import astropy.io.fits as fits
import glob
import numpy as np

# Paths
external_dir = "/Users/next/G_production_code/phase3a_kids_3x2pt_audit/external"
fits_dir = os.path.join(external_dir, "data", "kids", "fits")
output_dir = "/Users/next/G_production_code/phase4_kids_3x2pt_full/outputs"

# Ensure output dir exists
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "fits_product_inventory.csv")

# Write header
with open(output_file, "w") as f:
    f.write("file,hdu_name,n_rows,columns,possible_product\n")

# Iterate over all FITS files
if os.path.exists(fits_dir):
    fits_files = [os.path.join(fits_dir, f) for f in os.listdir(fits_dir) if f.endswith(".fits")]

    for fits_path in fits_files:
        fname = os.path.basename(fits_path)
        print(f"Inspecting {fname}...")
        with fits.open(fits_path) as hdul:
            for hdu in hdul:
                hdu_name = hdu.name
                n_rows = "N/A"
                cols = "N/A"
                possible = ""
                if hasattr(hdu, "data") and hdu.data is not None:
                    if hasattr(hdu.data, "shape"):
                        n_rows = hdu.data.shape[0]
                    if hasattr(hdu, "columns"):
                        col_names = [col.name for col in hdu.columns]
                        cols = "|".join(col_names)
                        # Check for Pnn/clustering keywords
                        if any(k in c.lower() for c in col_names for k in ["pnn", "nn", "clustering", "wtheta", "ngal", "lens", "density"]):
                            possible = "Pnn/Clustering Candidate"
                # Write row
                with open(output_file, "a") as f:
                    f.write(f"{fname},{hdu_name},{n_rows},{cols},{possible}\n")

# Also check covariance file size
cov_dir = os.path.join(external_dir, "data", "covariance", "outputs")
if os.path.exists(cov_dir):
    cov_3x2pt_files = [os.path.join(cov_dir, f) for f in os.listdir(cov_dir) if "3x2pt" in f]
    with open(output_file, "a") as f:
        f.write("\n# 3x2pt Covariance File Info\n")
        for cov_path in cov_3x2pt_files:
            fname = os.path.basename(cov_path)
            data = np.loadtxt(cov_path)
            N = int(np.sqrt(2*len(data) + 0.25) - 0.5)
            f.write(f"{fname},COV,{N},{len(data)} elements,Estimated 3x2pt covariance size\n")

print(f"FITS inspection complete, output saved to {output_file}")