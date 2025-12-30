#!/usr/bin/env python3
"""
Test script to help run the image conversion
"""

import os
import sys

def main():
    print("Image Conversion Test Helper")
    print("=" * 40)
    
    # Check if images directory is provided
    if len(sys.argv) < 2:
        print("Please provide the images directory path.")
        print("Example usage:")
        print("  python test_image_conversion.py /path/to/your/images")
        print("  python test_image_conversion.py C:\\path\\to\\images")
        print()
        print("Common image directories might be:")
        print("  - uploads/")
        print("  - static/images/")
        print("  - public/uploads/")
        print("  - /var/www/html/uploads/")
        sys.exit(1)
    
    images_dir = sys.argv[1]
    
    # Check if directory exists
    if not os.path.exists(images_dir):
        print(f"❌ Directory not found: {images_dir}")
        sys.exit(1)
    
    print(f"✅ Images directory found: {images_dir}")
    
    # List some files in the directory
    try:
        files = os.listdir(images_dir)
        image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'))]
        
        print(f"📁 Total files in directory: {len(files)}")
        print(f"🖼️  Image files found: {len(image_files)}")
        
        if image_files:
            print("\nFirst 5 image files:")
            for i, img in enumerate(image_files[:5]):
                print(f"  {i+1}. {img}")
            
            if len(image_files) > 5:
                print(f"  ... and {len(image_files) - 5} more")
        
        # Check for non-WebP images
        non_webp = [f for f in image_files if not f.lower().endswith('.webp')]
        print(f"🔄 Non-WebP images that could be converted: {len(non_webp)}")
        
        if non_webp:
            print("\nFirst 5 non-WebP images:")
            for i, img in enumerate(non_webp[:5]):
                print(f"  {i+1}. {img}")
        
        print("\n" + "=" * 40)
        print("Ready to run conversion!")
        print("Commands to try:")
        print(f"  # Dry run (preview only):")
        print(f"  python convert_images_to_webp.py \"{images_dir}\" --dry-run")
        print(f"  ")
        print(f"  # Actual conversion:")
        print(f"  python convert_images_to_webp.py \"{images_dir}\"")
        
    except Exception as e:
        print(f"❌ Error reading directory: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

