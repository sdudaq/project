# Project 6: Google Password Checkup 实现对比

## 目录
1. [协议数学原理](#1-协议数学原理)  
2. [完整版 vs 简化版对比](#2-完整版-vs-简化版对比)  
3. [实现思路解析](#3-实现思路解析)  
4. [使用指南](#5-使用指南)  

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

## 2. 完整版 vs 简化版对比

| 特性                | 完整版 (`full_protocol.py`)                                                                 | 简化版 (`simplified.py`)                                                                 |
|---------------------|-------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| **协议覆盖**         | 完整实现论文 Figure 2 流程<br>• 包含加密通信层<br>• 实现完整的前缀查询协议                 | 仅核心凭证验证逻辑<br>• 省略网络通信层<br>• 简化布隆过滤器实现                          |
| **密码学组件**       | • ECDH 密钥交换<br>• AES-GCM 加密传输<br>• PBKDF2 密钥派生                                | • HKDF 密钥派生<br>• HMAC-SHA256 凭证生成                                              |
| **隐私保护**         | ✅ 服务器仅知哈希前缀（16位）<br>• 无法还原完整密码                                        | ⚠️ 服务器获知完整凭证<br>• 需信任服务器不滥用数据                                       |
| **抗攻击能力**       | 🔒 多重防护：<br>• 防重放攻击（nonce）<br>• 防中间人（ECDHE）<br>• 防时序攻击（恒定时间比较） | 🔐 基础防护：<br>• 依赖传输层加密（HTTPS）<br>• 需额外实现防暴力破解机制                |
| **性能**            | ⏱️ ~120ms/查询<br>• 主要开销在 PBKDF2 和 ECDH                                             | ⚡ ~15ms/查询<br>• 仅计算哈希和简单比对                                                 |
| **代码复杂度**       | 📜 280行<br>• 含完整单元测试<br>• 包含错误处理和安全审计点                                 | 📜 85行<br>• 聚焦核心算法<br>• 适合快速原型开发                                         |
| **适用场景**         | 🏢 生产环境<br>• 高安全要求<br>• 不可信网络环境                                            | 🎓 教育/研究<br>• 算法学习<br>• 快速验证思路                                            |

### 关键差异说明
1. **隐私保护机制**：
   - 完整版采用论文中的**分层加密查询**：
     ```math
     \text{Query} = \text{AES-GCM}(\text{Prefix}(H(pwd)), \text{ECDH-SharedKey})
     ```
   - 简化版直接传输凭证元组：
     ```math
     \text{Transmit} = (u=\text{HMAC}(usr), v=\text{SHA256}(pwd))
     ```

2. **安全边界**：
   ```mermaid
   graph LR
   A[完整版] -->|攻击面| B(网络嗅探)
   A -->|防护| C(前向安全密钥)
   D[简化版] -->|攻击面| E(HTTPS劫持)
   D -->|依赖| F(传输层安全)

## 3. 实现思路解析

### 完整版关键设计
```python
class PrivacyPreservingServer:
    def __init__(self):
        # 前缀数据库：{"2字节前缀": [完整哈希1, 完整哈希2]}
        self.prefix_db = {}  
        
        # 椭圆曲线密钥对（每次会话更新）
        self.ec_key = ECC.generate(curve='P-256')  # 前向安全
        
    def _build_index(self, hashes: List[bytes], k: int = 16):
        """构建k-bit前缀索引（默认为16位）"""
        for h in hashes:
            prefix = h[:k//8]  # 取前k位（k=16 → 取2字节）
            self.prefix_db.setdefault(prefix, []).append(h)
```
优化点​​：
​1. ​分层加密​​：先ECDH密钥交换 → 再用AES-GCM加密前缀
​2. ​恒定时间验证​​：避免时序泄漏
```python
def safe_compare(a: bytes, b: bytes) -> bool:
    return hmac.compare_digest(a, b)
```
### 简化版核心逻辑
```python
def check_credentials(u: bytes, v: bytes, filter: Set[bytes]) -> bool:
    h = sha256(u).digest()
    h_xor = bytes([a ^ b for a, b in zip(h, v)])
    return h_xor in filter  # 布隆过滤器查询
```
​​设计取舍​​：

牺牲隐私性换取实现简单
假设服务端完全可信
## 5. 使用指南

#### 命令行执行
```bash
python full_protocol.py
python  simplified.py
```