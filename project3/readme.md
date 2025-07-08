# Project3: Poseidon2 Hash Circuit with Circom + Groth16

## 介绍

本项目用 Circom 实现了 Poseidon2 哈希电路，参数(t=3)，支持 Groth16 证明生成。

## 文件说明

- `poseidon2.circom`：Poseidon2电路代码
- `generate_input.js`：Node脚本，生成正确的`input.json`
- `input.json`：电路输入示例（私密输入+公开哈希）
- `run.sh`：自动化编译+证明流程脚本

## 环境准备

需要 Node.js，npm 以及 circom，snarkjs 全局安装

```bash
npm install -g circom snarkjs
npm install circomlibjs ffjavascript
