import cv2
import numpy as np

def block_dct(img_block):
    return cv2.dct(np.float32(img_block))

def block_idct(dct_block):
    return cv2.idct(dct_block)

def embed_dct_watermark(image_path, watermark_text, output_path, block_size=8):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    h, w = img.shape

    watermark_bin = ''.join(format(ord(c), '08b') for c in watermark_text)
    watermark_len = len(watermark_bin)

    blocks_per_row = w // block_size
    blocks_per_col = h // block_size
    max_bits = blocks_per_row * blocks_per_col

    if watermark_len > max_bits:
        raise ValueError("Watermark too large")

    watermarked_img = np.copy(img).astype(np.float32)
    bit_idx = 0
    for row in range(0, h - block_size + 1, block_size):
        for col in range(0, w - block_size + 1, block_size):
            if bit_idx >= watermark_len:
                break

            block = watermarked_img[row:row+block_size, col:col+block_size]
            dct_block = block_dct(block)

            pos1, pos2 = (3, 2), (2, 3)
            coeff1, coeff2 = dct_block[pos1], dct_block[pos2]

            bit = int(watermark_bin[bit_idx])
            delta = 5.0  # 控制嵌入强度

            if bit == 1 and coeff1 <= coeff2:
                dct_block[pos1] = coeff2 + delta
            elif bit == 0 and coeff1 >= coeff2:
                dct_block[pos2] = coeff1 + delta

            idct_block = block_idct(dct_block)
            watermarked_img[row:row+block_size, col:col+block_size] = np.clip(idct_block, 0, 255)

            bit_idx += 1
        if bit_idx >= watermark_len:
            break

    cv2.imwrite(output_path, np.uint8(watermarked_img))
    print(f"Watermark embedded (no LSB) into {output_path}")



def extract_dct_watermark(image_path, watermark_length, block_size=8):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    h, w = img.shape

    bits = []
    bit_idx = 0
    for row in range(0, h - block_size + 1, block_size):
        for col in range(0, w - block_size + 1, block_size):
            if bit_idx >= watermark_length * 8:
                break

            block = img[row:row+block_size, col:col+block_size].astype(np.float32)
            dct_block = block_dct(block)

            pos1, pos2 = (3, 2), (2, 3)
            coeff1, coeff2 = dct_block[pos1], dct_block[pos2]

            bit = 1 if coeff1 > coeff2 else 0
            bits.append(str(bit))
            bit_idx += 1
        if bit_idx >= watermark_length * 8:
            break

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

if __name__ == "__main__":
    original = "data/original.jpg"
    watermarked = "data/watermarked_dct.jpg"
    watermark = "Hidden123"

    embed_dct_watermark(original, watermark, watermarked)

    extracted = extract_dct_watermark(watermarked, len(watermark))
    print("Extracted watermark:", extracted)
    
    print("-------------------------some attacks---------------------------")
    print("Extracted (flip):", extract_dct_watermark("data/attacks/flip.jpg", len(watermark)))
    print("Extracted (translate):", extract_dct_watermark("data/attacks/translate.jpg", len(watermark)))
    print("Extracted (crop):", extract_dct_watermark("data/attacks/crop.jpg", len(watermark)))
    print("Extracted (contrast):", extract_dct_watermark("data/attacks/contrast.jpg", len(watermark)))