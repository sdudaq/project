#include <iostream>
#include <vector>
#include <cstring>
#include <iomanip>
#include <sstream>
#include <array>

class SM3 {
public:
    std::vector<uint8_t> hash(const std::string& message) {
        return hash(reinterpret_cast<const uint8_t*>(message.c_str()), message.length());
    }

    std::vector<uint8_t> hash(const uint8_t* message, size_t length) {
        // 初始化向量
        std::array<uint32_t, 8> V = {
            0x7380166F, 0x4914B2B9, 0x172442D7, 0xDA8A0600,
            0xA96F30BC, 0x163138AA, 0xE38DEE4D, 0xB0FB0E4E
        };

        // 消息填充
        auto padded = padding(message, length);

        // 处理每个512位(64字节)分组
        for (size_t i = 0; i < padded.size(); i += BLOCK_SIZE) {
            compress(V, &padded[i]);
        }

        // 将结果转换为字节数组
        std::vector<uint8_t> digest(DIGEST_SIZE);
        for (size_t i = 0; i < V.size(); ++i) {
            digest[i*4]   = static_cast<uint8_t>(V[i] >> 24);
            digest[i*4+1] = static_cast<uint8_t>(V[i] >> 16);
            digest[i*4+2] = static_cast<uint8_t>(V[i] >> 8);
            digest[i*4+3] = static_cast<uint8_t>(V[i]);
        }

        return digest;
    }

private:
    static constexpr size_t BLOCK_SIZE = 64;
    static constexpr size_t DIGEST_SIZE = 32;

    // 循环左移
    static uint32_t rotl(uint32_t x, uint32_t n) {
        return (x << n) | (x >> (32 - n));
    }

    // 置换函数P0
    static uint32_t P0(uint32_t X) {
        return X ^ rotl(X, 9) ^ rotl(X, 17);
    }

    // 置换函数P1
    static uint32_t P1(uint32_t X) {
        return X ^ rotl(X, 15) ^ rotl(X, 23);
    }

    // 常量函数Tj
    static constexpr uint32_t T(int j) {
        return j < 16 ? 0x79CC4519 : 0x7A879D8A;
    }

    // 布尔函数FF
    static uint32_t FF(uint32_t X, uint32_t Y, uint32_t Z, int j) {
        return j < 16 ? X ^ Y ^ Z : (X & Y) | (X & Z) | (Y & Z);
    }

    // 布尔函数GG
    static uint32_t GG(uint32_t X, uint32_t Y, uint32_t Z, int j) {
        return j < 16 ? X ^ Y ^ Z : (X & Y) | ((~X) & Z);
    }

    // 消息填充
    std::vector<uint8_t> padding(const uint8_t* message, size_t length) const {
        const size_t bit_length = length * 8;
        std::vector<uint8_t> padded(message, message + length);
        
        // 添加比特'1'
        padded.push_back(0x80);
        
        // 填充0直到长度≡448 mod 512
        while ((padded.size() * 8 + 64) % 512 != 0) {
            padded.push_back(0x00);
        }
        
        // 添加原始长度(64位大端整数)
        for (int i = 7; i >= 0; --i) {
            padded.push_back(static_cast<uint8_t>(bit_length >> (8 * i)));
        }

        return padded;
    }

    // 消息扩展
    void expand(const uint8_t* block, std::array<uint32_t, 68>& W, 
                std::array<uint32_t, 64>& W_) const {
        // 将消息分组划分为16个字
        for (int j = 0; j < 16; ++j) {
            W[j] = (static_cast<uint32_t>(block[j*4]) << 24) |
                   (static_cast<uint32_t>(block[j*4+1]) << 16) |
                   (static_cast<uint32_t>(block[j*4+2]) << 8) |
                   static_cast<uint32_t>(block[j*4+3]);
        }
        
        // 生成W16-W67
        for (int j = 16; j < 68; ++j) {
            W[j] = P1(W[j-16] ^ W[j-9] ^ rotl(W[j-3], 15)) ^ 
                   rotl(W[j-13], 7) ^ W[j-6];
        }
        
        // 生成W'0-W'63
        for (int j = 0; j < 64; ++j) {
            W_[j] = W[j] ^ W[j+4];
        }
    }

    // 压缩函数
    void compress(std::array<uint32_t, 8>& V, const uint8_t* block) const {
        std::array<uint32_t, 68> W;
        std::array<uint32_t, 64> W_;
        expand(block, W, W_);
        
        uint32_t A = V[0], B = V[1], C = V[2], D = V[3];
        uint32_t E = V[4], F = V[5], G = V[6], H = V[7];
        
        for (int j = 0; j < 64; ++j) {
            const uint32_t T_j = rotl(T(j), j);
            const uint32_t SS1 = rotl((rotl(A, 12) + E + T_j) & 0xFFFFFFFF, 7);
            const uint32_t SS2 = SS1 ^ rotl(A, 12);
            const uint32_t TT1 = (FF(A, B, C, j) + D + SS2 + W_[j]) & 0xFFFFFFFF;
            const uint32_t TT2 = (GG(E, F, G, j) + H + SS1 + W[j]) & 0xFFFFFFFF;
            
            D = C;
            C = rotl(B, 9);
            B = A;
            A = TT1;
            H = G;
            G = rotl(F, 19);
            F = E;
            E = P0(TT2);
        }
        
        V[0] ^= A; V[1] ^= B; V[2] ^= C; V[3] ^= D;
        V[4] ^= E; V[5] ^= F; V[6] ^= G; V[7] ^= H;
    }
};

// 辅助函数：将字节数组转换为十六进制字符串
std::string bytesToHex(const std::vector<uint8_t>& bytes) {
    std::ostringstream oss;
    oss << std::hex << std::setfill('0');
    for (uint8_t b : bytes) {
        oss << std::setw(2) << static_cast<int>(b);
    }
    return oss.str();
}

int main() {
    SM3 sm3;
    
    // 测试用例
    const std::vector<std::pair<std::string, std::string>> testCases = {
        {"abc", "66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0"},
        {"abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd", 
         "debe9ff92275b8a138604889c18e5a4d6fdb70e5387e5765293dcba39c0c5732"},
        {"HelloSM3", "36065686c1859012d3b504ecee7ae52e5f0fdf3089a0854811f613f77599a4cd"}
    };
    
    for (const auto& [input, expected] : testCases) {
        auto digest = sm3.hash(input);
        std::string hexDigest = bytesToHex(digest);
        
        std::cout << "Input: \"" << input << "\"\n"
                  << "Output: " << hexDigest << "\n"
                  << "Expected: " << expected << "\n"
                  << "Match: " << (hexDigest == expected) << "\n\n";
    }
    
    return 0;
}