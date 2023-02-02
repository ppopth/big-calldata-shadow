#!/usr/bin/env bash

source ./vars.env
set -eu

SOLIDITY_DEPOSIT_CONTRACT_SOURCE=./contract/bytes_contract.sol

solc --bin --abi --overwrite -o build $SOLIDITY_DEPOSIT_CONTRACT_SOURCE

rm -rf $ROOT
export NODE_COUNT=$NODE_COUNT
export VALIDATOR_COUNT=$VALIDATOR_COUNT
export GETH_CMD=../go-ethereum/build/bin/geth
cd ethereum-shadow; GENONLY=1 ROOT=../$ROOT ./run.sh; cd ..

HTTP_PORT=3013
SHADOW_CONFIG_FILE=$ROOT/shadow.yaml
SHADOW_DIR=$ROOT/shadow
SECONDS_PER_SLOT=$(yq .SECONDS_PER_SLOT $ROOT/consensus/config.yaml)

CONTRACT_DEPLOY_STARTTIME=$START_TIME
UPDATE_STARTTIME=$(expr $CONTRACT_DEPLOY_STARTTIME + $SECONDS_PER_SLOT \* 5)

# Allow insecure HTTP to node1
yq -i ".hosts.node1.processes[0].args += \"--http --http.port $HTTP_PORT --allow-insecure-unlock\"" $SHADOW_CONFIG_FILE
echo "Enabled HTTP endpoint of node1"

# Deploy the contract
env="NODE_PATH=$(realpath ./node_modules)"
args="$(realpath ./src/deploy-contract.js) \
--endpoint http://localhost:$HTTP_PORT \
--build-dir $(realpath ./build) \
--address-out $(realpath $ROOT/contract-address)"
yq -i ".hosts.node1.processes += { \
    \"path\": \"node\", \
    \"environment\": \"$env\", \
    \"args\": \"$args\", \
    \"start_time\": $CONTRACT_DEPLOY_STARTTIME \
}" $SHADOW_CONFIG_FILE
echo "Added contract deploy process in node1"

shadow -p $PARALLELISM -d $SHADOW_DIR $SHADOW_CONFIG_FILE --use-memory-manager false --progress true > $ROOT/shadow.log
