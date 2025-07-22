import hashlib
import hmac
from Crypto.PublicKey import ECC
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import HKDF
from Crypto.Random import get_random_bytes
from typing import List, Dict, Tuple
import unittest

# ------------------------ 密码哈希计算模块 ------------------------
def compute_password_hash(password: str, salt: bytes = b'') -> bytes:
    """使用PBKDF2-HMAC-SHA256计算密码哈希"""
    if not salt:
        salt = get_random_bytes(16)
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000,  # 迭代次数
        32       # 输出长度
    )

# ------------------------ 协议核心模块 ------------------------
class PasswordCheckupProtocol:
    @staticmethod
    def get_prefix(hash_value: bytes, k: int = 16) -> bytes:
        """获取哈希值的前k位 (k in bits)"""
        byte_length = (k + 7) // 8  # 计算需要的字节数
        return hash_value[:byte_length]
    
    @staticmethod
    def constant_time_compare(a: bytes, b: bytes) -> bool:
        """恒定时间比较函数，防止时序攻击"""
        return hmac.compare_digest(a, b)

# ------------------------ 服务端实现 ------------------------
class PasswordCheckupServer:
    def __init__(self, leaked_hashes: List[bytes]):
        """
        初始化服务器
        :param leaked_hashes: 已泄露的密码哈希列表
        """
        self.ec_key = ECC.generate(curve='P-256')
        self.db = self._build_prefix_db(leaked_hashes)
        self.client_pubkey = None  # 会在查询时设置
    
    def _build_prefix_db(self, hashes: List[bytes]) -> Dict[bytes, List[bytes]]:
        """构建前缀查询数据库"""
        db = {}
        for h in hashes:
            prefix = PasswordCheckupProtocol.get_prefix(h)
            db.setdefault(prefix, []).append(h)
        return db
    
    def get_public_key(self) -> ECC.EccKey:
        """获取服务器的ECC公钥"""
        return self.ec_key.public_key()
    
    def set_client_public_key(self, pubkey: ECC.EccKey):
        """设置客户端的ECC公钥"""
        self.client_pubkey = pubkey
    
    def _derive_shared_key(self) -> bytes:
        """派生共享密钥"""
        if not self.client_pubkey:
            raise ValueError("Client public key not set")
        
        shared_secret = self.ec_key.d * self.client_pubkey.pointQ
        return HKDF(
            shared_secret.x.to_bytes(32, 'big'),
            32,  # 密钥长度
            b'',  # salt
            hashlib.sha256
        )
    
    def query(self, encrypted_prefix: bytes, nonce: bytes) -> List[bytes]:
        """
        处理客户端查询
        :return: 加密的匹配哈希列表
        """
        # 派生共享密钥
        shared_key = self._derive_shared_key()
        
        # 解密前缀
        cipher = AES.new(shared_key, AES.MODE_GCM, nonce=nonce)
        prefix = cipher.decrypt(encrypted_prefix)
        
        # 获取匹配的哈希值
        matched_hashes = self.db.get(prefix, [])
        
        # 加密匹配的哈希值
        encrypted_results = []
        for h in matched_hashes:
            cipher = AES.new(shared_key, AES.MODE_GCM, nonce=nonce)
            encrypted_results.append(cipher.encrypt(h))
        
        return encrypted_results

