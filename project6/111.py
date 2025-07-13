import hashlib
import hmac
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
import os

class PasswordCheckupClient:
    """
    Google Password Checkup协议客户端实现
    对应论文Figure 2的Client步骤
    """
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        
    def generate_credentials(self):
        """生成协议所需的凭证（对应论文步骤1）"""
        # 使用HKDF派生密钥
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'password-checkup-key',
            backend=default_backend()
        )
        secret_key = hkdf.derive(self.password.encode())
        
        # 计算u = HMAC-SHA256(key: secret_key, msg: username)
        h = hmac.new(secret_key, self.username.encode(), hashlib.sha256)
        u = h.digest()
        
        # 计算v = SHA256(password)
        v = hashlib.sha256(self.password.encode()).digest()
        
        return u, v

class PasswordCheckupServer:
    """
    服务端实现（对应论文步骤2-4）
    注：实际部署中应采用分段布隆过滤器等优化
    """
    
    def __init__(self, leaked_creds_db):
        """
        :param leaked_creds_db: 已泄露的凭证数据库 (u, v)列表
        """
        self.leaked_db = set(leaked_creds_db)
        
    def build_bloom_filter(self):
        """构建布隆过滤器（简化实现，实际应使用高效数据结构）"""
        # 注：论文中使用更高效的XOR布隆过滤器
        self.filter = set()
        for u, v in self.leaked_db:
            # 论文中的h = H(u) XOR v
            h_u = hashlib.sha256(u).digest()
            h_xor = bytes(a ^ b for a, b in zip(h_u, v))
            self.filter.add(h_xor)
    
    def check_password(self, client_u, client_v):
        """检查密码是否泄露（步骤3-4）"""
        # 计算h = H(client_u) XOR client_v
        h_u = hashlib.sha256(client_u).digest()
        h_xor = bytes(a ^ b for a, b in zip(h_u, client_v))
        
        # 检查是否在布隆过滤器中（简化实现）
        return h_xor in self.filter

# 使用示例
if __name__ == "__main__":
    # 模拟已泄露的凭证库
    leaked_database = [
        (b'u1_leaked', b'v1_leaked'),  # 实际应为(hash, hash)
        (b'u2_leaked', b'v2_leaked')
    ]
    
    # 初始化服务端
    server = PasswordCheckupServer(leaked_database)
    server.build_bloom_filter()
    
    # 客户端检查密码
    client = PasswordCheckupClient("user123", "mypassword")
    u, v = client.generate_credentials()
    
    # 检查是否泄露
    is_leaked = server.check_password(u, v)
    print(f"密码泄露状态: {'⚠️ 存在泄露风险' if is_leaked else '✅ 安全'}")
    
    # 测试已知泄露案例
    test_client = PasswordCheckupClient("leaked_user", "password123")
    test_u, test_v = test_client.generate_credentials()
    server.check_password(test_u, test_v)  # 应返回True