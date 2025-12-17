# Changelog

---
## [unreleased]

### 🐛 Bug Fixes

- **(ci)** simplify workflow to use mise run ci and suppress pytest warnings by [@basher83](https://github.com/basher83) in [db69a83](https://github.com/basher83/radiant-filament/commit/db69a831a39a2d76757a2c2db75844eb634b7a87)

---
## [0.2.0](https://github.com/basher83/radiant-filament/compare/v0.1.0..v0.2.0) - 2025-12-17

### 🚀 Features

- **(agent)** add config merging and extended parameters by [@basher83](https://github.com/basher83) in [9e8cd78](https://github.com/basher83/radiant-filament/commit/9e8cd78524dba0f55096ca00e04f116c6a25f654)
- **(cli)** add arguments for advanced Deep Research features by [@basher83](https://github.com/basher83) in [9d9ef3a](https://github.com/basher83/radiant-filament/commit/9d9ef3a26d06f6a49985cd5e94b065664a56d5e8)
- **(cli)** add --prompt-file option to read prompts from files by [@basher83](https://github.com/basher83) in [953b3d7](https://github.com/basher83/radiant-filament/commit/953b3d77195d11d5969998f46311b85a908b288f)
- **(docs)** address PR review issues and enhance error handling by [@basher83](https://github.com/basher83) in [d62e79f](https://github.com/basher83/radiant-filament/commit/d62e79f63eff9bc9029610b1b138cbfd145da27a)

### 🐛 Bug Fixes

- **(tests)** add dependency injection for testability by [@basher83](https://github.com/basher83) in [179ec88](https://github.com/basher83/radiant-filament/commit/179ec8801b71ee6ad6cd58434a0211c57a4a228a)
- **(tests)** add dependency injection for testability by [@basher83](https://github.com/basher83) in [e0fa2ab](https://github.com/basher83/radiant-filament/commit/e0fa2ab421e150e0c28399defdc8a5969c0894e2)
- **(workflow)** remove redundant literal from concurrency group by [@Copilot](https://github.com/Copilot) in [d748a81](https://github.com/basher83/radiant-filament/commit/d748a818edef720c677aeb7f76502b848c0b3271)
- **(workflow)** remove redundant literal from concurrency group by [@Copilot](https://github.com/Copilot) in [1cd5ca3](https://github.com/basher83/radiant-filament/commit/1cd5ca3efebbecef358dfd961e41c32b995a9a0e)
- improve error handling and polling robustness by [@basher83](https://github.com/basher83) in [ffcc377](https://github.com/basher83/radiant-filament/commit/ffcc377af3a86a1422167bc947a4e3cb7b00150a)

### 🔍 Other Changes

- **(mise)** add pandoc tool for document conversion by [@basher83](https://github.com/basher83) in [fe8e3be](https://github.com/basher83/radiant-filament/commit/fe8e3bebbd9c7e293a4a98d33fecd9c10be0035a)

### 🚜 Refactor

- **(agent)** improve error handling and enhance docstrings by [@basher83](https://github.com/basher83) in [eeb1729](https://github.com/basher83/radiant-filament/commit/eeb1729ab9c148dae4629a12d14e1cc39677e61f)
- **(agent)** improve error handling and validation by [@basher83](https://github.com/basher83) in [d8d1923](https://github.com/basher83/radiant-filament/commit/d8d19232146234493903b31848b1fa2c8791015f)

### 📚 Documentation

- **(copilot-instructions)** add quick commands, env note, and testing snippets by [@basher83](https://github.com/basher83) in [430a4d1](https://github.com/basher83/radiant-filament/commit/430a4d1ae2265ab902e277d00fdc986f48807393)
- reorganize documentation and add research artifacts by [@basher83](https://github.com/basher83) in [9c3cb5e](https://github.com/basher83/radiant-filament/commit/9c3cb5ead132a99c99e4715589956dca8b4bdd80)
- update changelog for v0.2.0 by [@basher83](https://github.com/basher83) in [2923957](https://github.com/basher83/radiant-filament/commit/29239571fcc885d0e0205cf15fe1dbeac45ba54e)

### 🧪 Testing

- add tests for new agent and CLI features by [@basher83](https://github.com/basher83) in [22618aa](https://github.com/basher83/radiant-filament/commit/22618aaca55773247ba016b6430b5c1a06b5bbe1)
- update existing tests for new error handling behavior by [@basher83](https://github.com/basher83) in [af7992c](https://github.com/basher83/radiant-filament/commit/af7992c9c105807502868b0f55a8c9a6d3cd0d4d)
- add comprehensive edge case coverage by [@basher83](https://github.com/basher83) in [9371cbd](https://github.com/basher83/radiant-filament/commit/9371cbdbfb16ac38a4f0fe92514ced20447e1757)
- update exception types to match narrowed error handling by [@basher83](https://github.com/basher83) in [f9780c5](https://github.com/basher83/radiant-filament/commit/f9780c59a3b765e22f09aeca4bb0d8bdd209b686)

### ⚙️ Miscellaneous Tasks

- **(copilot)** add repo copilot configuration by [@basher83](https://github.com/basher83) in [081b839](https://github.com/basher83/radiant-filament/commit/081b839c1a1825c5d95cdebff4639eec36f91aee)
- **(hooks)** update require-uv rule to conditions format by [@basher83](https://github.com/basher83) in [be40779](https://github.com/basher83/radiant-filament/commit/be40779dac061f5984300fe4caad6e5f7e077cbb)
- **(mise)** add pytest test task by [@basher83](https://github.com/basher83) in [c83684c](https://github.com/basher83/radiant-filament/commit/c83684c2bf27b5e2bf2156423bbe7c3067728822)
- **(mise)** add 'ci' task and CI-specific deps task by [@basher83](https://github.com/basher83) in [dfdf741](https://github.com/basher83/radiant-filament/commit/dfdf7418fbcdd7b4136637b075f6aa51d48bb498)
- **(vscode)** add mcp server config by [@basher83](https://github.com/basher83) in [081b564](https://github.com/basher83/radiant-filament/commit/081b564e52bea886083cd1c81785201d1b07b1ff)
- **(workflows)** standardize checkout (fetch-depth), use mise, and add job timeout by [@basher83](https://github.com/basher83) in [2adfb37](https://github.com/basher83/radiant-filament/commit/2adfb37487fb12b9b0488a62c5eaee97bc148784)
- **(workflows)** standardize checkout (fetch-depth), use mise, and add job timeout by [@basher83](https://github.com/basher83) in [7640d7c](https://github.com/basher83/radiant-filament/commit/7640d7cecc7bb3a3fe4970f1ff7fe3acf7359eb0)
- update .gitignore by [@basher83](https://github.com/basher83) in [bfece61](https://github.com/basher83/radiant-filament/commit/bfece615f35d9a5a4c25027e9d1b45fc0b28ea6e)
- add fast PR gate workflow by [@basher83](https://github.com/basher83) in [10bf967](https://github.com/basher83/radiant-filament/commit/10bf96756fdb49ee50d2c684f050a09ee03eb7d6)
- add copilot setup steps workflow by [@basher83](https://github.com/basher83) in [686237c](https://github.com/basher83/radiant-filament/commit/686237cf754a46fb2393dd2df2598ef83606bb95)
- add fast PR gate workflow by [@basher83](https://github.com/basher83) in [16ab39e](https://github.com/basher83/radiant-filament/commit/16ab39e27609e012961047a6b2da76cd685a4fe6)

### New Contributors

* @Copilot made their first contribution

---
## [0.1.0] - 2025-12-15

### 🐛 Bug Fixes

- **(agent)** handle initial connection errors and optimize reconnection loop by [@basher83](https://github.com/basher83) in [be592b2](https://github.com/basher83/radiant-filament/commit/be592b2fb95cc39a5eef3e1f6b08a1fbabbe3264)
- **(agent)** add timeout parameters and improve empty function call error handling by [@basher83](https://github.com/basher83) in [8a17ac3](https://github.com/basher83/radiant-filament/commit/8a17ac3ebc7a4d417ab2bbe5d152cd0dab1b067c)

### 🔍 Other Changes

- add tombi directive for non-strict schema validation by [@basher83](https://github.com/basher83) in [09149af](https://github.com/basher83/radiant-filament/commit/09149af11facda0afb72dc5b01564f6175e77844)
- add git-cliff to mise tools by [@basher83](https://github.com/basher83) in [ed16fc7](https://github.com/basher83/radiant-filament/commit/ed16fc702822e55d763543eb5e5b4f5e4483c74b)
- add git-cliff configuration by [@basher83](https://github.com/basher83) in [49d3262](https://github.com/basher83/radiant-filament/commit/49d3262a837546d4d077a392ad428e0b87eb4052)

### 📚 Documentation

- expand README with comprehensive setup and usage instructions by [@basher83](https://github.com/basher83) in [101bec6](https://github.com/basher83/radiant-filament/commit/101bec6bb35ce8c0f7720d51a43a7b3e6e7d0048)
- add research artifacts from deep research sessions by [@basher83](https://github.com/basher83) in [6230f19](https://github.com/basher83/radiant-filament/commit/6230f19ea113de03104d6adc2b4b008403c9f2aa)
- add CLAUDE.md with project context and quick reference by [@basher83](https://github.com/basher83) in [cf331ee](https://github.com/basher83/radiant-filament/commit/cf331ee961c577b750d4775736839c7a36e8c053)
- add uvx quick start section to README by [@basher83](https://github.com/basher83) in [8d4e832](https://github.com/basher83/radiant-filament/commit/8d4e83251a12880da6f04dd8bfa6e11171a120d8)
- reorganize documentation and update commands by [@basher83](https://github.com/basher83) in [2360d4d](https://github.com/basher83/radiant-filament/commit/2360d4db6699ff771b63c0ef56c72a45a2ba396f)
- add changelog by [@basher83](https://github.com/basher83) in [00bc48f](https://github.com/basher83/radiant-filament/commit/00bc48f0fa9e7edbd62f923bad92b041ee6b1ff6)
- update changelog for v0.1.0 by [@basher83](https://github.com/basher83) in [d27a234](https://github.com/basher83/radiant-filament/commit/d27a2346990af0ffdfb3fde4df840ea16f6a9220)

### ⚙️ Miscellaneous Tasks

- add Claude Code configuration by [@basher83](https://github.com/basher83) in [55409ea](https://github.com/basher83/radiant-filament/commit/55409ea46f36d1b4b296d790690f936a1da43e0d)

### New Contributors

* @basher83 made their first contribution
* @renovate[bot] made their first contribution

<!-- generated by git-cliff -->
