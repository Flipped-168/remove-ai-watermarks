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
  - `10` global provider specialists + `33` subfamily specialists, each combining a 3-seed MLP Soup, a vectorized fixed-depth `HistGradientBoosting` tree ensemble, and a distilled `ExtraTrees -> MLP` student with calibration-reoptimized distilled blend weights (`w_e <= 0.25`), pooled via drift-bounded zero-inflation subfamily blending (`alpha in {0.0, 0.55, 0.70, 0.85, 1.0}`) across 16 real-image varieties and routed by a unified damped competitive margin (`gamma = 0.60`).
- **Stage 2 (`9` stacked version heads, `999-d`):**
  - Feature-subsampled vectorized `HistGradientBoosting` tree ensembles taking the `956-d` features (and Stage-1 log-odds scores) to predict the canonical model/export subfamily (`version_subfamily`).
- **Artifact:** `multi-provider-source-v3.npz` (`allow_pickle=False`)
- **SHA-256:** `e5264354edb0109461e3c4988e3267903a8a2a0648b05e81705dee298be97806`

The artifact contains only learned parameters, normalization constants, tree arrays, labels, and calibrated thresholds. It does not contain training images, paths, image hashes, embeddings, or a training catalog.

## Evaluation (`40,974` clean audited samples; `8,476` locked test)

The operating point was selected on a disjoint `6,708`-image calibration split (`0.19%` calibration `unknown` false-positive rate across 16 fine-grained real-image varieties). On the `8,476`-image locked test split (`4,410` multi-variety `unknown` negatives + `4,066` AI provider images):

- **Unified 10-provider router:** `99.68%` `unknown` specificity (`0.32%` test `unknown` FPR; `0.37%` photographic FPR and `0.27%` non-photographic structured FPR) and `53.30%` aggregate target recall.

| Provider | Test count | Standalone ROC AUC | Router recall | Router precision | Stage-2 version accuracy |
|---|---:|---:|---:|---:|---:|
| `openai` | 1,146 | 0.9807 | 65.0% | 96.6% | 86.8% |
| `google` | 1,038 | 0.9804 | 56.1% | 97.5% | 94.8% |
| `bytedance` | 371 | 0.9456 | 48.2% | 98.9% | 87.9% |
| `flux` | 740 | 0.9604 | 41.2% | 97.8% | 92.8% |
| `stable_diffusion` | 397 | 0.9803 | 48.1% | 96.0% | 85.4% |
| `meta` | 94 | 0.9690 | 77.7% | 94.8% | — (`meta:imagine`) |
| `midjourney` | 77 | 0.9742 | 54.5% | 84.0% | 96.1% |
| `ideogram` | 72 | 0.9825 | 34.7% | 78.1% | 59.7% |
| `firefly` | 83 | 0.8993 | 21.7% | 85.7% | 100.0% |
| `xai` | 48 | 0.9291 | 14.6% | 77.8% | 64.6% |

### Held-out real-image specificity by variety (`4,410` test negatives across 16 real classes + foreign AI)

| Real-image variety | Test count | False positives | False-positive rate | Specificity |
|---|---:|---:|---:|---:|
| `photo` | 2,183 | 8 | 0.37% | 99.63% |
| `photo_retouched` | 321 | 1 | 0.31% | 99.69% |
| `classical_inpaint` | 17 | 0 | 0.00% | 100.00% |
| `digital_art` | 441 | 1 | 0.23% | 99.77% |
| `game_art` | 131 | 1 | 0.76% | 99.24% |
| `vector` | 135 | 0 | 0.00% | 100.00% |
| `interface` | 171 | 1 | 0.58% | 99.42% |
| `diagram` | 98 | 1 | 1.02% | 98.98% |
| `chart_data_viz` | 159 | 0 | 0.00% | 100.00% |
| `technical_architecture` | 84 | 0 | 0.00% | 100.00% |
| `procedural_graphic` | 13 | 0 | 0.00% | 100.00% |
| `document` | 165 | 0 | 0.00% | 100.00% |
| `gov_scientific_doc` | 32 | 0 | 0.00% | 100.00% |
| `receipt_invoice` | 122 | 0 | 0.00% | 100.00% |
| `print_publishing` | 229 | 0 | 0.00% | 100.00% |
| `stress_recompressed` | 103 | 1 | 0.97% | 99.03% |
| `foreign_ai` | 6 | 0 | 0.00% | 100.00% |

### External blind multi-variety real-image verification (`selective-v8`, `2,267` untouched images)

Evaluated on the hash-disjoint external `selective-v8` blind real-image cohorts (`2,267` images never seen in train, calibration, or test): **8 / 2,267 false positives (`0.35%` overall FPR, `99.65%` specificity)**.

| Blind `selective-v8` cell | Evaluated | False positives | False-positive rate | Specificity |
|---|---:|---:|---:|---:|
| `photo` | 450 | 3 | 0.67% | 99.33% |
| `vector` | 332 | 0 | 0.00% | 100.00% |
| `game_art` | 230 | 4 | 1.74% | 98.26% |
| `interface` | 342 | 0 | 0.00% | 100.00% |
| `diagram` | 305 | 0 | 0.00% | 100.00% |
| `document` | 308 | 0 | 0.00% | 100.00% |
| `stress_recompressed` | 300 | 1 | 0.33% | 99.67% |

## Intended use

Install `remove-ai-watermarks[source-classify]` and call the explicit Python API `classify_source(path)` or CLI command `remove-ai-watermarks classify-source <IMAGE>`. `identify` does not run this model. Set `RAIW_SOURCE_CLASSIFY_WEIGHTS` to the `.npz` file or its parent directory for offline deployments.
