
# Healthcare Record Management Using Blockchain

MySQL → Flask → SHA-256 → Smart Contract → Blockchain, and verification
by re-hashing and comparing.

---

## 1. Architecture (simple explanation)

```
Patient Details
      |
      v
MySQL Database   <---- stores the ACTUAL patient data (sensitive)
      |
      v
Flask Backend (Python)
      |
      v
SHA-256 Hash Generation   <---- fingerprint of the record
      |
      v
Solidity Smart Contract  --->  Blockchain (Hardhat local network)
                                 stores ONLY: Patient ID + hash
```

Verification:
```
MySQL record --> generate hash again --> compare with hash on blockchain
Same hash  -> "Record Verified"
Diff hash  -> "Record Modified"
```


