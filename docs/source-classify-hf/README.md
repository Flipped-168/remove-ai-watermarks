---
license: apache-2.0
library_name: numpy
pipeline_tag: image-classification
tags:
  - image-forensics
  - source-attribution
  - open-set-classification
---

# RAIW multi-provider source-pipeline classifier (`multi-provider-source-v3`)

This repository contains the pickle-free (`allow_pickle=False`) derivative weights for the abstaining `remove-ai-watermarks` pixel source-pipeline classifier across **10 AI provider families** (`openai`, `google`, `bytedance`, `flux`, `stable_diffusion`, `meta`, `midjourney`, `ideogram`, `firefly`, `xai`) plus `unknown` (`classify_source` / `remove-ai-watermarks classify-source`).

This model is **not a SynthID detector** and does not decode or verify any cryptographic or invisible watermark payload (`watermark_truth="unknown"`). Its labels describe complete generation and export pixel pipelines, so renderer, geometry, encoding, post-processing, and watermark state may be confounded. `unknown` does not mean that SynthID is absent, and a provider label does not prove that SynthID is present.

## Model architecture

- **Input (`956-d`):**
  - `124-d` spatial opponent-residual and gradient forensic features (`extract_124d`).
  - `768-d` phase-free `16x16` log-power and radial spectral features (`source_spectral`).
  - `64-d` directional / block-boundary (`8x8` and `16x16`) / chroma-aliasing / azimuthal-anisotropy features (`augment_892d_to_956d`).
- **Stage 1 (`43` specialist units across `10` canonical providers):**
  - `10` global provider specialists + `33` subfamily specialists, each combining a 3-seed MLP Soup (`0.35`), a vectorized fixed-depth `HistGradientBoosting` tree ensemble (`0.35`), and a distilled `ExtraTrees -> MLP` student (`0.30`), pooled via zero-inflation subfamily blending (`alpha in {0.0, 0.65, 0.85, 1.0}`) and routed by a unified damped competitive margin (`gamma = 0.60`).
- **Stage 2 (`9` stacked version heads, `999-d`):**
  - Vectorized `HistGradientBoosting` tree ensembles taking the `956-d` features concatenated with all `43` Stage-1 log-odds scores to predict the canonical model/export subfamily (`version_subfamily`).
- **Artifact:** `multi-provider-source-v3.npz` (`allow_pickle=False`)
- **SHA-256:** `7a550c2613af99ea784d2f25396776de0aa4ecf2efabe937054679f620b5ee5c`

The artifact contains only learned parameters, normalization constants, tree arrays, labels, and calibrated thresholds. It does not contain training images, paths, image hashes, embeddings, or a training catalog.

## Evaluation (`36,761` clean audited samples; `7,395` locked test)

The operating point was selected on a disjoint `5,591`-image calibration split (`0.75%` calibration `unknown` false-positive rate across 9 real-image varieties). On the `7,395`-image locked test split (`3,329` multi-variety `unknown` negatives + `4,066` AI provider images):

- **Unified 10-provider router:** `98.95%` `unknown` specificity (`1.05%` test `unknown` FPR; `1.25%` photographic FPR and `0.81%` non-photographic structured FPR) and `61.07%` aggregate target recall.

| Provider | Test count | Standalone ROC AUC | Router recall | Router precision | Stage-2 version accuracy |
|---|---:|---:|---:|---:|---:|
| `openai` | 1,146 | 0.9750 | 70.3% | 96.4% | 85.6% |
| `google` | 1,038 | 0.9747 | 72.2% | 95.5% | 93.4% |
| `bytedance` | 371 | 0.9363 | 59.0% | 96.1% | 88.1% |
| `flux` | 740 | 0.9557 | 47.4% | 94.1% | 89.7% |
| `stable_diffusion` | 397 | 0.9784 | 44.8% | 95.2% | 78.3% |
| `meta` | 94 | 0.9652 | 77.7% | 90.1% | — (`meta:imagine`) |
| `midjourney` | 77 | 0.9718 | 64.9% | 60.2% | 89.6% |
| `ideogram` | 72 | 0.9798 | 30.6% | 84.6% | 62.5% |
| `firefly` | 83 | 0.9020 | 31.3% | 100.0% | 96.4% |
| `xai` | 48 | 0.9295 | 18.8% | 75.0% | 68.8% |

### Held-out real-image specificity by variety (`3,329` test negatives)

| Real-image variety | Test count | False positives | False-positive rate | Specificity |
|---|---:|---:|---:|---:|
| `photo` | 1,839 | 23 | 1.25% | 98.75% |
| `photo_retouched` | 194 | 1 | 0.52% | 99.48% |
| `vector` | 67 | 0 | 0.00% | 100.00% |
| `game_art` | 111 | 1 | 0.90% | 99.10% |
| `digital_art` | 469 | 3 | 0.64% | 99.36% |
| `interface` | 79 | 0 | 0.00% | 100.00% |
| `diagram` | 231 | 4 | 1.73% | 98.27% |
| `document` | 230 | 0 | 0.00% | 100.00% |
| `stress_recompressed` | 103 | 3 | 2.91% | 97.09% |
| `foreign_ai` | 6 | 0 | 0.00% | 100.00% |

### External blind multi-variety real-image verification (`selective-v8`, `2,267` untouched images)

Evaluated on the hash-disjoint external `selective-v8` blind real-image cohorts (`2,267` images never seen in train, calibration, or test): **15 / 2,267 false positives (`0.66%` overall FPR, `99.34%` specificity)**.

| Blind `selective-v8` cell | Evaluated | False positives | False-positive rate | Specificity |
|---|---:|---:|---:|---:|
| `photo` | 450 | 4 | 0.89% | 99.11% |
| `vector` | 332 | 0 | 0.00% | 100.00% |
| `game_art` | 230 | 7 | 3.04% | 96.96% |
| `interface` | 342 | 2 | 0.58% | 99.42% |
| `diagram` | 305 | 1 | 0.33% | 99.67% |
| `document` | 308 | 0 | 0.00% | 100.00% |
| `stress_recompressed` | 300 | 1 | 0.33% | 99.67% |

## Intended use

Install `remove-ai-watermarks[source-classify]` and call the explicit Python API `classify_source(path)` or CLI command `remove-ai-watermarks classify-source <IMAGE>`. `identify` does not run this model. Set `RAIW_SOURCE_CLASSIFY_WEIGHTS` to the `.npz` file or its parent directory for offline deployments.
