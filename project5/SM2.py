import random
import hashlib
import base64
from gmssl import sm3, func
class SM2:
    """
    纯Python实现的SM2椭圆曲线数字签名算法
    包含密钥生成、签名和验证功能
    """
    
    # SM2推荐椭圆曲线参数 (国密标准GB/T 32918.5-2016)
    P = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
    A = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
    B = 0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93
    N = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123
    Gx = 0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7
    Gy = 0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0
    G = (Gx, Gy)
    
    @staticmethod
    def inv_mod(a, p):
        """扩展欧几里得算法求模逆"""
        old_r, r = a, p
        old_s, s = 1, 0
        while r != 0:
            quotient = old_r // r
            old_r, r = r, old_r - quotient * r
            old_s, s = s, old_s - quotient * s
        return old_s % p
    @staticmethod
    def _hash_message(message: bytes) -> int:
        """使用SM3计算消息哈希值，返回整数形式"""
        digest = sm3.sm3_hash(func.bytes_to_list(message))  # 返回十六进制字符串
        return int(digest, 16) % SM2.N

    @staticmethod
    def ec_add(p1, p2, p):
        """椭圆曲线点加法"""
        if p1 == (0, 0):
            return p2
        if p2 == (0, 0):
            return p1
        if p1[0] == p2[0] and p1[1] != p2[1]:
            return (0, 0)
        if p1 == p2:
            lam = (3 * p1[0] * p1[0] + SM2.A) * SM2.inv_mod(2 * p1[1], p) % p
        else:
            lam = (p2[1] - p1[1]) * SM2.inv_mod(p2[0] - p1[0], p) % p
        x3 = (lam * lam - p1[0] - p2[0]) % p
        y3 = (lam * (p1[0] - x3) - p1[1]) % p
        return (x3, y3)
    
    @staticmethod
    def ec_mult(k, point, p):
        """椭圆曲线点乘法（快速幂算法）"""
        result = (0, 0)
        addend = point
        while k:
            if k & 1:
                result = SM2.ec_add(result, addend, p)
            addend = SM2.ec_add(addend, addend, p)
            k >>= 1
        return result
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
    
    def generate_key_pair(self):
        """生成SM2密钥对"""
        self.private_key = random.randint(1, SM2.N - 1)
        self.public_key = SM2.ec_mult(self.private_key, SM2.G, SM2.P)
        return self.private_key, self.public_key
    
    def sign(self, message):
        """
        SM2签名
        :param message: 待签名的消息(bytes)
        :return: (r, s)签名元组
        """
        if not self.private_key:
            raise ValueError("Private key not initialized")
        
        # 计算消息哈希 (实际应使用SM3，此处用SHA-256替代)
        e = self._hash_message(message)
        if e == 0:
            e = 1
            
        while True:
            # 生成随机k
            k = random.randint(1, SM2.N - 1)
            
            # 计算椭圆曲线点(x1, y1) = [k]G
            x1, y1 = SM2.ec_mult(k, SM2.G, SM2.P)
            
            # 计算r = (e + x1) mod n
            r = (e + x1) % SM2.N
            if r == 0 or r + k == SM2.N:
                continue
                
            # 计算s = ((1 + d)^-1 * (k - r*d)) mod n
            s = (SM2.inv_mod(1 + self.private_key, SM2.N) * (k - r * self.private_key)) % SM2.N
            if s == 0:
                continue
                
            return (r, s)
    
    def verify(self, message, signature):
        """
        SM2签名验证
        :param message: 原始消息(bytes)
        :param signature: (r, s)签名元组
        :return: 验证结果(bool)
        """
        if not self.public_key:
            raise ValueError("Public key not initialized")
            
        r, s = signature
        if not (1 <= r < SM2.N and 1 <= s < SM2.N):
            return False
            
        # 计算消息哈希 (实际应使用SM3，此处用SHA-256替代)
        e = self._hash_message(message)
        if e == 0:
            e = 1
            
        # 计算t = (r + s) mod n
        t = (r + s) % SM2.N
        if t == 0:
            return False
            
        # 计算椭圆曲线点(x1, y1) = [s]G + [t]P
        sg = SM2.ec_mult(s, SM2.G, SM2.P)
        tp = SM2.ec_mult(t, self.public_key, SM2.P)
        x1, _ = SM2.ec_add(sg, tp, SM2.P)
        
        # 验证R = (e + x1) mod n
        return (e + x1) % SM2.N == r


# 使用示例
if __name__ == "__main__":
    sm2 = SM2()
    
    # 1. 生成密钥对
    private_key, public_key = sm2.generate_key_pair()
    print("私钥:", hex(private_key))
    print("公钥(x,y):", hex(public_key[0]), hex(public_key[1]))
    
    # 2. 签名消息
    message = b"Hello SM2 Digital Signature"
    signature = sm2.sign(message)
    print("签名(r,s):", hex(signature[0]), hex(signature[1]))
    
    # 3. 验证签名
    is_valid = sm2.verify(message, signature)
    print("签名验证结果:", "有效" if is_valid else "无效")
    
    # 4. 测试篡改检测
    tampered_message = b"Hello SM2 Digital Signature!"
    is_valid_tampered = sm2.verify(tampered_message, signature)
    print("篡改消息验证结果:", "有效" if is_valid_tampered else "无效")
        # 4. 性能测试
    import time
    start = time.time()
    for _ in range(10):
        sm2.sign(message)
    print(f"10次签名平均耗时: {(time.time()-start)/10:.4f}s")