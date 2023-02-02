// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.17;

contract BytesContract {
    uint public size;
    function update(bytes calldata b) external {
        size = b.length;
    }
}
