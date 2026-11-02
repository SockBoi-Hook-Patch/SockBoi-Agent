# APK Reverse Engineering and Android Assessment Roadmap

## Design inputs reviewed

This design distills public architectural patterns from:
- yaklang/hack-skills: hierarchical master/category/deep skills and mobile security checklists.
- jbro129/android-modding: Android tool and framework taxonomy (JADX, Apktool, Frida, LSPlant, Dobby, IL2CPP tooling, pack/sign utilities).
- morluto/rea: typed CLI/MCP reverse-engineering workflows, static APK inspection, DEX class/method/reference navigation, JNI binding inspection, APK signature metadata, Android resources, and ADB-backed device evidence.
- zhaoxuya520/reverse-skill: task routing, scope-gated case setup, tool readiness checks, evidence/finding/report handoff.

No third-party source code or large Skill text is copied into SockBoi. Tool availability and licenses remain independently verified.

## Target capability map

| Capability | Intended implementation | Status after this change |
|---|---|---|
| APK intake identity | SHA-256, size, ZIP safety limits | Implemented as offline library function |
| APK structural inventory | DEX, ABI .so, resources, assets, signing entry inventory | Implemented |
| Plain-text manifest summary | Package, permissions, application flags, component declarations | Implemented for text XML only |
| Binary Android manifest | Sandboxed Apktool/aapt2 adapter | Planned |
| DEX Java/Kotlin analysis | JADX-backed typed adapter, class/method/reference tools | Planned |
| JNI and native ELF analysis | ABI-aware ELF/JNI parser and native provider adapters | Planned |
| Resources and localized strings | Apktool/aapt2 resource adapter | Planned |
| APK signature verification | v1/v2/v3/v3.1 verification and signer lineage | Planned; current inventory is not verification |
| Framework analysis | Flutter, Unity/IL2CPP, React Native, Xamarin indicators | Planned |
| ADB dynamic inspection | Existing ADB Skill; bounded typed adapter is future work | Skill only |
| Frida runtime instrumentation | Existing Frida Skill; reviewed script runtime is future work | Skill only |
| Evidence graph and reporting | Artifact → observations → findings → remediation | Design |
| Router and case workflow | Master/category/deep Skill loading and scope/evidence state machine | Design |

## Architecture

~~~text
APK upload
  -> size/type/archive validation + SHA-256
  -> tenant/engagement artifact record
  -> APK triage router
      -> Manifest / permissions / exported components
      -> DEX / JADX / class / method / references
      -> Resources / strings / locales
      -> ELF / ABI / JNI / native provider
      -> Signature / signer / dependency provenance
      -> Framework (Flutter / Unity IL2CPP / React Native)
  -> findings + evidence graph + coverage report
  -> optional approved Android worker
      -> ADB device lifecycle / logs / screenshots / bounded transfers
      -> Frida reviewed instrumentation / bounded events
  -> analyst review / report
~~~

The APK parsing worker must be separate from the FastAPI control plane. Static parsing must not execute APK code or extract unbounded archives. Runtime work must use a disposable emulator and separately approved, typed ADB/Frida operations.

## Implementation phases

### Phase A — Safe static intake (current)
- Bounded ZIP inspection, archive path validation, duplicate rejection, compression-ratio and expansion limits.
- SHA-256 identity and DEX/native/resource inventory.
- Plain XML manifest parsing only; binary Android XML remains explicitly unknown.

### Phase B — Static APK providers
- Pinned JADX, Apktool/aapt2 adapters with subprocess isolation, timeouts, output limits and no network.
- Typed tools for package inspection, class search, class/method decompilation, references, JNI candidates and resource lookup.
- Signature verification using trusted platform tooling; do not equate META-INF entries with valid signatures.
- Evidence IDs and provenance on every result.

### Phase C — Case router and report
- Master → Android category → specialist skill routing.
- Case scope contract, timeline, work items, tool-index and supply-chain manifest.
- Evidence graph, finding confidence, false-positive handling, coverage and reproducible report export.

### Phase D — Dynamic Android lab
- Disposable emulator manager, ADB device lifecycle, APK install/launch, logs, screenshots and bounded transfers.
- Frida server compatibility, process discovery, reviewed hash-pinned instrumentation templates, bounded events, redaction and deterministic detach.
- Human approval immediately before active dispatch; network egress disabled by default.

### Phase E — Framework and advanced native coverage
- Flutter/Dart snapshots, Unity IL2CPP metadata and native libraries, React Native bundles, JNI, symbol/call graphs.
- Optional Ghidra/IDA/JEB providers subject to their own licensing and installation requirements.
- Differential builds, signer changes, SBOM/dependency analysis and patch comparison.

## Release gates

- All artifacts are untrusted; parser fuzzing and ZIP-bomb tests are required.
- Tenant/Engagement binding on artifact, job, evidence and finding reads/writes.
- No generic shell, arbitrary Frida script, arbitrary ADB command or model-selected executable path.
- Tools are pinned and checksummed; tool setup is explicit and never silently downloads binaries.
- Static and dynamic workers have resource quotas, cancellation, isolated temp storage and cleanup.
- Secrets and personal data are redacted before persistence.
- Integration tests use purpose-built APK fixtures and disposable local emulators.
- A feature is not marked implemented until tests and CI pass.

## Limitations

The current APK inspector is a safe ZIP inventory and optional plain-XML manifest reader. It does not decompile DEX, decode binary Android XML, verify APK signatures, run JADX/Apktool, launch an emulator, connect ADB, or attach Frida. These are explicit future adapter milestones, not active capabilities.
