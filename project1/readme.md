# SM4 加密算法实现（C++ 版本）

本项目是对 [GB/T 32907-2016 国家密码算法 SM4](https://en.wikipedia.org/wiki/SM4_(cipher)) 的标准实现，支持跨平台构建与独立测试。

---

## 项目结构

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

##运行查看
./sm4_test
