import os
import json
from PIL import Image, ExifTags

INPUT_DIR = "./training_img"
OUTPUT_IMG_DIR = "./training_noexif/img"
OUTPUT_EXIF_DIR = "./training_noexif/exif_info"

os.makedirs(OUTPUT_IMG_DIR, exist_ok=True)
os.makedirs(OUTPUT_EXIF_DIR, exist_ok=True)


def make_json_serializable(value):
    """Convert EXIF values into JSON-safe types."""
    if isinstance(value, bytes):
        return value.decode(errors="ignore")
    elif isinstance(value, tuple):
        return tuple(make_json_serializable(v) for v in value)
    elif hasattr(value, "numerator") and hasattr(value, "denominator"):
        # Handles IFDRational
        try:
            return float(value)
        except Exception:
            return str(value)
    elif isinstance(value, dict):
        return {k: make_json_serializable(v) for k, v in value.items()}
    else:
        return value


def get_exif_data(image):
    """Extract EXIF data as a JSON-safe dictionary."""
    exif = image._getexif()
    if not exif:
        return {}

    exif_dict = {}
    for tag, value in exif.items():
        tag_name = ExifTags.TAGS.get(tag, tag)
        exif_dict[tag_name] = make_json_serializable(value)

    return exif_dict
def get_datetime_from_exif(exif_dict):
    """Get DateTimeOriginal or DateTime for sorting."""
    return exif_dict.get("DateTimeOriginal") or exif_dict.get("DateTime") or ""


# Step 1: Read files and extract EXIF + datetime
images_info = []

for filename in os.listdir(INPUT_DIR):
    filepath = os.path.join(INPUT_DIR, filename)

    if not os.path.isfile(filepath):
        continue

    try:
        with Image.open(filepath) as img:
            exif_data = get_exif_data(img)
            datetime_value = get_datetime_from_exif(exif_data)

            images_info.append({
                "filename": filename,
                "filepath": filepath,
                "exif": exif_data,
                "datetime": datetime_value
            })

    except Exception as e:
        print(f"Skipping {filename}: {e}")

# Step 2: Sort by datetime (old → recent)
images_info.sort(key=lambda x: x["datetime"])

# Step 3: Copy image without EXIF and save EXIF as JSON
for index, info in enumerate(images_info, start=1):
    new_name = f"{index:03d}"
    output_img_path = os.path.join(OUTPUT_IMG_DIR, info['filename'])
    output_exif_path = os.path.join(OUTPUT_EXIF_DIR, os.path.splitext(info['filename'])[0] + ".json")

    # Save EXIF to JSON
    with open(output_exif_path, "w", encoding="utf-8") as f:
        json.dump(info["exif"], f, indent=4, ensure_ascii=False)

    # Save image WITHOUT EXIF
    with Image.open(info["filepath"]) as img:
        data = list(img.getdata())
        new_img = Image.new(img.mode, img.size)
        new_img.putdata(data)
        new_img.save(output_img_path)

    print(f"Processed {info['filename']} -> {new_name}.jpg")

print("Done.")