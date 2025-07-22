# Project 6: Google Password Checkup 实现对比

## 目录
1. [协议数学原理](#1-协议数学原理)  
2. [完整版 vs 简化版对比](#2-完整版-vs-简化版对比)  
3. [实现思路解析](#3-实现思路解析)  
4. [安全性与优化](#4-安全性与优化)  
5. [使用指南](#5-使用指南)  

---

## 1. 协议数学原理

### 核心公式（论文Section 3.1）

#### 凭证生成
```math
\begin{aligned}
&\text{Client:} \\
&\quad \text{secret} \leftarrow \text{HKDF}(pwd, \text{info="password-checkup"}) \\
&\quad u \leftarrow \text{HMAC-SHA256}(secret, username) \\
&\quad v \leftarrow \text{SHA256}(pwd) \\
\\
&\text{Server:} \\
&\quad h \leftarrow \text{SHA256}(u) \oplus v \\
&\quad \text{BloomFilter}[h] = 1 \quad \text{(XOR布隆过滤器)}
\end{aligned}
```
## 隐私保护机制：布隆过滤器误判率分析

### 误判概率公式
```math
P_{\text{leak}} = \frac{\text{False Positives}}{\text{Total Checks}} \leq \left(1 - e^{-kn/m}\right)^k
其中：
```
m: 布隆过滤器位数
k: 哈希函数个数
n: 已插入元素数量