# ------------------------ 客户端实现 ------------------------
class PasswordCheckupClient:
    def __init__(self):
        self.ec_key = ECC.generate(curve='P-256')
        self.server_pubkey = None
    
    def get_public_key(self) -> ECC.EccKey:
        """获取客户端的ECC公钥"""
        return self.ec_key.public_key()
    
    def set_server_public_key(self, pubkey: ECC.EccKey):
        """设置服务器的ECC公钥"""
        self.server_pubkey = pubkey
    
    def _derive_shared_key(self) -> bytes:
        """派生共享密钥"""
        if not self.server_pubkey:
            raise ValueError("Server public key not set")
        
        shared_secret = self.ec_key.d * self.server_pubkey.pointQ
        return HKDF(
            shared_secret.x.to_bytes(32, 'big'),
            32,  # 密钥长度
            b'',  # salt
            hashlib.sha256
        )
    
    def check_password(self, password: str, server: PasswordCheckupServer) -> bool:
        """
        检查密码是否已泄露
        :return: True如果密码已泄露，False否则
        """
        # 1. 计算密码哈希
        pwd_hash = compute_password_hash(password)
        
        # 2. 获取前缀
        prefix = PasswordCheckupProtocol.get_prefix(pwd_hash)
        
        # 3. 设置服务器公钥
        server.set_client_public_key(self.get_public_key())
        self.set_server_public_key(server.get_public_key())
        
        # 4. 派生共享密钥
        shared_key = self._derive_shared_key()
        
        # 5. 加密前缀
        nonce = get_random_bytes(12)  # GCM推荐12字节nonce
        cipher = AES.new(shared_key, AES.MODE_GCM, nonce=nonce)
        encrypted_prefix = cipher.encrypt(prefix)
        
        # 6. 发送查询并获取响应
        encrypted_hashes = server.query(encrypted_prefix, nonce)
        
        # 7. 解密并验证
        for enc_hash in encrypted_hashes:
            cipher = AES.new(shared_key, AES.MODE_GCM, nonce=nonce)
            decrypted_hash = cipher.decrypt(enc_hash)
            
            if PasswordCheckupProtocol.constant_time_compare(decrypted_hash, pwd_hash):
                return True
        
        return False

# ------------------------ 测试模块 ------------------------
class TestPasswordCheckup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 模拟一些已泄露的密码
        cls.leaked_passwords = [
            "password123",
            "123456",
            "qwerty",
            "letmein",
            "admin123"
        ]
        
        # 计算它们的哈希
        cls.leaked_hashes = [compute_password_hash(pwd) for pwd in cls.leaked_passwords]
        
        # 初始化服务端
        cls.server = PasswordCheckupServer(cls.leaked_hashes)
    
    def test_leaked_password(self):
        client = PasswordCheckupClient()
        
        # 测试已知泄露的密码
        for pwd in self.leaked_passwords:
            self.assertTrue(client.check_password(pwd, self.server),
                          f"Password '{pwd}' should be reported as leaked")
    
    def test_safe_password(self):
        client = PasswordCheckupClient()
        
        # 测试未泄露的密码
        safe_passwords = [
            "thisIsASecureP@ssw0rd",
            "anotherSafePassword!123",
            "correct horse battery staple"
        ]
        
        for pwd in safe_passwords:
            self.assertFalse(client.check_password(pwd, self.server),
                           f"Password '{pwd}' should not be reported as leaked")
    
    def test_privacy(self):
        """测试协议是否真正保护了密码隐私"""
        client = PasswordCheckupClient()
        
        # 检查服务器是否只能看到前缀而非完整密码
        original_query = self.server.query
        
        def spy_query(encrypted_prefix: bytes, nonce: bytes):
            # 派生共享密钥来解密（模拟服务器正常操作）
            shared_key = self.server._derive_shared_key()
            cipher = AES.new(shared_key, AES.MODE_GCM, nonce=nonce)
            prefix = cipher.decrypt(encrypted_prefix)
            
            # 确保服务器只能看到前缀（16位），而不是完整哈希（256位）
            self.assertEqual(len(prefix), 2)  # 16 bits = 2 bytes
            
            return original_query(encrypted_prefix, nonce)
        
        self.server.query = spy_query
        
        # 执行测试
        client.check_password("password123", self.server)
        
        # 恢复原始方法
        self.server.query = original_query

# ------------------------ 主程序 ------------------------
if __name__ == "__main__":
    # 示例用法
    leaked_hashes = [
        compute_password_hash("password123"),
        compute_password_hash("123456"),
        compute_password_hash("admin123")
    ]
    
    server = PasswordCheckupServer(leaked_hashes)
    client = PasswordCheckupClient()
    
    passwords_to_check = [
        "password123",    # 已泄露
        "securePass123",  # 未泄露
        "admin123",       # 已泄露
        "anotherPassword" # 未泄露
    ]
    
    print("Google Password Checkup 协议演示")
    print("=" * 40)
    
    for pwd in passwords_to_check:
        result = client.check_password(pwd, server)
        status = "已泄露" if result else "安全"
        print(f"密码: {pwd:20} 状态: {status}")
    
    print("\n运行单元测试...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)