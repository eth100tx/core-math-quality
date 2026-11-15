# November 14 planning evidence

This targeted comparison informs the [roadmap](../../ROADMAP.md). The Sunday scan retains its separate baseline.

- **Implementation.** The start is the implementation tip observed at the November 10 adoption check. The individual queue cards retain their original evidence pins. Comparing `3b8cd7f48bcb88088beb8d61c94807a303578782` to [018fa97c](https://gitlab.inria.fr/core-math/core-math/-/commit/018fa97cbdacf59924b899a9dfa422d532cb2bb7) returned one changed path, `src/binary64/tgamma/check_special.c`. A smaller special-test run motivates checking input selection. Its effect on coverage has not been measured here.
- **Proof.** Comparing `d5fab2e483d00b7a21c5b50b1abb877cadeb5c5b` to [08b80413](https://gitlab.inria.fr/zimmerma/core-math-proofs/-/commit/08b804138d9e39b507522762c5b0df5e1b0b1478) showed a cosine update and two tan proof commits. In [cos.tex lines 752–755](https://gitlab.inria.fr/zimmerma/core-math-proofs/-/blob/43c9a83bc6d15f96d2886dee543b5523ebf30394/cos/cos.tex#L752-755) the swap condition is equal quadrant and remainder-sign bits with w₁ ≤ w₂. The text then gives σ = (b + q + d) mod 2 and `(-1)^σ C = (-1)^b D`. This closes the wording follow-up; exceptional-input census completeness remains separate.
- **Bivariate transfer.** At transfer snapshot `2a8b106`, SHA-256 of each Git blob and each corresponding checkout file matched the ten entries in the separate transfer-level .sha256 manifest below. That outer manifest includes the inner SHA256SUMS.json. This authenticates the received bytes against the manifest. The calculation, census regeneration, platform qualification and import each need independent evidence. This planning check executed no archived code.

| File | SHA-256 |
|---|---|
| `MAIN-AI-HANDOFF.txt` | `759fdd09c168f08bee194368f0acfd2cceac8018bbf5c64500b8ed929e7a9bff` |
| `SHA256SUMS.json` | `d31c7af28356df7b5ecaaa1c5d2e3c3eb0b0a611ed0200212e2ade8a06514340` |
| `TRANSFER-README.txt` | `a51acd5641d657b63245fdca1df67cea6d83cca90e13fb35af8c46eca7f98847` |
| `VALIDATION.json` | `25d9a6420f053566cb2ae0fc4f26ccb9e00da837db64e0fb1f146882330e3d1a` |
| `hypot-endpoint-20261013.zip` | `2402ff57e94b6cc1fd1fd008ad17e13fcf6a002043ce4ef8e57a35d0c6460afb` |
| `hypot-extremal-20261013.zip` | `d308e416c424884bcb68d69cb95ea5c9179e90451794379a417a11edb14ee278` |
| `hypot-portable-20261012-v2.zip` | `d8f8d59134cf7a7008cbe79e07b556770207c94f29ecdbff47204df0c573beba` |
| `remaining-functions-20261013-v3.zip` | `63ea8267656f93bce0f2fa3337a819dfde0f4e65646e73a6f242e1766026c380` |
| `review-weekly-integration-20261025.json` | `ff7a40ccda78593f28c02c9ee302fd36ea1bd59a47df9732ed6750d4d439f103` |
| `weekly-workflow.patch` | `34c7b54a886800146c4923fb5ef72887fb32c5fe4934a8282e233ee6b4108006` |
