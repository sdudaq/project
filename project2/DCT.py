import cv2
import numpy as np
from collections import Counter
import random

def block_dct(block):
    return cv2.dct(np.float32(block))

def block_idct(dct_block):
    return cv2.idct(dct_block)

def embed_dct_watermark_robust(image_path, watermark_text, output_path, block_size=8, redundancy=3):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    h, w = img.shape

    watermark_bin = ''.join(format(ord(c), '08b') for c in watermark_text)
    total_bits = len(watermark_bin)

    max_blocks = (h // block_size) * (w // block_size)
    needed_blocks = total_bits * redundancy

    if needed_blocks > max_blocks:
        raise ValueError("Not enough blocks to embed watermark with redundancy")

    # 初始化图像副本
    watermarked_img = np.copy(img).astype(np.float32)

    # 获取所有块坐标
    block_coords = [(r, c) for r in range(0, h - block_size + 1, block_size)
                           for c in range(0, w - block_size + 1, block_size)]
    random.seed(42)  # 固定嵌入顺序
    random.shuffle(block_coords)

    pos1, pos2 = (3, 2), (2, 3)
    delta = 5.0  # 修改强度

    block_ptr = 0
    for bit in watermark_bin:
        for _ in range(redundancy):
            row, col = block_coords[block_ptr]
            block = watermarked_img[row:row+block_size, col:col+block_size]
            dct_block = block_dct(block)

            c1, c2 = dct_block[pos1], dct_block[pos2]
            if int(bit) == 1 and c1 <= c2:
                dct_block[pos1] = c2 + delta
            elif int(bit) == 0 and c1 >= c2:
                dct_block[pos2] = c1 + delta

            idct_block = block_idct(dct_block)
            watermarked_img[row:row+block_size, col:col+block_size] = np.clip(idct_block, 0, 255)
            block_ptr += 1

    cv2.imwrite(output_path, np.uint8(watermarked_img))
    print(f" Robust DCT Watermark embedded into {output_path}")


def extract_dct_watermark_robust(image_path, watermark_length, block_size=8, redundancy=3, threshold=1.0):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    h, w = img.shape

    total_bits = watermark_length * 8
    total_samples = total_bits * redundancy

    # 重新获取块顺序
    block_coords = [(r, c) for r in range(0, h - block_size + 1, block_size)
                           for c in range(0, w - block_size + 1, block_size)]
    random.seed(42)
    random.shuffle(block_coords)

    pos1, pos2 = (3, 2), (2, 3)
    bit_votes = []

    for i in range(total_bits):
        votes = []
        for j in range(redundancy):
            idx = i * redundancy + j
            row, col = block_coords[idx]
            block = img[row:row+block_size, col:col+block_size].astype(np.float32)
            dct_block = block_dct(block)

            c1, c2 = dct_block[pos1], dct_block[pos2]
            if abs(c1 - c2) < threshold:
                continue  # 弱比较差距，跳过
            bit = 1 if c1 > c2 else 0
            votes.append(bit)

        # 多数投票
        if votes:
            bit = Counter(votes).most_common(1)[0][0]
        else:
            bit = 0  # 默认值
        bit_votes.append(str(bit))

    chars = [chr(int(''.join(bit_votes[i:i+8]), 2)) for i in range(0, len(bit_votes), 8)]
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

    embed_dct_watermark_robust(original, watermark, watermarked)

    extracted = extract_dct_watermark_robust(watermarked, len(watermark))
    print("Extracted watermark:", extracted)
    
    print("-------------------------some attacks---------------------------")
    print("Extracted (flip):", extract_dct_watermark_robust("data/attacks/flip.jpg", len(watermark)))
    print("Extracted (translate):", extract_dct_watermark_robust("data/attacks/translate.jpg", len(watermark)))
    print("Extracted (crop):", extract_dct_watermark_robust("data/attacks/crop.jpg", len(watermark)))
    print("Extracted (contrast):", extract_dct_watermark_robust("data/attacks/contrast.jpg", len(watermark)))