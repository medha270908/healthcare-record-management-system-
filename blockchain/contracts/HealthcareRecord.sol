// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title HealthcareRecord
 * @dev Smart contract for storing cryptographic hashes of healthcare records.
 * Designed for deployment via Remix IDE or Hardhat.
 * 
 * ARCHITECTURE & VIVA POINTS:
 * 1. The blockchain NEVER stores sensitive patient medical data.
 * 2. Sensitive medical data resides securely in off-chain MySQL database.
 * 3. Only the Patient ID, SHA-256 record hash, block timestamp, and doctor address are recorded on-chain.
 * 4. Verification compares the recalculated MySQL hash with the immutable blockchain hash.
 */
contract HealthcareRecord {

    // Structure holding record verification metadata
    struct RecordProof {
        string recordHash;    // SHA-256 hash of patient record
        uint256 timestamp;    // Block timestamp when hash was anchored
        address recordedBy;   // Wallet address of the doctor/caller
        bool exists;          // Existence flag
    }

    // Mapping: Patient ID (e.g., "P001") => RecordProof
    mapping(string => RecordProof) private records;

    // Total count of registered hashes on-chain
    uint256 public totalRecords;

    // Owner of the contract (the deployer)
    address public owner;

    // Event emitted whenever a hash is anchored to the ledger
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
     * @notice Store or update the SHA-256 hash for a given Patient ID.
     * @param patientId Unique identifier of the patient (e.g. "P001")
     * @param recordHash SHA-256 cryptographic digest of the MySQL record
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
     * @notice Retrieve the stored SHA-256 hash for a patient.
     * @param patientId Patient identifier
     * @return recordHash Stored cryptographic hash
     */
    function getHash(string memory patientId) public view returns (string memory) {
        require(records[patientId].exists, "No hash stored for this patient ID");
        return records[patientId].recordHash;
    }

    /**
     * @notice Retrieve complete audit details: hash, timestamp, and recorder address.
     * @param patientId Patient identifier
     * @return recordHash The stored SHA-256 hash
     * @return timestamp The UNIX timestamp when stored
     * @return recordedBy Ethereum address of the sender
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
     * @notice Checks if a hash exists for a given patient ID without reverting.
     * @param patientId Patient identifier
     * @return bool True if hash exists, false otherwise
     */
    function hasHash(string memory patientId) public view returns (bool) {
        return records[patientId].exists;
    }
}
