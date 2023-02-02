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
STOP_TIME=$(yq .general.stop_time $SHADOW_CONFIG_FILE)

CONTRACT_DEPLOY_STARTTIME=$START_TIME
UPDATE_STARTTIME=$(expr $CONTRACT_DEPLOY_STARTTIME + $SECONDS_PER_SLOT \* 5)

# Allow insecure HTTP to every node
for node in $(seq 1 $NODE_COUNT); do
    yq -i ".hosts.node$node.processes[0].args += \"--http --http.port $HTTP_PORT --allow-insecure-unlock\"" $SHADOW_CONFIG_FILE
    echo "Enabled HTTP endpoint of node$node"
done

# Deploy the contract in every node so that the contract will be deployed quickly
for node in $(seq 1 $NODE_COUNT); do
    env="NODE_PATH=$(realpath ./node_modules)"
    args="$(realpath ./src/deploy-contract.js) \
--endpoint http://localhost:$HTTP_PORT \
--build-dir $(realpath ./build) \
--address-out $(realpath $ROOT/contract-address)"
    yq -i ".hosts.node$node.processes += { \
        \"path\": \"node\", \
        \"environment\": \"$env\", \
        \"args\": \"$args\", \
        \"start_time\": $CONTRACT_DEPLOY_STARTTIME \
    }" $SHADOW_CONFIG_FILE
    echo "Added contract deploy process in node$node"
done

# The math here is to make sure that there will be at least one bytes update
# with high probability.
TIME_LEFT=$(expr $STOP_TIME - $UPDATE_STARTTIME)
SLOTS_LEFT=$(expr $TIME_LEFT / $SECONDS_PER_SLOT + 1)
UPDATE_NODE_COUNT=$(expr $NODE_COUNT \* 2 / $SLOTS_LEFT + 1)

# Update the bytes in the contract
for node in $(seq 1 $UPDATE_NODE_COUNT); do
    env="NODE_PATH=$(realpath ./node_modules)"
    args="$(realpath ./src/update.js) \
--endpoint http://localhost:$HTTP_PORT \
--build-dir $(realpath ./build) \
--address-file $(realpath $ROOT/contract-address) \
--length 2097152"
    yq -i ".hosts.node$node.processes += { \
        \"path\": \"node\", \
        \"environment\": \"$env\", \
        \"args\": \"$args\", \
        \"start_time\": $UPDATE_STARTTIME \
    }" $SHADOW_CONFIG_FILE
    echo "Added bytes update process in node$node"
done

shadow -p $PARALLELISM -d $SHADOW_DIR $SHADOW_CONFIG_FILE --use-memory-manager false --progress true > $ROOT/shadow.log
