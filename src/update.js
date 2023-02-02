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
    .option('address-file', {
        description: 'Contract address file',
        type: 'string',
        demandOption: true,
        requiresArg: true,
    })
    .option('length', {
        description: 'Length of the random bytes',
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
    const address = fs.readFileSync(argv.addressFile).toString();
    const contract = new web3.eth.Contract(abi, address);
    console.log((new Date()).toLocaleTimeString());

    console.log('contract_address', address);
    const data = web3.utils.randomHex(parseInt(argv.length));
    const transaction = contract.methods.update(data);
    const receipt = await transaction
        .send({
            from: accounts[0],
            gas: 100000000,
            gasPrice: '147000000000',
        })
        .once('transactionHash', hash => {
            console.log('transaction', hash);
        });
    console.log('block_number', receipt.blockNumber);
    console.log('block_hash', receipt.blockHash);
    console.log('status', receipt.status);
    console.log((new Date()).toLocaleTimeString());

    process.exit();
})();
