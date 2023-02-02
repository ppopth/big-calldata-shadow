#!/usr/bin/env bash

SOLIDITY_DEPOSIT_CONTRACT_SOURCE=./contract/bytes_contract.sol

solc --bin --abi --overwrite -o build $SOLIDITY_DEPOSIT_CONTRACT_SOURCE
