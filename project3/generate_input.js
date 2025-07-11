const poseidon = require("circomlibjs").poseidon;
const ff = require("ffjavascript");
const fs = require("fs");

async function main() {
  const F = await ff.buildBn128();

  // 测试输入数据（2个域元素）
  const preimage = [123456789, 987654321];

  // 计算Poseidon哈希
  const hash = poseidon(preimage);
  const hashStr = F.toString(hash);

  // 生成输入文件
  const input = {
    preimage: preimage.map(x => x.toString()),
    hash: hashStr
  };

  fs.writeFileSync("input.json", JSON.stringify(input, null, 2));
  console.log("input.json generated with hash:", hashStr);
}

main().catch(console.error);