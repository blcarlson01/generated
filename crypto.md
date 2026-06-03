Below is a markdown version of the currently known cryptography-focused LLM benchmarks, along with whether they have native or known integration with Inspect AI.

---

# Cryptography-Focused LLM Benchmarks

| Benchmark        | Focus                                                              | Open Source        | Inspect-AI Support                         |
| ---------------- | ------------------------------------------------------------------ | ------------------ | ------------------------------------------ |
| AICrypto         | Comprehensive cryptography benchmark (MCQ, proofs, CTFs)           | Yes                | ❌ No official Inspect implementation found |
| Crypto-Eval      | Multi-dimensional cryptographic capability evaluation              | Unknown            | ❌ No Inspect implementation found          |
| CREBench         | Cryptographic reverse engineering and key recovery                 | Partial            | ❌ No Inspect implementation found          |
| CipherBank       | Cryptographic reasoning and decryption challenges                  | Yes                | ❌ No Inspect implementation found          |
| Random-Crypto    | Procedurally generated cryptographic CTF challenges                | Yes                | ❌ No Inspect implementation found          |
| CIPHER           | Security analysis of LLM-generated cryptographic code              | Research release   | ❌ No Inspect implementation found          |
| s2n-bignum-bench | Formal verification and theorem proving for crypto implementations | Yes                | ❌ No Inspect implementation found          |
| LLM-CLVA         | Cryptographic vulnerability analysis                               | Research benchmark | ❌ No Inspect implementation found          |

---

# 1. AICrypto

### Links

* Website: [AICrypto Website](https://aicryptobench.github.io/?utm_source=chatgpt.com)
* Paper: [AICrypto Paper (arXiv)](https://arxiv.org/abs/2507.09580?utm_source=chatgpt.com)

### Coverage

* 135 cryptography MCQs
* 150 CTF challenges
* 18 proof problems
* Human expert baselines
* Agent-based evaluation framework

### Inspect-AI Status

**No official Inspect-AI implementation currently exists.** The authors released their own evaluation framework and agent infrastructure. ([AICrypto][1])

### Porting Difficulty

**Medium**

Most tasks could be represented as:

* Inspect datasets
* Tool-enabled agents
* Custom scorers
* Docker-based challenge environments

---

# 2. Crypto-Eval

### Links

* SSRN: [Crypto-Eval Paper](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6595772&utm_source=chatgpt.com)

### Coverage

Six dimensions:

1. Basic cryptography
2. Algorithmic reasoning
3. Encryption/decryption
4. Code generation
5. Contextual cryptanalysis
6. Algorithm identification

### Inspect-AI Status

**No Inspect implementation found.** ([SSRN][2])

### Porting Difficulty

**Easy**

This benchmark appears largely structured and question-driven, making it a natural fit for Inspect datasets and scorers.

---

# 3. CREBench

### Coverage

* Reverse engineering
* Algorithm identification
* Binary analysis
* Key recovery
* Cryptanalysis

### Inspect-AI Status

**No known Inspect implementation.**

### Porting Difficulty

**Hard**

Requires:

* Docker containers
* Binary execution
* Tool usage
* Multi-step agent workflows

This would resemble CyberSec Eval or OASIS style evaluations.

---

# 4. CipherBank

### Links

* Website: [CipherBank Website](https://cipherbankeva.github.io/?utm_source=chatgpt.com)

### Coverage

* Cipher solving
* Cryptographic reasoning
* Decryption challenges

### Inspect-AI Status

**No official Inspect support.** ([CipherBank][3])

### Porting Difficulty

**Easy to Medium**

Would map well to:

* Dataset tasks
* Programmatic scorers
* Pass/fail evaluation

---

# 5. Random-Crypto

### Links

* Website: [Random-Crypto Benchmark](https://aielte-research.github.io/Random-Crypto/?utm_source=chatgpt.com)

### Coverage

* Procedurally generated CTFs
* Caesar ciphers
* Vigenère
* Classical cryptography
* RL training data

### Inspect-AI Status

**No known implementation.** ([Aielte Research][4])

### Porting Difficulty

**Very Easy**

Likely one of the easiest crypto benchmarks to bring into Inspect.

---

# 6. CIPHER

### Links

* Paper: [CIPHER Paper](https://arxiv.org/abs/2602.01438?utm_source=chatgpt.com)

### Coverage

Evaluates whether models introduce:

* Static IVs
* Missing authentication
* Nonce misuse
* Broken crypto implementations

### Inspect-AI Status

**No implementation found.** ([arXiv][5])

### Porting Difficulty

**Medium**

Would work extremely well as:

* Secure coding benchmark
* Code generation benchmark
* Static-analysis-backed scorer

---

# 7. s2n-bignum-bench

### Coverage

* Formal proofs
* HOL Light
* Machine-verified crypto correctness

### Inspect-AI Status

**No implementation found.**

### Porting Difficulty

**Hard**

Requires theorem prover integration.

---

# 8. LLM-CLVA

### Coverage

* CVE analysis
* Cryptographic implementation flaws
* Security auditing

### Inspect-AI Status

**No implementation found.**

### Porting Difficulty

**Medium to Hard**

Could leverage:

* Docker
* Static analysis
* LLM judges
* Tool-using agents

---

# What Already Exists in Inspect Ecosystem?

The closest existing foundations are:

| Project                                                                             | Inspect-Based          |
| ----------------------------------------------------------------------------------- | ---------------------- |
| [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai?utm_source=chatgpt.com) | Yes                    |
| [OpenBench](https://github.com/groq/openbench?utm_source=chatgpt.com)               | Yes (built on Inspect) |

OpenBench explicitly states it is built on Inspect AI and supports custom benchmark suites. ([GitHub][6])

---

# Recommendation for Your Benchmark Platform

If your goal is to build a serious cybersecurity and cryptography evaluation suite on top of Inspect, I would prioritize:

1. **AICrypto** (highest value)
2. **CIPHER** (real-world secure coding)
3. **CREBench** (agentic crypto reverse engineering)
4. **Crypto-Eval** (broad capability coverage)

Together these would give you:

* Knowledge evaluation
* Mathematical reasoning
* Secure code generation
* Vulnerability discovery
* Reverse engineering
* Agentic exploitation

That combination would arguably be the most complete Inspect-based cryptography benchmark suite currently available, because I could not find evidence that any of these have already been fully ported into Inspect AI. ([AICrypto][1])

[1]: https://aicryptobench.github.io/?utm_source=chatgpt.com "AICrypto"
[2]: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6595772&utm_source=chatgpt.com "Crypto-Eval: A Benchmark for Evaluating Cryptographic Capabilities of Large Language Models by Jianxin Wang, Haodong Deng, Chaoen Xiao, Lei Zhang, Huiyi Zhao :: SSRN"
[3]: https://cipherbankeva.github.io/?utm_source=chatgpt.com "CipherBank - Cryptography Challenges for LLMs"
[4]: https://aielte-research.github.io/Random-Crypto/?utm_source=chatgpt.com "Random-Crypto Benchmark"
[5]: https://arxiv.org/abs/2602.01438?utm_source=chatgpt.com "CIPHER: Cryptographic Insecurity Profiling via Hybrid Evaluation of Responses"
[6]: https://github.com/groq/openbench?utm_source=chatgpt.com "GitHub - groq/openbench: Provider-agnostic, open-source evaluation infrastructure for language models · GitHub"
