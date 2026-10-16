// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * ============================================================================
 * HEALTHCARE RECORD MANAGEMENT USING BLOCKCHAIN
 * Solidity Smart Contract for Remix IDE (https://remix.ethereum.org)
 * ============================================================================
 * 
 * CORE VIVA EXPLANATION:
 * 1. MySQL Database: Stores full patient clinical data off-chain (Name, Age, Disease, Prescription).
 * 2. SHA-256 Hashing: Generates an immutable 64-character digital fingerprint.
 * 3. Smart Contract: Stores the Patient ID + SHA-256 hash + timestamp + doctor address.
 * 4. Verification: Recalculates hash from MySQL and compares with this on-chain hash.
 *    - Matching hashes  -> Record Verified (No tampering)
 *    - Differing hashes -> Record Modified (Tampering detected)
 * ============================================================================
 */
contract HealthcareRecord {

    // Record proof structure stored on the blockchain
    struct RecordProof {
        string recordHash;    // SHA-256 hash
        uint256 timestamp;    // Block timestamp
        address recordedBy;   // Caller wallet address
        bool exists;          // Quick check flag
    }

    // Mapping: Patient ID => RecordProof
    mapping(string => RecordProof) private records;

    // Total count of records stored
    uint256 public totalRecords;

    // Contract deployer
    address public owner;

    // Event emitted when a hash is stored (recorded in block receipts)
    event HashStored(
        string indexed patientId,
        string recordHash,
        uint256 timestamp,
        address indexed recordedBy
    );

    constructor() {
        owner = msg.sender;
    }

    /**
     * @dev Store or update the SHA-256 hash for a patient record
     * @param patientId e.g. "P001"
     * @param recordHash e.g. 64-char hex SHA-256 string
     */
    function storeHash(string memory patientId, string memory recordHash) public {
        require(bytes(patientId).length > 0, "Patient ID cannot be empty");
        require(bytes(recordHash).length > 0, "Record hash cannot be empty");

        if (!records[patientId].exists) {
            totalRecords++;
        }

        records[patientId] = RecordProof({
            recordHash: recordHash,
            timestamp: block.timestamp,
            recordedBy: msg.sender,
            exists: true
        });

        emit HashStored(patientId, recordHash, block.timestamp, msg.sender);
    }

    /**
     * @dev Retrieve the stored hash for verification
     * @param patientId e.g. "P001"
     */
    function getHash(string memory patientId) public view returns (string memory) {
        require(records[patientId].exists, "No hash stored for this patient ID");
        return records[patientId].recordHash;
    }

    /**
     * @dev Retrieve full audit details (hash, timestamp, address)
     * @param patientId e.g. "P001"
     */
    function getRecordDetails(string memory patientId) 
        public 
        view 
        returns (string memory recordHash, uint256 timestamp, address recordedBy) 
    {
        require(records[patientId].exists, "No hash stored for this patient ID");
        RecordProof memory r = records[patientId];
        return (r.recordHash, r.timestamp, r.recordedBy);
    }

    /**
     * @dev Check if a record exists
     * @param patientId e.g. "P001"
     */
    function hasHash(string memory patientId) public view returns (bool) {
        return records[patientId].exists;
    }
}
