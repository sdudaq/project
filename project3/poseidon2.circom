pragma circom 2.0.0;

include "node_modules/circomlib/circuits/poseidon.circom";

template Poseidon2Hash() {
    // 隐私输入：哈希原像（2个域元素）
    signal input preimage[2];
    
    // 公开输出：哈希值
    signal output hash;
    
    // 使用Poseidon哈希组件（输入数量为2）
    component hasher = Poseidon(2);
    
    // 连接输入
    hasher.inputs[0] <== preimage[0];
    hasher.inputs[1] <== preimage[1];
    
    // 连接输出
    hash <== hasher.out;
}

component main {public [hash]} = Poseidon2Hash();