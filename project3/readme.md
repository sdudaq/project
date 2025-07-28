# Project3: Poseidon2 Hash Circuit with Circom + Groth16

## 一、项目介绍

本项目使用 [Circom](https://docs.circom.io/) 编写了一个基于 Poseidon2 哈希函数的零知识证明电路，并使用 [snarkjs](https://github.com/iden3/snarkjs) 工具链进行 Groth16 证明系统的完整流程，包括编译电路、生成输入、生成见证、创建证明与验证证明，最终导出 Solidity 验证合约。

---

## 二、算法原理分析

### Poseidon2 哈希函数

Poseidon2 是一种适用于零知识证明系统的高效哈希函数。它专为低约束（low constraint）和高安全性而设计，构建在有穷域（Finite Field）上，避免了传统哈希函数（如 SHA256）在 zkSNARK 电路中的高成本。

本实验采用的 Poseidon2 变体参数为：

- 输入向量大小：`t = 3`（其中包含 2 个输入 + 1 个 capacity 元素）
- 安全参数：支持 SNARK-friendly 特性
- 算法核心操作包括：非线性 S-box（幂运算）、线性混合（矩阵乘法）、全轮/部分轮常数注入等

---

## 三、项目结构

```bash
.
├── compile.sh            # 编译和证明流程脚本
├── generate_input.js     # 生成 input.json 输入
├── input.json            # 哈希输入与期望输出
├── poseidon2.circom      # Poseidon2 Circom 电路文件
├── readme.md             # 实验说明与报告（本文件）
```
## 四、依赖环境
请确保已安装以下工具和库：
```
# 安装全局工具
npm install -g circom snarkjs

# 安装本地依赖
npm install circom circomlib circomlibjs ffjavascript snarkjs

# 安装全局工具
npm install -g circom snarkjs

# 安装本地依赖
npm install circom circomlib circomlibjs ffjavascript snarkjs
```
推荐 Node.js 版本：>=14.x

## 五、实验流程
以下为自动化脚本 run.sh 的执行步骤说明：

``` bash

# 1. 编译电路
circom poseidon2.circom --r1cs --wasm --sym

# 2. 生成输入文件
node generate_input.js

# 3. 生成 witness
node poseidon2_js/generate_witness.js poseidon2_js/poseidon2.wasm input.json witness.wtns

# 4. 下载 trusted setup 文件（首次使用）
wget https://hermez.s3-eu-west-1.amazonaws.com/powersOfTau28_hez_final_12.ptau -O pot12_final.ptau

# 5. Groth16 setup
snarkjs groth16 setup poseidon2.r1cs pot12_final.ptau poseidon2_0000.zkey
snarkjs zkey contribute poseidon2_0000.zkey poseidon2_final.zkey --name="Contributor"

# 6. 导出验证密钥
snarkjs zkey export verificationkey poseidon2_final.zkey verification_key.json

# 7. 生成证明
snarkjs groth16 prove poseidon2_final.zkey witness.wtns proof.json public.json

# 8. 验证证明
snarkjs groth16 verify verification_key.json public.json proof.json

```
## 六、输入生成脚本说明
generate_input.js 脚本通过 circomlibjs 的 Poseidon 实现计算输入数据对应的哈希值：
``` javascript
const poseidon = require("circomlibjs").poseidon;
const ff = require("ffjavascript");
const fs = require("fs");

async function main() {
  const F = await ff.buildBn128();
  const preimage = [123456789, 987654321];
  const hash = poseidon(preimage);
  const hashStr = F.toString(hash);

  const input = {
    preimage: preimage.map(x => x.toString()),
    hash: hashStr
  };

  fs.writeFileSync("input.json", JSON.stringify(input, null, 2));
  console.log("input.json generated with hash:", hashStr);
}

main().catch(console.error);

```
## 七、电路设计说明（poseidon2.circom）
``` circom
pragma circom 2.0.0;
include "node_modules/circomlib/circuits/poseidon.circom";

template Poseidon2Hash() {
    signal input preimage[2];
    signal output hash;

    component hasher = Poseidon(2);
    hasher.inputs[0] <== preimage[0];
    hasher.inputs[1] <== preimage[1];
    hash <== hasher.out;
}

component main {public [hash]} = Poseidon2Hash();

```
## 八、示例输入输出文件（input.json）
``` json
{
  "preimage": [
    "123456789",
    "987654321"
  ],
  "hash": "12345678901234567890"
}

```
注意：输出 hash 为字符串格式，其值由 poseidon(preimage) 动态生成，确保与 Circom 中电路一致。

## 九、验证成功实例
终端显示如下表示验证成功：
``` csharp
[INFO]  snarkJS: OK!

```
