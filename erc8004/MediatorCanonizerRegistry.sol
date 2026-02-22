// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Mediator-Canonizer Validation Registry
/// @notice ERC-8004 Validation Authority — canonical doctrine on-chain
/// @dev Operator: 0xeb65c54ee09AAc48612Dc77e6d106005547dF67A

contract MediatorCanonizerRegistry {

    address public operator;
    string public constant CMP_DOI = "10.5281/zenodo.18732820";
    string public constant VERSION = "1.0.0";

    struct CanonArtifact {
        string domain;
        string status;
        bytes32 hash;
        uint256 timestamp;
        string cmp_doi;
        string cite_as;
    }

    mapping(bytes32 => CanonArtifact) public artifacts;
    bytes32[] public artifactIndex;

    event ArtifactFrozen(
        bytes32 indexed hash,
        string domain,
        string status,
        uint256 timestamp,
        string cite_as
    );

    modifier onlyOperator() {
        require(msg.sender == operator, "Not operator");
        _;
    }

    constructor() {
        operator = 0xeb65c54ee09AAc48612Dc77e6d106005547dF67A;
    }

    function registerArtifact(
        string calldata domain,
        string calldata status,
        bytes32 hash,
        string calldata cite_as
    ) external onlyOperator {
        require(artifacts[hash].timestamp == 0, "Artifact already registered");

        artifacts[hash] = CanonArtifact({
            domain: domain,
            status: status,
            hash: hash,
            timestamp: block.timestamp,
            cmp_doi: CMP_DOI,
            cite_as: cite_as
        });

        artifactIndex.push(hash);

        emit ArtifactFrozen(hash, domain, status, block.timestamp, cite_as);
    }

    function verify(bytes32 hash) external view returns (bool exists, string memory domain, string memory status, uint256 timestamp) {
        CanonArtifact memory a = artifacts[hash];
        return (a.timestamp > 0, a.domain, a.status, a.timestamp);
    }

    function totalArtifacts() external view returns (uint256) {
        return artifactIndex.length;
    }
}
