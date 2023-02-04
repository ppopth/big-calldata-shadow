# Simulate Ethereum network with big calldata

We want to run the simulation see the network effect of producing a large block. Currently with the Bellatrix fork, we can do that by sending
a transaction with big calldata.

This simulation relies heavily on [ethereum-shadow](https://github.com/ppopth/ethereum-shadow). It's also helpful to read more about it before
running the simulation.

## Installation

Please follow https://github.com/ppopth/ethereum-shadow#install-dependencies to install the required dependencies. Then follow the following steps.

```bash
git clone https://github.com/ppopth/big-calldata-shadow.git
cd big-calldata-shadow
git submodule update --init --depth 1

# Build the customized geth
cd go-ethereum
make geth
cd ..

# Install node modules
npm install
```

## Run the simulation

```bash
./run.sh
```
By default, the number of nodes will be 10, the number of validators will be 100, and the size of the calldata will be 2MB.
You can change them by setting the environment variables.
```bash
# 102400 is 100KB
LENGTH=102400 NODE_COUNT=20 VALIDATOR_COUNT=150 ./run.sh
```

## Network topology

Currently we set each node to have 20Mbps for downloading and another 20Mbps for uploading. Each pair of nodes has the latency of 100ms
(which is the average latency of the nodes in discv5 network, see https://notes.ethereum.org/@pop/discv5-network-measurement).

In the future, we have a plan to assign each node the physical location so that the latencies among nodes will be more realistic.

## Customized go-ethereum

You can note that we have go-ethereum as a submodule and we compile it from source. That is because we want to patch go-ethereum in order to
1. Increase all the limits that are necessary to send a large transaction.
2. Disable transaction broadcasting because our transaction is large and it will eat bandwidth in the Execution Layer instead of just the Consensus Layer.

## What happens in the network

In order to send a transaction with big calldata, we need to have a contract that accepts a big-calldata transaction first. The Solidity code of the
contract looks as follows.

```solidity
contract BytesContract {
    uint public size;
    function update(bytes calldata b) external {
        size = b.length;
    }
}
```

As mentioned earlier, we disable transaction broadcasting in go-ethereum, so, when we need to send a transaction to the chain, it will be on the chain
only when the node to which we send the transaction is the proposer. So, if we send a transaction to a node, we need to wait until that node becomes
a proposer.

In order to make sure the contract is deployed quickly, we have every node create and send a contract-creation transaction and include it in the block
when it becomes a proposer. This results to a lot of contracts created in the block chain (I know that there is a way to create only one contract, but
it's easy to do this for now). You can see the lines like the following when you run the simulation.
```
Added contract deploy process in node1
Added contract deploy process in node2
Added contract deploy process in node3
...
```

After the contract is deployed, we will send a big-calldata transaction which will call the `update` function in the contract. For the same reason, this
time, we also have many nodes create and send the transaction as well (but not every node because otherwise we have too many big-calldata transactions
created in the network). We do it in enough nodes just to have less than 10% of probability that there is no big-calldata transaction included in the
block chain at all. If you run the simulation and you don't see any such transaction in the chain at all, it means that you are in that 10% and
you should run the simulation again. You can see the lines like the following if the node is assigned to create a transaction.
```
Added bytes update process in node1
```

You can see the transaction of which node is included in the chain by looking at the file `./data/shadow/hosts/node{id}/node{id}.node.1005.stdout`.
If the transaction is included in the chain, the file should look like this.
```
7:06:00 AM
contract_address 0x43f352Cca3ca64eDbD1f5fD47cedf9C63eC9aCf4
transaction 0x00a9139d0a7c60442448e0df6917e97b7ec8aa099403a71a036920c5cbb04945
block_number 49
block_hash 0x77907894c6d4956a4a58f43bbd5208f3477a7b7893e211f48c60f1d0a075ef23
status true
7:09:36 AM
```
If the transaction is not included, the file will not have the `block_number`, `block_hash`, and the `status`.

## Simulation result

Please look at https://github.com/ppopth/ethereum-shadow#simulation-result to see the relevant files you probably want to look at.

## Scale to hundreds of nodes

Please look at https://github.com/ppopth/ethereum-shadow#scale-to-hundreds-of-nodes to see how to scale the simulation to a lot of nodes.
