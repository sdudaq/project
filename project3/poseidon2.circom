pragma circom 2.0.0;

include "circomlib/poseidon.circom";

template Poseidon2Hash() {
    signal input preimage[2];
    signal input hashOut;

    component poseidon = Poseidon(2);
    for (var i = 0; i < 2; i++) {
        poseidon.inputs[i] <== preimage[i];
    }

    hashOut === poseidon.out;
}

component main = Poseidon2Hash();
