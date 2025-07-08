# watermark_embed.py
import cv2
import numpy as np

def embed_lsb(image_path, watermark_text, output_path):
    img = cv2.imread(image_path)
    h, w, c = img.shape
    flat = img.flatten()

    # Convert watermark to binary
    watermark_bin = ''.join(format(ord(c), '08b') for c in watermark_text)
    watermark_len = len(watermark_bin)

    if watermark_len > len(flat):
        raise ValueError("Watermark too large for the image.")

    # Embed watermark bits into LSB (use 0xFE to mask last bit)
    for i in range(watermark_len):
        flat[i] = (flat[i] & 0xFE) | int(watermark_bin[i])  # fix here

    watermarked_img = flat.reshape(img.shape)
    cv2.imwrite(output_path, watermarked_img)
    print(f"Watermark embedded and saved to {output_path}")

# watermark_extract.py
def extract_lsb(image_path, watermark_length):
    img = cv2.imread(image_path)
    flat = img.flatten()

    bits = [str(flat[i] & 1) for i in range(watermark_length * 8)]
    chars = [chr(int(''.join(bits[i:i+8]), 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)

# attack.py

def flip_image(image_path, output_path):
    img = cv2.imread(image_path)
    flipped = cv2.flip(img, 1)
    cv2.imwrite(output_path, flipped)

def translate_image(image_path, output_path, tx=10, ty=10):
    img = cv2.imread(image_path)
    rows, cols = img.shape[:2]
    M = np.float32([[1, 0, tx], [0, 1, ty]])
    translated = cv2.warpAffine(img, M, (cols, rows))
    cv2.imwrite(output_path, translated)

def crop_image(image_path, output_path, crop_percent=0.1):
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    crop_h = int(h * crop_percent)
    crop_w = int(w * crop_percent)
    cropped = img[crop_h:h - crop_h, crop_w:w - crop_w]
    resized = cv2.resize(cropped, (w, h))
    cv2.imwrite(output_path, resized)

def adjust_contrast(image_path, output_path, alpha=1.5, beta=0):
    img = cv2.imread(image_path)
    adjusted = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    cv2.imwrite(output_path, adjusted)

# test.py
if __name__ == "__main__":

    original = "data/original.jpg"
    watermarked = "data/watermarked.png"
    watermark = "Hidden123"

    # Step 1: Embed watermark
    embed_lsb(original, watermark, watermarked)

    # Step 2: Apply attacks
    flip_image(watermarked, "data/attacks/flip.jpg")
    translate_image(watermarked, "data/attacks/translate.jpg")
    crop_image(watermarked, "data/attacks/crop.jpg")
    adjust_contrast(watermarked, "data/attacks/contrast.jpg")

    # Step 3: Try to extract from attacked images
    print("Extracted (watermarked):", extract_lsb("data/watermarked.png", len(watermark)))
    print("-------------------------some attacks---------------------------")
    print("Extracted (flip):", extract_lsb("data/attacks/flip.jpg", len(watermark)))
    print("Extracted (translate):", extract_lsb("data/attacks/translate.jpg", len(watermark)))
    print("Extracted (crop):", extract_lsb("data/attacks/crop.jpg", len(watermark)))
    print("Extracted (contrast):", extract_lsb("data/attacks/contrast.jpg", len(watermark)))