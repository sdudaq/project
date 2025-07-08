/**
 * @file test.cpp
 * @brief SM4算法测试用例
 */

#include "../include/SM4.h"
#include <iostream>
#include <iomanip>

void printHex(const std::vector<uint8_t>& data) {
    for (uint8_t b : data) {
        std::cout << std::hex << std::setw(2) << std::setfill('0') 
                  << static_cast<int>(b) << " ";
    }
    std::cout << std::dec << "\n";
}

void testStandardVector() {
    std::vector<uint8_t> key = {
        0x01,0x23,0x45,0x67,0x89,0xab,0xcd,0xef,
        0xfe,0xdc,0xba,0x98,0x76,0x54,0x32,0x10
    };
    std::vector<uint8_t> plaintext = {
        0x01,0x23,0x45,0x67,0x89,0xab,0xcd,0xef,
        0xfe,0xdc,0xba,0x98,0x76,0x54,0x32,0x10
    };

    SM4 sm4(key);
    auto ciphertext = sm4.encrypt(plaintext);
    auto decrypted = sm4.decrypt(ciphertext);

std::cout << "Standard test vector:\n";
std::cout << "Plaintext: "; printHex(plaintext);
std::cout << "Ciphertext: "; printHex(ciphertext);
std::cout << "Decrypted: "; printHex(decrypted);
std::cout << (plaintext == decrypted ? "Success" : "Failure") << "\n\n";
}

int main() {
    try {
        testStandardVector();
    } catch (const std::exception& e) {
        std::cerr << "test error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}