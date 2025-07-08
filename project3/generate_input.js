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
    hashOut: hashStr
  };

  fs.writeFileSync("input.json", JSON.stringify(input, null, 2));
  console.log("input.json generated with hash:", hashStr);
}

main();
