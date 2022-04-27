// SPDX-License-Identifier: MIT
// infant level solidity, be gentle.
// lcfr.eth && @lcfr_eth

pragma solidity ^0.8.7;

import "@ensdomains/ens-contracts/contracts/ethregistrar/ETHRegistrarController.sol";

contract ENSBulkRegister {

    event log_named_string       (string key, string val);

    address baseRegistrarAddr = 0x283Af0B28c62C092C9727F1Ee09c02CA627EB7F5;
    ETHRegistrarController controller = ETHRegistrarController(baseRegistrarAddr);

    address owner;

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner {
        require(msg.sender == owner);
        _;
    }

    function updateRegistrarAddr(address _newRegistrar) external onlyOwner {
        baseRegistrarAddr = _newRegistrar;
    }

    function updateOwner(address _newOwner) external onlyOwner {
        owner = _newOwner;
    }

    function emergencyWithdraw(address _payee) external onlyOwner {
        (bool sent, bytes memory data) = _payee.call{value: address(this).balance}("");
        require(sent, "Failed to send Ether");
    }

    function doCommitloop(bytes32[] memory _commitments) external {
        for ( uint i = 0; i < _commitments.length; ++i ) {
            controller.commit(_commitments[i]);
        }
    }

    function doRegisterloop(string[] memory _names, bytes32[] memory _secrets, uint256 _duration) external payable { 

        uint256 totalPrice = rentPriceLoop(_names, _duration);

        require(_names.length == _secrets.length, "names/secrets length mismatch");
        
        // could technically do this in the front end. remove totalPrice/rentPriceLoop. 
        // calculate totalPrice in frontend to send as value. Test gas cost to decide.
        
        require(msg.value >= totalPrice, "Not enough Ether sent.");
        
        for( uint i = 0; i < _names.length; ++i ) {
            uint price = controller.rentPrice(_names[i], _duration);
            controller.register{value: price}(_names[i], msg.sender, _duration, _secrets[i]);
            emit log_named_string("NameRegistered: ", _names[i]);
        }
        
        // check if any extra eth and refund user.
        
    }

    function rentPriceLoop(string[] memory _name, uint256 _duration) public view returns(uint total) {
        uint256 total;
        for (uint i = 0; i < _name.length; ++i {
            total += controller.rentPrice(_name[i], _duration);
        }
        return total;
    }

}
