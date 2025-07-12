import secrets
from gmssl import sm3, func

class SM2:
    # SM2参数（国密标准）
    P = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
    A = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
    B = 0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93
    N = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123
    Gx = 0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7
    Gy = 0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0
    G = (Gx, Gy)

    @staticmethod
    def inv_mod(a, p):
        """扩展欧几里得求逆元"""
        if a == 0:
            return 0
        lm, hm = 1, 0
        low, high = a % p, p
        while low > 1:
            r = high // low
            nm, new = hm - lm * r, high - low * r
            lm, low, hm, high = nm, new, lm, low
        return lm % p

    @staticmethod
    def jacobian_double(X1, Y1, Z1):
        """Jacobian坐标点加倍"""
        if Y1 == 0:
            return (0, 0, 0)
        P, A = SM2.P, SM2.A
        S = (4 * X1 * Y1 * Y1) % P
        M = (3 * X1 * X1 + A * Z1 * Z1 * Z1 * Z1) % P
        X3 = (M * M - 2 * S) % P
        Y3 = (M * (S - X3) - 8 * Y1 * Y1 * Y1 * Y1) % P
        Z3 = (2 * Y1 * Z1) % P
        return (X3, Y3, Z3)

    @staticmethod
    def jacobian_add(X1, Y1, Z1, X2, Y2, Z2):
        """Jacobian坐标点加法"""
        P = SM2.P
        if Z1 == 0:
            return (X2, Y2, Z2)
        if Z2 == 0:
            return (X1, Y1, Z1)
        U1 = (X1 * Z2 * Z2) % P
        U2 = (X2 * Z1 * Z1) % P
        S1 = (Y1 * Z2 * Z2 * Z2) % P
        S2 = (Y2 * Z1 * Z1 * Z1) % P
        if U1 == U2:
            if S1 != S2:
                return (0, 0, 1)  # 无穷远点
            else:
                return SM2.jacobian_double(X1, Y1, Z1)
        H = (U2 - U1) % P
        R = (S2 - S1) % P
        H2 = (H * H) % P
        H3 = (H * H2) % P
        U1H2 = (U1 * H2) % P
        X3 = (R * R - H3 - 2 * U1H2) % P
        Y3 = (R * (U1H2 - X3) - S1 * H3) % P
        Z3 = (H * Z1 * Z2) % P
        return (X3, Y3, Z3)

    @staticmethod
    def jacobian_to_affine(X, Y, Z):
        """Jacobian坐标转仿射坐标"""
        P = SM2.P
        if Z == 0:
            return (0, 0)
        Z_inv = SM2.inv_mod(Z, P)
        Z_inv2 = (Z_inv * Z_inv) % P
        Z_inv3 = (Z_inv2 * Z_inv) % P
        x = (X * Z_inv2) % P
        y = (Y * Z_inv3) % P
        return (x, y)

    @staticmethod
    def ec_mult(k, point):
        """Jacobian坐标快速点乘"""
        X1, Y1 = point
        X, Y, Z = 0, 0, 0  # Jacobian无穷远点
        X2, Y2, Z2 = X1, Y1, 1
        while k > 0:
            if k & 1:
                if Z == 0:
                    X, Y, Z = X2, Y2, Z2
                else:
                    X, Y, Z = SM2.jacobian_add(X, Y, Z, X2, Y2, Z2)
            X2, Y2, Z2 = SM2.jacobian_double(X2, Y2, Z2)
            k >>= 1
        return SM2.jacobian_to_affine(X, Y, Z)

    @staticmethod
    def _hash_message(message: bytes) -> int:
        digest = sm3.sm3_hash(func.bytes_to_list(message))
        return int(digest, 16) % SM2.N

    def __init__(self):
        self.private_key = None
        self.public_key = None

    def generate_key_pair(self):
        self.private_key = secrets.randbelow(SM2.N - 1) + 1
        self.public_key = SM2.ec_mult(self.private_key, SM2.G)
        return self.private_key, self.public_key

    def sign(self, message: bytes):
        if self.private_key is None:
            raise ValueError("Private key not set")

        e = self._hash_message(message)
        if e == 0:
            e = 1

        inv_1_d = SM2.inv_mod(1 + self.private_key, SM2.N)  # 预计算，提高效率

        while True:
            k = secrets.randbelow(SM2.N - 1) + 1
            x1, y1 = SM2.ec_mult(k, SM2.G)
            r = (e + x1) % SM2.N
            if r == 0 or r + k == SM2.N:
                continue
            s = (inv_1_d * (k - r * self.private_key)) % SM2.N
            if s == 0:
                continue
            return (r, s)

    def verify(self, message: bytes, signature):
        if self.public_key is None:
            raise ValueError("Public key not set")

        r, s = signature
        if not (1 <= r < SM2.N and 1 <= s < SM2.N):
            return False

        e = self._hash_message(message)
        if e == 0:
            e = 1

        t = (r + s) % SM2.N
        if t == 0:
            return False

        sg = SM2.ec_mult(s, SM2.G)
        tp = SM2.ec_mult(t, self.public_key)
        x1, y1 = SM2.ec_add(sg, tp)
        R = (e + x1) % SM2.N
        return R == r

    @staticmethod
    def ec_add(p1, p2):
        """仿射坐标点加法，用于验证时"""
        P = SM2.P
        if p1 == (0, 0):
            return p2
        if p2 == (0, 0):
            return p1
        if p1[0] == p2[0] and p1[1] != p2[1]:
            return (0, 0)
        if p1 == p2:
            lam = (3 * p1[0] * p1[0] + SM2.A) * SM2.inv_mod(2 * p1[1], P) % P
        else:
            lam = (p2[1] - p1[1]) * SM2.inv_mod(p2[0] - p1[0], P) % P
        x3 = (lam * lam - p1[0] - p2[0]) % P
        y3 = (lam * (p1[0] - x3) - p1[1]) % P
        return (x3, y3)


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

    # 5. 性能测试（10次签名平均耗时）
    import time
    start = time.time()
    for _ in range(10):
        sm2.sign(message)
    print(f"10次签名平均耗时: {(time.time()-start)/10:.4f}s")
