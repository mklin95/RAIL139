import os
import random
import sys
import time
from pathlib import Path

import google.generativeai as genai


GOOGLE_API_KEY = os.getenv("GEMINI_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("GEMINI_KEY is not set. Add it to your environment before running this script.")

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-3-flash-preview",
    generation_config={
        "temperature": 0.1,
        "top_p": 0.95,
        "response_mime_type": "text/plain",  # image to text
    },
)


def load_system_instruction(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def process_railway_images(image_folder: Path, output_folder: Path, failed_log: str) -> None:
    system_instruction = load_system_instruction("./img_to_tag_format.md")
    extensions = (".jpg", ".jpeg", ".png", ".JPG")
    image_files = [f for f in image_folder.iterdir() if f.suffix.lower() in extensions]

    print(f"🚀 Processing {len(image_files)} images as tags stored into csv files ...")
    os.makedirs(output_folder, exist_ok=True)

    for img_path in image_files:
        output_file = output_folder / f"{img_path.stem}.csv"

        if output_file.exists():
            print(f"⏩ Skipping existing file: {img_path.name}")
            continue

        try:
            print(f"📸 Recognizing: {img_path.name} ...")
            uploaded_file = genai.upload_file(path=img_path)
            response = model.generate_content([system_instruction, uploaded_file])
            csv_content = response.text.strip()
            if csv_content.startswith("```"):
                csv_content = csv_content.replace("```csv", "").replace("```", "").strip()

            csv_content = "type, feature, confidence_score\n" + csv_content
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(csv_content)

            print(f"✅ Saved: {output_file.name}")
            r = random.randrange(20000, 30000, 1) / 1000.0
            time.sleep(r)

        except Exception as e:
            print(f"❌ Failed to process: {img_path.name}: {e}")
            with open(failed_log, "a", encoding="utf-8") as log:
                log.write(f"{img_path.name}: {str(e)}\n")
            time.sleep(5)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python img_to_tags.py <image_folder> <output_csv_folder>")

    if not os.path.exists("./img_to_tag_format.md"):
        print("Error: no prompt file found.")
    else:
        image_folder = Path(sys.argv[1])
        output_folder = Path(sys.argv[2])
        failed_log = "failed_images.log"

        if not image_folder.is_dir():
            raise FileNotFoundError(f"Image folder not found: {image_folder}")

        process_railway_images(image_folder, output_folder, failed_log)
        print("\n🎉 CSV annotation complete!")