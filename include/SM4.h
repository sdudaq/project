/**
 * @file SM4.h
 * @brief 国密SM4分组密码算法实现
 * @license MIT
 */

#ifndef SM4_H
#define SM4_H

#include <vector>
#include <cstdint>
#include <stdexcept>

class SM4 {
public:
    /**
     * @brief 使用128位密钥初始化
     * @param key 16字节密钥向量
     * @throw std::invalid_argument 密钥长度错误时抛出
     */
    explicit SM4(const std::vector<uint8_t>& key);
    
    /**
     * @brief ECB模式加密
     * @param plaintext 明文(长度需为16的倍数)
     * @return 密文数据
     */
    std::vector<uint8_t> encrypt(const std::vector<uint8_t>& plaintext);
    
    /**
     * @brief ECB模式解密
     * @param ciphertext 密文(长度需为16的倍数) 
     * @return 明文数据
     */
    std::vector<uint8_t> decrypt(const std::vector<uint8_t>& ciphertext);

private:
    uint32_t rk[32]; // 轮密钥

    void generateRoundKeys(const std::vector<uint8_t>& key);
    uint32_t F(uint32_t X0, uint32_t X1, uint32_t X2, uint32_t X3, uint32_t rk);
    uint32_t T(uint32_t X);
    uint32_t T_prime(uint32_t X);
    uint32_t L(uint32_t B);
    uint32_t L_prime(uint32_t B);
    uint32_t rotateLeft(uint32_t x, uint32_t n);
    std::vector<uint8_t> crypt(const std::vector<uint8_t>& input, bool isEncrypt);

    // 算法常量
    static const uint8_t SBOX[256];
    static const uint32_t FK[4];
    static const uint32_t CK[32];
};

#endif // SM4_H