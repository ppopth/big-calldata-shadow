#!/usr/bin/env node

const yargs = require('yargs');
const fs = require('fs');
const Web3 = require('web3');

const argv = yargs
    .option('endpoint', {
        description: 'HTTP endpoint of the node which you want to use to deploy the contract',
        type: 'string',
        demandOption: true,
        requiresArg: true,
    })
    .option('build-dir', {
        description: 'Directory containing the abi and the bytecode',
        type: 'string',
        demandOption: true,
        requiresArg: true,
    })
    .option('address-out', {
        description: 'The file path to write the contract address',
        type: 'string',
        demandOption: true,
        requiresArg: true,
    })
    .help()
    .alias('help', 'h').argv;

(async function() {
    const web3 = new Web3(argv.endpoint);
    const accounts = await web3.eth.getAccounts();

    const abi = JSON.parse(fs.readFileSync(argv.buildDir + '/BytesContract.abi'));
    const bin = fs.readFileSync(argv.buildDir + '/BytesContract.bin');
    const undeployed = new web3.eth.Contract(abi);

    const contract = await undeployed
        .deploy({ data: '0x' + bin })
        .send({
            from: accounts[0],
            gasPrice: '147000000000',
        })
        .once('transactionHash', hash => {
            console.log('transaction', hash);
        })
        .once('receipt', receipt => {
            console.log('block_number', receipt.blockNumber);
        });

    console.log('address', contract.options.address);
    fs.writeFileSync(argv.addressOut, contract.options.address);
    process.exit();
})();
