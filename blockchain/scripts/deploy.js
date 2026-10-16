const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

// ============================================================
// This script:
// 1. Deploys the HealthcareRecord smart contract to the
//    Hardhat local blockchain (started with "npx hardhat node").
// 2. Saves the deployed contract's ADDRESS and ABI into
//    deployment.json, inside the blockchain/ folder.
//
// The Flask backend (app.py) reads deployment.json so it knows
// which contract to talk to and which functions it has.
// ============================================================
async function main() {
  const HealthcareRecord = await hre.ethers.getContractFactory("HealthcareRecord");
  const contract = await HealthcareRecord.deploy();
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  console.log("HealthcareRecord contract deployed to:", address);

  // Get the contract ABI (the "interface list" describing
  // storeHash / getHash / hasHash) from the compiled artifact.
  const artifact = await hre.artifacts.readArtifact("HealthcareRecord");

  const deploymentInfo = {
    address: address,
    abi: artifact.abi,
  };

  const outputPath = path.join(__dirname, "..", "deployment.json");
  fs.writeFileSync(outputPath, JSON.stringify(deploymentInfo, null, 2));

  console.log("Saved contract address + ABI to:", outputPath);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
