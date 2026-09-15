// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract EvidenceRegistry {
    struct EvidenceRecord {
        bytes32 evidenceHash;
        uint256 timestamp;
        address registrant;
        bool exists;
    }

    mapping(bytes32 => EvidenceRecord) private records;

    event EvidenceRegistered(bytes32 indexed evidenceId, bytes32 indexed evidenceHash, uint256 timestamp, address indexed registrant);

    function registerEvidenceHash(bytes32 evidenceId, bytes32 evidenceHash) external {
        require(evidenceId != bytes32(0), "evidence id required");
        require(evidenceHash != bytes32(0), "hash required");
        require(!records[evidenceId].exists, "evidence already registered");
        records[evidenceId] = EvidenceRecord(evidenceHash, block.timestamp, msg.sender, true);
        emit EvidenceRegistered(evidenceId, evidenceHash, block.timestamp, msg.sender);
    }

    function verifyEvidenceHash(bytes32 evidenceId, bytes32 evidenceHash) external view returns (bool) {
        require(records[evidenceId].exists, "evidence not found");
        return records[evidenceId].evidenceHash == evidenceHash;
    }

    function getEvidenceRecord(bytes32 evidenceId) external view returns (bytes32 evidenceHash, uint256 timestamp, address registrant) {
        require(records[evidenceId].exists, "evidence not found");
        EvidenceRecord memory record = records[evidenceId];
        return (record.evidenceHash, record.timestamp, record.registrant);
    }
}
