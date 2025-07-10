# Image Watermarking with LSB and DCT (图像水印嵌入与提取)

本项目实现了基于 LSB 和 DCT 的图片水印嵌入与提取方法，并支持常见攻击（翻转、裁剪、平移、调对比度）下的鲁棒性测试。

---

## 项目结构


---

## 实现原理

### LSB 方法（Least Significant Bit）

- 将文本水印转为二进制后，嵌入图像像素值的最低位（LSB）。
- 优点：实现简单、不可见性强；
- 缺点：对翻转、裁剪、压缩等处理非常脆弱。

### DCT 方法（Discrete Cosine Transform）

- 将图像转为频域，对中低频系数进行微调以嵌入水印；
- 优点：较强鲁棒性，可抵抗压缩、滤波、部分裁剪；
- 缺点：实现稍复杂，可能影响图像质量。

---

## 使用方法

### 1. 安装依赖

```bash
pip install opencv-python numpy


## 查看输出
Watermark embedded and saved to data/watermarked.png
Extracted (watermarked): Hidden123
-------------------------some attacks---------------------------
Extracted (flip): ;¤lí¶q"R
Extracted (translate): $!
Extracted (crop): IIN
Extracted (contrast): ù 8ìNH
```

## LSB
<img src="project2\data\original.jpg" alt="原图片" width="500">
## 总结
- 经过演示我们可以发现LCB很脆弱如果压缩图片为jpg会提取不到水印，但是如果改进为DCT会发现即使是压缩也会提取到完整的水印说明DCT的鲁棒性更强

