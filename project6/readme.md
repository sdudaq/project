# Project 6: Google Password Checkup 实现

## Private Set Intersection-Sum Protocol (PSI-Sum) 协议
1. 概述
协议实现了一个基于DDH假设的隐私保护集合交集求和协议(PSI-Sum)，允许两方在不泄露各自完整数据集的情况下，计算双方数据的交集，并对交集项在P2中的关联值求和。
2. 协议原理
### 2.1 问题定义
给定：
P1：集合 V = {v₁, v₂, ..., vₘ₁}，其中 vᵢ ∈ U (标识符空间)
P2：集合 W = {(w₁, t₁), (w₂, t₂), ..., (wₘ₂, tₘ₂)}，其中 wⱼ ∈ U，tⱼ ∈ ℤ⁺
目标：
计算 V ∩ W (交集)
计算 ∑{tⱼ | (wⱼ, tⱼ) ∈ W 且 wⱼ ∈ V}
### 2.2 协议设计原理
协议基于以下密码学技术：

​​DDH假设​​：在素数阶群中，区分(gᵃ, gᵇ, gᵃᵇ)和(gᵃ, gᵇ, gᶜ)是困难的
​​加法同态加密​​：支持对加密数据进行加法运算
​​随机预言机模型​​：哈希函数H:U→G被视为随机预言机
### 2.3 数学公式解释
#### 哈希到群​​：
``` math
H:U → G
```
``` math
h = H(v) = SHA256(v) mod p
```
将任意标识符映射到群G中的随机元素
#### 双盲化过程：
​​
``` math
P1计算: H(v)ᵏ¹ mod p
```
``` math
P2计算: (H(v)ᵏ¹)ᵏ² = H(v)ᵏ¹ᵏ² mod p
```
通过双方私钥k₁,k₂实现双重盲化
#### 交集判断：
​``` math
J = {j | H(wⱼ)ᵏ¹ᵏ² ∈ Z}
​​```
其中Z是P2返回的盲化集合

#### 同态求和：
``` math
Sⱼ = Σ tⱼ (对j ∈ J)

```

## 代码实现
### 3.1 依赖库
``` python
from Crypto.Util.number import getPrime  # 生成大素数
from phe import paillier  # 加法同态加密
import hashlib  # 哈希函数
import random  # 随机数生成
```
### 3.2 核心函数
#### 哈希到群函数
``` python
def hash_to_group(element):
    h = hashlib.sha256(element.encode()).digest()
    return int.from_bytes(h, 'big') % prime_order
```
输入：字符串元素
输出：群G中的元素(大整数)
过程：SHA256哈希后取模素数阶
#### 双盲化过程
``` python
# P1盲化
P1_hashed = [pow(hash_to_group(v), k1, prime_order) for v in V]

# P2二次盲化
Z = [pow(h, k2, prime_order) for h in P1_hashed]
```
#### 同态加密处理
``` python
# P2准备加密数据
P2_hashed = [(pow(hash_to_group(w), k2, prime_order), 
              public_key.encrypt(t)) for w, t in W]
```
#### 交集计算
``` python
# P1处理P2数据
processed_P2 = [(pow(h, k1, prime_order), t) for h, t in P2_hashed]

# 计算交集索引
intersection_indices = [i for i, (h, _) in enumerate(processed_P2) 
                       if h in Z_set]
```

#### 同态求和
``` python
sum_ciphertext = sum((t for i, (_, t) in enumerate(processed_P2) 
                     if i in intersection_indices), 
                     public_key.encrypt(0))
```
## 协议流程

### 4.1 初始化阶段
生成256位素数阶群
P1和P2各自生成随机私钥k₁,k₂
P2生成Paillier密钥对(pk,sk)
### 4.2 协议执行
####
Round 1 (P1 → P2)
P1对每个v∈V计算H(v)ᵏ¹
打乱顺序后发送给P2
####
Round 2 (P2 → P1)
P2对收到的每个元素计算H(v)ᵏ¹ᵏ² → 生成集合Z
P2对自己的每个(w,t)计算(H(w)ᵏ², Enc(t))
打乱顺序后发送Z和加密数据给P1
####
Round 3 (P1计算)
P1对P2的数据计算(H(w)ᵏ²)ᵏ¹ = H(w)ᵏ¹ᵏ²
找出H(w)ᵏ¹ᵏ² ∈ Z的项 → 交集
对交集中的加密值求和并解密
## 安全分析
### 1. ​数据隐私​​：
原始数据通过哈希和双盲化保护
只有交集结果泄露，非交集项保持隐藏
### 2. ​前向安全​​：
每次会话使用临时密钥k₁,k₂
即使长期密钥泄露，历史会话仍安全
### 3. ​抵抗攻击​​：
抵抗被动攻击：得益于DDH假设
抵抗主动攻击：需要额外的认证机制
## 实验结果
示例输入：
``` python
V = ["password1", "password2", "user123"]
W = [("password1", 100), ("password3", 50), ("user123", 200)]
```
输出：
``` python
Intersection sum: 300
```