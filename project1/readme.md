# SM4 加密算法实现（C++ 版本）

本项目是对 [GB/T 32907-2016 国家密码算法 SM4](https://en.wikipedia.org/wiki/SM4_(cipher)) 的标准实现，支持跨平台构建与独立测试。

---

## 项目结构
```
project1/
├── CMakeLists.txt # CMake 构建配置
├── include/ # 头文件目录
│ └── SM4.h # 算法接口定义
├── src/ # 算法实现代码
│ └── SM4.cpp # SM4 核心逻辑
├── tests/ # 测试代码
│ └── test.cpp # 功能测试
├── build/ # 构建目录（自动生成）
├── .vscode/ # VSCode 配置（可选）
├── README.md # 项目说明文件
└── readme.md # 补充说明
```

---

## 功能特性

### 标准实现

- 符合 **GB/T 32907-2016** 标准；
- 支持 **128位密钥长度**；
- 实现 **32轮 Feistel 网络结构**。

### 工程化支持

- 支持 **CMake 跨平台构建**（Linux / Windows / macOS）；
- **头文件与实现分离**，便于嵌入其他项目；
- **独立测试目录**，便于功能验证。

---

## 构建指南

### 环境依赖

- CMake ≥ 3.10
- GCC / MinGW / Clang / MSVC 任一编译器

### 构建步骤（以 MinGW 为例）

```bash
# Step 1: 创建构建目录
mkdir build && cd build

# Step 2: 使用 CMake 生成构建文件
cmake -G "MinGW Makefiles" ..

# Step 3: 编译项目
make
```
## 运行查看
```
./sm4_test
```
# 解析
## 目录
- [算法概述](#算法概述)
- [核心组件](#核心组件)
  - [S盒](#s盒)
  - [固定参数](#固定参数)
  - [密钥扩展](#密钥扩展)
  - [加密解密流程](#加密解密流程)
- [代码结构](#代码结构)
  - [主要方法](#主要方法)
  - [辅助函数](#辅助函数)


## 算法概述
SM4是中国国家密码管理局发布的分组密码算法，具有以下特点：
- 分组长度：128位（16字节）
- 密钥长度：128位（16字节）
- 轮数：32轮
- 采用非平衡Feistel结构

## 核心组件

### S盒
256字节的固定置换表，用于非线性变换，在T和T'变换中使用。

### 固定参数
- `FK`：系统参数，用于密钥扩展
- `CK`：固定参数，用于轮密钥生成

### 密钥扩展
1. 将128位主密钥分为4个32位字(MK)
2. 与FK异或得到中间密钥K
3. 通过T'变换和CK生成32个轮密钥

### 加密解密流程
加密和解密使用相同的结构，只是轮密钥的使用顺序相反。每轮操作：
1. 非线性变换T（S盒替换+线性变换L）
2. 轮密钥异或
3. Feistel结构轮函数F

## 代码结构

### 主要方法
| 方法 | 描述 |
|------|------|
| `SM4()` | 构造函数，接收16字节密钥 |
| `generateRoundKeys()` | 实现密钥扩展算法 |
| `crypt()` | 核心加密/解密函数 |
| `encrypt()/decrypt()` | 分别调用crypt()的便捷方法 |

### 辅助函数
| 函数 | 描述 |
|------|------|
| `F()` | 轮函数，包含非线性变换和线性变换 |
| `T()/T'()` | 合成变换，包含S盒替换和线性变换 |
| `L()/L'()` | 线性变换，使用循环左移实现 |
| `rotateLeft()` | 循环左移辅助函数 |

### 代码模块
```src/SM4.cpp
/**
 * @file SM4.cpp
 * @brief SM4算法核心实现
 */

#include "SM4.h"
#include <array>

const uint8_t SM4::SBOX[256] = {
    0xd6, 0x90, 0xe9, 0xfe, 0xcc, 0xe1, 0x3d, 0xb7, 0x16, 0xb6, 0x14, 0xc2, 0x28, 0xfb, 0x2c, 0x05,
    0x2b, 0x67, 0x9a, 0x76, 0x2a, 0xbe, 0x04, 0xc3, 0xaa, 0x44, 0x13, 0x26, 0x49, 0x86, 0x06, 0x99,
    0x9c, 0x42, 0x50, 0xf4, 0x91, 0xef, 0x98, 0x7a, 0x33, 0x54, 0x0b, 0x43, 0xed, 0xcf, 0xac, 0x62,
    0xe4, 0xb3, 0x1c, 0xa9, 0xc9, 0x08, 0xe8, 0x95, 0x80, 0xdf, 0x94, 0xfa, 0x75, 0x8f, 0x3f, 0xa6,
    0x47, 0x07, 0xa7, 0xfc, 0xf3, 0x73, 0x17, 0xba, 0x83, 0x59, 0x3c, 0x19, 0xe6, 0x85, 0x4f, 0xa8,
    0x68, 0x6b, 0x81, 0xb2, 0x71, 0x64, 0xda, 0x8b, 0xf8, 0xeb, 0x0f, 0x4b, 0x70, 0x56, 0x9d, 0x35,
    0x1e, 0x24, 0x0e, 0x5e, 0x63, 0x58, 0xd1, 0xa2, 0x25, 0x22, 0x7c, 0x3b, 0x01, 0x21, 0x78, 0x87,
    0xd4, 0x00, 0x46, 0x57, 0x9f, 0xd3, 0x27, 0x52, 0x4c, 0x36, 0x02, 0xe7, 0xa0, 0xc4, 0xc8, 0x9e,
    0xea, 0xbf, 0x8a, 0xd2, 0x40, 0xc7, 0x38, 0xb5, 0xa3, 0xf7, 0xf2, 0xce, 0xf9, 0x61, 0x15, 0xa1,
    0xe0, 0xae, 0x5d, 0xa4, 0x9b, 0x34, 0x1a, 0x55, 0xad, 0x93, 0x32, 0x30, 0xf5, 0x8c, 0xb1, 0xe3,
    0x1d, 0xf6, 0xe2, 0x2e, 0x82, 0x66, 0xca, 0x60, 0xc0, 0x29, 0x23, 0xab, 0x0d, 0x53, 0x4e, 0x6f,
    0xd5, 0xdb, 0x37, 0x45, 0xde, 0xfd, 0x8e, 0x2f, 0x03, 0xff, 0x6a, 0x72, 0x6d, 0x6c, 0x5b, 0x51,
    0x8d, 0x1b, 0xaf, 0x92, 0xbb, 0xdd, 0xbc, 0x7f, 0x11, 0xd9, 0x5c, 0x41, 0x1f, 0x10, 0x5a, 0xd8,
    0x0a, 0xc1, 0x31, 0x88, 0xa5, 0xcd, 0x7b, 0xbd, 0x2d, 0x74, 0xd0, 0x12, 0xb8, 0xe5, 0xb4, 0xb0,
    0x89, 0x69, 0x97, 0x4a, 0x0c, 0x96, 0x77, 0x7e, 0x65, 0xb9, 0xf1, 0x09, 0xc5, 0x6e, 0xc6, 0x84,
    0x18, 0xf0, 0x7d, 0xec, 0x3a, 0xdc, 0x4d, 0x20, 0x79, 0xee, 0x5f, 0x3e, 0xd7, 0xcb, 0x39, 0x48
};

const uint32_t SM4::FK[4] = {
    0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dc
};

const uint32_t SM4::CK[32] = {
    0x00070e15, 0x1c232a31, 0x383f464d, 0x545b6269,
    0x70777e85, 0x8c939aa1, 0xa8afb6bd, 0xc4cbd2d9,
    0xe0e7eef5, 0xfc030a11, 0x181f262d, 0x343b4249,
    0x50575e65, 0x6c737a81, 0x888f969d, 0xa4abb2b9,
    0xc0c7ced5, 0xdce3eaf1, 0xf8ff060d, 0x141b2229,
    0x30373e45, 0x4c535a61, 0x686f767d, 0x848b9299,
    0xa0a7aeb5, 0xbcc3cad1, 0xd8dfe6ed, 0xf4fb0209,
    0x10171e25, 0x2c333a41, 0x484f565d, 0x646b7279
};

SM4::SM4(const std::vector<uint8_t>& key) {
    if (key.size() != 16) {
        throw std::invalid_argument("SM4 key must be 128 bits (16 bytes)");
    }
    generateRoundKeys(key);
}

void SM4::generateRoundKeys(const std::vector<uint8_t>& key) {
    uint32_t MK[4];
    for (int i = 0; i < 4; i++) {
        MK[i] = (key[4*i] << 24) | (key[4*i+1] << 16) | (key[4*i+2] << 8) | key[4*i+3];
    }

    uint32_t K[36];
    for (int i = 0; i < 4; i++) {
        K[i] = MK[i] ^ FK[i];
    }

    for (int i = 0; i < 32; i++) {
        K[i+4] = K[i] ^ T_prime(K[i+1] ^ K[i+2] ^ K[i+3] ^ CK[i]);
        rk[i] = K[i+4];
    }
}

// ... 其他成员函数实现 ...

std::vector<uint8_t> SM4::crypt(const std::vector<uint8_t>& input, bool isEncrypt) {
    if (input.size() % 16 != 0) {
        throw std::invalid_argument("SM4 input length must be multiple of 16 bytes");
    }

    std::vector<uint8_t> output;
    output.reserve(input.size());

    for (size_t i = 0; i < input.size(); i += 16) {
        uint32_t X[4];
        for (int j = 0; j < 4; j++) {
            X[j] = (input[i+4*j]<<24) | (input[i+4*j+1]<<16) | 
                   (input[i+4*j+2]<<8) | input[i+4*j+3];
        }

        for (int j = 0; j < 32; j++) {
            uint32_t rk_j = isEncrypt ? rk[j] : rk[31-j];
            uint32_t X_next = F(X[0], X[1], X[2], X[3], rk_j);
            X[0] = X[1];
            X[1] = X[2];
            X[2] = X[3];
            X[3] = X_next;
        }

        uint32_t Y[4] = {X[3], X[2], X[1], X[0]};
        for (int j = 0; j < 4; j++) {
            output.push_back((Y[j] >> 24) & 0xFF);
            output.push_back((Y[j] >> 16) & 0xFF);
            output.push_back((Y[j] >> 8) & 0xFF);
            output.push_back(Y[j] & 0xFF);
        }
    }

    return output;
}
std::vector<uint8_t> SM4::encrypt(const std::vector<uint8_t>& plaintext) {
    return crypt(plaintext, true);
}

std::vector<uint8_t> SM4::decrypt(const std::vector<uint8_t>& ciphertext) {
    return crypt(ciphertext, false);
}
// 线性变换函数 F
uint32_t SM4::F(uint32_t X0, uint32_t X1, uint32_t X2, uint32_t X3, uint32_t rk) {
    return X0 ^ L(X1 ^ X2 ^ X3 ^ rk);
}

// 密钥扩展专用变换 T'
uint32_t SM4::T_prime(uint32_t X) {
    uint32_t a[4];
    a[0] = (X >> 24) & 0xFF;
    a[1] = (X >> 16) & 0xFF;
    a[2] = (X >> 8) & 0xFF;
    a[3] = X & 0xFF;

    for (int i = 0; i < 4; i++) {
        a[i] = SBOX[a[i]];
    }

    uint32_t B = (a[0] << 24) | (a[1] << 16) | (a[2] << 8) | a[3];
    return L_prime(B);
}
// 线性变换 L
uint32_t SM4::L(uint32_t B) {
    return B ^ rotateLeft(B, 2) ^ rotateLeft(B, 10) ^ rotateLeft(B, 18) ^ rotateLeft(B, 24);
}

// 密钥扩展专用线性变换 L'
uint32_t SM4::L_prime(uint32_t B) {
    return B ^ rotateLeft(B, 13) ^ rotateLeft(B, 23);
}
// 合成变换 T
uint32_t SM4::T(uint32_t X) {
    uint32_t a[4];
    a[0] = (X >> 24) & 0xFF;
    a[1] = (X >> 16) & 0xFF;
    a[2] = (X >> 8) & 0xFF;
    a[3] = X & 0xFF;

    for (int i = 0; i < 4; i++) {
        a[i] = SBOX[a[i]];
    }

    uint32_t B = (a[0] << 24) | (a[1] << 16) | (a[2] << 8) | a[3];
    return L(B);
}

// 循环左移辅助函数
uint32_t SM4::rotateLeft(uint32_t x, uint32_t n) {
    return (x << n) | (x >> (32 - n));
}
```
## tests/test.cpp
```
/**
 * @file test.cpp
 * @brief SM4算法测试用例
 */

#include "../include/SM4.h"
#include <iostream>
#include <iomanip>

void printHex(const std::vector<uint8_t>& data) {
    for (uint8_t b : data) {
        std::cout << std::hex << std::setw(2) << std::setfill('0') 
                  << static_cast<int>(b) << " ";
    }
    std::cout << std::dec << "\n";
}

void testStandardVector() {
    std::vector<uint8_t> key = {
        0x01,0x23,0x45,0x67,0x89,0xab,0xcd,0xef,
        0xfe,0xdc,0xba,0x98,0x76,0x54,0x32,0x10
    };
    std::vector<uint8_t> plaintext = {
        0x01,0x23,0x45,0x67,0x89,0xab,0xcd,0xef,
        0xfe,0xdc,0xba,0x98,0x76,0x54,0x32,0x10
    };

    SM4 sm4(key);
    auto ciphertext = sm4.encrypt(plaintext);
    auto decrypted = sm4.decrypt(ciphertext);

std::cout << "Standard test vector:\n";
std::cout << "Plaintext: "; printHex(plaintext);
std::cout << "Ciphertext: "; printHex(ciphertext);
std::cout << "Decrypted: "; printHex(decrypted);
std::cout << (plaintext == decrypted ? "Success" : "Failure") << "\n\n";
}

int main() {
    try {
        testStandardVector();
    } catch (const std::exception& e) {
        std::cerr << "test error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```