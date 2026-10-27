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
  - `10` global provider specialists + `33` subfamily specialists, each combining a 3-seed MLP Soup, a vectorized fixed-depth `HistGradientBoosting` tree ensemble, and a distilled `ExtraTrees -> MLP` student with calibration-reoptimized distilled blend weights (`w_e <= 0.25`), pooled via drift-bounded zero-inflation subfamily blending (`alpha in {0.0, 0.55, 0.70, 0.85, 1.0}`) and routed by a unified damped competitive margin (`gamma = 0.60`).
- **Stage 2 (`9` stacked version heads, `999-d`):**
  - Feature-subsampled vectorized `HistGradientBoosting` tree ensembles taking the `956-d` features (and Stage-1 log-odds scores) to predict the canonical model/export subfamily (`version_subfamily`).
- **Artifact:** `multi-provider-source-v3.npz` (`allow_pickle=False`)
- **SHA-256:** `5c271b0ba7d7ae6b3965de18cade40c867a6bcc31f6848422111667aa2deba53`

The artifact contains only learned parameters, normalization constants, tree arrays, labels, and calibrated thresholds. It does not contain training images, paths, image hashes, embeddings, or a training catalog.

## Evaluation (`36,761` clean audited samples; `7,395` locked test)

The operating point was selected on a disjoint `5,591`-image calibration split (`0.83%` calibration `unknown` false-positive rate across 9 real-image varieties). On the `7,395`-image locked test split (`3,329` multi-variety `unknown` negatives + `4,066` AI provider images):

- **Unified 10-provider router:** `99.01%` `unknown` specificity (`0.99%` test `unknown` FPR; `1.20%` photographic FPR and `0.74%` non-photographic structured FPR) and `61.68%` aggregate target recall.

| Provider | Test count | Standalone ROC AUC | Router recall | Router precision | Stage-2 version accuracy |
|---|---:|---:|---:|---:|---:|
| `openai` | 1,146 | 0.9803 | 70.9% | 96.1% | 86.8% |
| `google` | 1,038 | 0.9786 | 70.3% | 96.1% | 94.8% |
| `bytedance` | 371 | 0.9451 | 59.3% | 96.9% | 89.2% |
| `flux` | 740 | 0.9558 | 47.2% | 96.1% | 92.8% |
| `stable_diffusion` | 397 | 0.9780 | 53.9% | 93.0% | 85.4% |
| `meta` | 94 | 0.9667 | 77.7% | 91.3% | — (`meta:imagine`) |
| `midjourney` | 77 | 0.9675 | 64.9% | 64.9% | 96.1% |
| `ideogram` | 72 | 0.9817 | 33.3% | 92.3% | 58.3% |
| `firefly` | 83 | 0.8968 | 30.1% | 86.2% | 100.0% |
| `xai` | 48 | 0.9244 | 22.9% | 78.6% | 68.8% |

### Held-out real-image specificity by variety (`3,329` test negatives)

| Real-image variety | Test count | False positives | False-positive rate | Specificity |
|---|---:|---:|---:|---:|
| `photo` | 1,839 | 22 | 1.20% | 98.80% |
| `photo_retouched` | 194 | 1 | 0.52% | 99.48% |
| `vector` | 67 | 1 | 1.49% | 98.51% |
| `game_art` | 111 | 2 | 1.80% | 98.20% |
| `digital_art` | 469 | 1 | 0.21% | 99.79% |
| `interface` | 79 | 0 | 0.00% | 100.00% |
| `diagram` | 231 | 2 | 0.87% | 99.13% |
| `document` | 230 | 0 | 0.00% | 100.00% |
| `stress_recompressed` | 103 | 4 | 3.88% | 96.12% |
| `foreign_ai` | 6 | 0 | 0.00% | 100.00% |

### External blind multi-variety real-image verification (`selective-v8`, `2,267` untouched images)

Evaluated on the hash-disjoint external `selective-v8` blind real-image cohorts (`2,267` images never seen in train, calibration, or test): **14 / 2,267 false positives (`0.62%` overall FPR, `99.38%` specificity)**.

| Blind `selective-v8` cell | Evaluated | False positives | False-positive rate | Specificity |
|---|---:|---:|---:|---:|
| `photo` | 450 | 4 | 0.89% | 99.11% |
| `vector` | 332 | 0 | 0.00% | 100.00% |
| `game_art` | 230 | 6 | 2.61% | 97.39% |
| `interface` | 342 | 2 | 0.58% | 99.42% |
| `diagram` | 305 | 0 | 0.00% | 100.00% |
| `document` | 308 | 0 | 0.00% | 100.00% |
| `stress_recompressed` | 300 | 2 | 0.67% | 99.33% |

## Intended use

Install `remove-ai-watermarks[source-classify]` and call the explicit Python API `classify_source(path)` or CLI command `remove-ai-watermarks classify-source <IMAGE>`. `identify` does not run this model. Set `RAIW_SOURCE_CLASSIFY_WEIGHTS` to the `.npz` file or its parent directory for offline deployments.
