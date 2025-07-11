#!/bin/bash

# 1. 安装必要依赖
npm install circom circomlib circomlibjs ffjavascript snarkjs

# 2. 编译电路
circom poseidon2.circom --r1cs --wasm --sym -v

# 3. 生成输入文件
node generate_input.js

# 4. 生成见证文件
node poseidon2_js/generate_witness.js poseidon2_js/poseidon2.wasm input.json witness.wtns

# 5. 下载可信设置文件（如果不存在）
if [ ! -f pot12_final.ptau ]; then
    wget https://hermez.s3-eu-west-1.amazonaws.com/powersOfTau28_hez_final_12.ptau -O pot12_final.ptau
fi

# 6. 生成Groth16密钥
snarkjs groth16 setup poseidon2.r1cs pot12_final.ptau poseidon2_0000.zkey
snarkjs zkey contribute poseidon2_0000.zkey poseidon2_final.zkey --name="Contributor" -v

# 7. 导出验证密钥
snarkjs zkey export verificationkey poseidon2_final.zkey verification_key.json

# 8. 生成证明
snarkjs groth16 prove poseidon2_final.zkey witness.wtns proof.json public.json

# 9. 验证证明
snarkjs groth16 verify verification_key.json public.json proof.json

# 10. 生成Solidity验证合约
snarkjs zkey export solidityverifier poseidon2_final.zkey verifier.sol

echo "All steps completed successfully!"