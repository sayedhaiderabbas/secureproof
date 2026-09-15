const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("EvidenceRegistry", function () {
  async function deployed() {
    const Registry = await ethers.getContractFactory("EvidenceRegistry");
    const registry = await Registry.deploy();
    return registry;
  }

  it("registers and retrieves a cryptographic proof", async function () {
    const registry = await deployed();
    const id = ethers.keccak256(ethers.toUtf8Bytes("evidence-1"));
    const hash = ethers.keccak256(ethers.toUtf8Bytes("sha256-placeholder"));
    await expect(registry.registerEvidenceHash(id, hash)).to.emit(registry, "EvidenceRegistered");
    expect(await registry.verifyEvidenceHash(id, hash)).to.equal(true);
    expect((await registry.getEvidenceRecord(id))[0]).to.equal(hash);
  });

  it("rejects mismatches, empty values, and duplicates", async function () {
    const registry = await deployed();
    const id = ethers.keccak256(ethers.toUtf8Bytes("evidence-2"));
    const hash = ethers.keccak256(ethers.toUtf8Bytes("hash"));
    const other = ethers.keccak256(ethers.toUtf8Bytes("other"));
    await expect(registry.registerEvidenceHash(ethers.ZeroHash, hash)).to.be.revertedWith("evidence id required");
    await expect(registry.registerEvidenceHash(id, ethers.ZeroHash)).to.be.revertedWith("hash required");
    await registry.registerEvidenceHash(id, hash);
    expect(await registry.verifyEvidenceHash(id, other)).to.equal(false);
    await expect(registry.registerEvidenceHash(id, hash)).to.be.revertedWith("evidence already registered");
  });
});
