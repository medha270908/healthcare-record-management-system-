require("@nomicfoundation/hardhat-toolbox");

// ============================================================
// Hardhat configuration.
// Hardhat is used as a LOCAL DEVELOPMENT / TESTING blockchain network
// (running on http://127.0.0.1:8545).
// ============================================================
module.exports = {
  solidity: {
    compilers: [
      {
        version: "0.8.19",
        settings: {
          optimizer: {
            enabled: true,
            runs: 200,
          },
        },
      },
      {
        version: "0.8.20",
        settings: {
          optimizer: {
            enabled: true,
            runs: 200,
          },
        },
      },
    ],
  },
  networks: {
    localhost: {
      url: "http://127.0.0.1:8545",
    },
  },
};
