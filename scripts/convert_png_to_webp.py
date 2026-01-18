import os
from pathlib import Path
from PIL import Image

def convert_pngs_to_webp(source_dir: Path, dest_dir: Path):
    """
    Converts all PNG files in source_dir to WebP format in dest_dir.
    """
    if not source_dir.exists():
        print(f"Source directory does not exist: {source_dir}")
        return

    # Ensure destination directory exists
    dest_dir.mkdir(parents=True, exist_ok=True)

    # List all PNG files
    png_files = list(source_dir.glob("*.png"))
    
    if not png_files:
        print(f"No PNG files found in {source_dir}")
        return

    print(f"Found {len(png_files)} PNG files to convert...")

    for png_path in png_files:
        try:
            # Construct destination path
            webp_filename = png_path.stem + ".webp"
            webp_path = dest_dir / webp_filename

            # Check if it already exists (optional: skip if exists? for now overwrite)
            # Opening and converting
            with Image.open(png_path) as img:
                # Convert to RGB if necessary (though WebP supports transparency, sometimes it acts up with specific modes)
                # Usually simply saving as webp handles RGBA correctly for transparency.
                print(f"Converting: {png_path.name} -> {webp_filename}")
                img.save(webp_path, "webp", quality=80) 
                
        except Exception as e:
            print(f"Failed to convert {png_path.name}: {e}")

    print("Conversion complete.")

if __name__ == "__main__":
    # Define paths relative to the script or project root
    # Assuming script is run from project root or inside scripts/
    # We'll use absolute paths based on the provided project structure for reliability
    
    project_root = Path(r"d:\Hobby\github\hobbytp.github.io")
    source_directory = project_root / "static" / "images" / "backup" / "png"
    destination_directory = project_root / "static" / "images" / "generated-covers"

    convert_pngs_to_webp(source_directory, destination_directory)
