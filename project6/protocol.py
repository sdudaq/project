# Python示例(需要安装pycryptodome和phe库)
from Crypto.Util.number import getPrime
from phe import paillier  # 加法同态加密库
import hashlib
import random

# 参数设置
prime_order = getPrime(256)  # 选择一个质数阶的群
identifier_space = 2**128    # 标识符空间
# P1的输入
V = ["password1", "password2", "user123"]  # 用户密码集合

# P2的输入
W = [("password1", 100), ("password3", 50), ("user123", 200)]  # (泄露密码, 出现次数)
# 双方选择随机私钥
k1 = random.randint(1, prime_order-1)
k2 = random.randint(1, prime_order-1)

# P2生成Paillier同态加密密钥对
public_key, private_key = paillier.generate_paillier_keypair()
def hash_to_group(element):
    # 将元素哈希到群中
    h = hashlib.sha256(element.encode()).digest()
    return int.from_bytes(h, 'big') % prime_order

# P1计算并发送
P1_hashed = [pow(hash_to_group(v), k1, prime_order) for v in V]
random.shuffle(P1_hashed)  # 打乱顺序
# P2处理P1的消息
Z = [pow(h, k2, prime_order) for h in P1_hashed]
random.shuffle(Z)

# P2准备自己的数据
P2_hashed = [(pow(hash_to_group(w), k2, prime_order), public_key.encrypt(t)) 
             for w, t in W]
random.shuffle(P2_hashed)
# P1处理P2的消息
processed_P2 = [(pow(h, k1, prime_order), t) for h, t in P2_hashed]

# 计算交集
Z_set = set(Z)
intersection_indices = [i for i, (h, _) in enumerate(processed_P2) 
                       if h in Z_set]

# 计算交集和
sum_ciphertext = sum((t for i, (_, t) in enumerate(processed_P2) 
                     if i in intersection_indices), 
                     public_key.encrypt(0))
intersection_sum = private_key.decrypt(sum_ciphertext)
print(f"Intersection sum: {intersection_sum}")