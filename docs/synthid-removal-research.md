# SynthID mark removal research

> Research archive for pixel-only SynthID removal, not diffusion
> regeneration. Not a statement of current product capability. Shipped
> invisible removal is lossy regeneration:
> [known limitations](known-limitations.md).
>
> Sister pages: [SynthID local detector](synthid-detector-research.md),
> [SynthID source classifiers](synthid-classifiers.md),
> [mechanism reference](synthid.md).

## Result

The quality-preserving OpenAI SynthID remover hunt closed 2026-08-20.
Bayer, VNG demosaic, upscale-then-Bayer, barrel distortion, scanline
jitter, and a 2 px shift closed 2026-08-22 on s1/s2 and 2026-08-23 on s3
and fish: they leave the official oracle `detected`.

Working residual kills on photographs cost about 19-26 dB:

- 16-32 px cartesian phase scramble (s1 24.6-24.8 dB, fish 23.2 dB, s2 19.0 dB)
- Fourier-angle scramble of the same annulus (s1 24.1 dB)
- Radial-phase scramble of the same annulus (s1 25.0 dB)
- Y-only 16-32 scramble (s1 24.6 dB); Cb/Cr-only do not kill
- File named polar-1632, actually cartesian (s1 25.6 dB)
- Replace 16-32 with a COCO photo's 16-32 (s1 25.2 dB)
- Gaussian blur sigma 7 (23.8 dB), holds 3/3 versus sigma 6
- Additive 16-32 jam only at a=24 / 18.6 dB, worse than scramble

Baker-map, 8-seam carve, Poisson, nested LSB, palette64, and ICC rewrite
do not kill at a better PSNR.

JPEG q5, noise sigma 16, grayscale, rot90, flip, 5°, downscale 0.20x,
median 7, posterize 4, VAE round-trip, and white pad to 40% linear stay
`detected`. Elastic warp is not a stable kill (s3 still `detected` at
22.0 dB).

The product remainder is diffusion regeneration (`qwen-zimage` /
`sdxl-zimage`), which does not decode and delete a payload. Defeating the
verifier does not restore forensic deniability; see
[synthid.md](synthid.md#23-removal-attacks-and-forensic-detectability).

Official `not_detected` on collage, photo-pad, and two-panel layouts is a
presentation gate, not residual damage. Those rungs are in
[detector research](synthid-detector-research.md).

## Closed quiet removers

| Attack | Close | Notes |
| --- | --- | --- |
| Quality-preserving photo remover | 2026-08-20 | Every residual `not_detected` that is not a collage is below usable quality |
| Additive in-band jam as a quiet remover | 2026-08-21 | Fish flips only at 18.6 dB; 4-8 px at the same PSNR stays `detected` |
| Bayer bilinear / VNG / upscale-Bayer | 2026-08-23 | s1/s2/s3 and fish still `detected`. s3 bilinear 37.1 dB, fish 34.7 dB. VNG on s2 is dirtier than scramble (18.5 vs 19.0 dB) and the mark remains |
| Barrel k1=0.06, scanline ±0.8 px, and shift 2 px | 2026-08-23 | s1/s2/s3/fish `detected` even at 14-20 dB barrel. Fish scanline 32.5 dB and shift 22.7 dB still `detected` |
| TrustMark-style micro-warp | 2026-08-21 | 0.25 px / 32 dB still 100% detect on TrustMark P; OpenAI elastic ~21 dB unreplicated |
| OKLab random-codeword replacement as a quiet wipe | 2026-08-15 | On four public Google-oracle positives, replacing the period-16 tile at 0.95 dropped the *local* lattice score below 0.173 at ~54 dB. Gemini pixel verify never accepted the candidates (`Connecting to Verify AI`). Local-score intervention, not an official wipe |
| PRC-style OKLab a/b noise plus spectral peak cleaning | 2026-08-15 | Independent high-pass OKLab noise at 32.6 dB moved the median local score by only `-0.0219`. Comb suppression moved one of four below threshold at 58 dB. Not a quiet official kill |
| Rinne414 fixed-template subtraction | 2026-08-24 | The pinned pre-May GPT-Image2 residual was resized onto a current verified OpenAI image and subtracted at 0.25x, 0.5x, 1x, and 2x. Official SynthID stayed `detected` at 43.13, 37.49, 31.60, and 25.72 dB after metadata stripping. Even the dirtiest rung is no better than the existing 24-25 dB annulus-phase scramble. The template can spoof its own public correlator but does not cancel the current mark |
| `newideas99` CNN gradient | 2026-08-24 | A 3x3 crop-grid objective spread the white-box perturbation over the full marked frame. The frozen ensemble fell from 0.99995 to 0.25956 at ±2/255 (45.92 dB) and to effectively zero at ±4/255 (40.30 dB). Official OpenAI SynthID stayed `detected` at ±1, ±2, ±4, and ±8/255, through 34.30 dB. The gradient attacks the surrogate's shortcut, not the production mark |
| `reverse-SynthID` V4 Round-06 | 2026-08-24 | The advertised `final`/`nuke` path is SD-VAE regeneration plus elastic and affine warps, resize squeeze, color change, residual FFT subtraction, and a JPEG/noise chain, with PSNR floors of only 14/11 dB. The repository claims 20 manual Gemini-app successes but contains no manifest, tally, or per-image verdicts. Its four bundled older cleaned pairs are 45.7-50.2 dB, yet the reproduced V4 score rises on three and is nearly unchanged on the fourth. No callable Google pixel oracle was available for an independent Round-06 verdict. This is an unverified lossy regeneration/distortion stack, not a quiet pattern cancellation |
| [`0xROOTPLS/DeSynth`](https://github.com/0xROOTPLS/DeSynth/tree/96db920731c2a3d04bf13163a5077b9a67706d1b) | 2026-08-24 | Qwen Image img2img at strength 0.25, followed by a Gaussian frequency split that restores the source high frequencies above sigma 1.95. The repository's public OpenAI original, default output, and edge-guided output all returned official `detected` in a current repeat after metadata stripping. The published `not found` claim does not reproduce against the current OpenAI oracle |
| [`froggeric/gemini-watermark-and-synthid-remover`](https://github.com/froggeric/gemini-watermark-and-synthid-remover/tree/5918384ce403968de0560cefd889e50eba0163bc) | 2026-08-24 | SDXL img2img with a documented manual Google-verifier ladder. The author reports 7/8 clears at strength 0.08 and 9/9, including a double mark, at strength 0.10 with five effective denoise steps and PSNR 29-41 dB. The exact nine before/after verdict artifacts are not tracked, so this is useful external regeneration corroboration, not an independently reproduced oracle result |
| [`atomantic/PortOS`](https://github.com/atomantic/PortOS/tree/b11a93e110262925c64a1b145a154ca87b340055) adversarial-jamming experiment | 2026-08-24 | Its own one-image manual OpenAI run found that quality-preserving phase noise, band noise, blur, and 0.70 resize squeeze stayed detected. Only visibly destructive phase perturbation cleared. A 0.85-0.90 resize caused repeated detector timeouts, which the repository correctly keeps separate from `not_detected`. This independently closes high-fidelity additive/phase jamming, but the source artifacts are not published |
| Generic regeneration claims | 2026-08-24 | `mertizci/noai-watermark`, `BovineOverlord/Loyal-Bear`, `obaskly/NeuralBleach`, and `tymongumienik/unwatermark` are SD/CtrlRegen/ControlNet redraws. Their algorithms are already covered by the product's regeneration remainder and the CtrlRegen literature. README verdicts without a frozen manifest do not establish a quieter or more reliable operating point |
| Add unmarked context (frame, pad, hstack, collage) | 2026-08-19 | Official `not_detected` is a presentation gate. White pad 40% linear stays `detected`; photo fill at the same geometry is `not_detected`. See detector identity/layout |
| `cebeuq/Synthid-Bypass` diffusion reconstruction | 2026-08-13 | 12 public pairs. Lattice and Gemini Verify go quiet on the *after* images because the image was redrawn, not because a payload was deleted. Faces and text are a quality claim for regeneration, not a local wipe |

Development oracle: the internal OpenAI provenance helper after AI-metadata
strip. Seeds s1, s2, s3 as in
[detector research](synthid-detector-research.md). Raw files:
`.local-eval/synthid/prc-oklab-attack-2026-08-15/`.

## Band that actually carries the mark

Phase-randomize one octave at a time, preserve energy (E2, s1, replicated
p16_32 on s2 and s3):

| Octave (period px) | Verdict |
| --- | --- |
| 2-4 | detected |
| 4-8 | detected |
| 8-16 | detected |
| 16-32 | not_detected |
| 32-64 | detected |
| 64-128 | detected |

Destroying only 16-32 px periods silences the official decoder. The
lattice band 8-16 px does not. On a marked gray flat the same scramble is
51.1 dB `not_detected` because the band is almost empty. On a photograph
the band holds the scene (24.3 dB). Replacing native 16-32 with a
2x-pyramid prediction is 48.4 dB and still `detected`.

Fish additive jam, luma RMS `a`:

| Band | a | PSNR | Verdict |
| --- | ---: | ---: | --- |
| 16-32 | 0.06-4.0 | 51.2-33.6 | detected |
| 16-32 | 8 | 27.7 | detected |
| 16-32 | 16 | 21.9 | detected |
| 16-32 | 24 | 18.6 | not_detected |
| 4-8 | 16 | 21.9 | detected |
| 4-8 | 24 | 18.6 | detected |

Preregistered close `a*_photo < 0.53` failed (`a* > 16`).

## Bayer and geometry (2026-08-22)

Frozen one-pass batch. Lattice scores on these OpenAI sources are already
`indeterminate` and are not the label.

| Attack | s1 | s2 | s3 | fish |
| --- | --- | --- | --- | --- |
| source | detected | detected | detected | detected |
| Bayer bilinear | 32.7 detected | 28.4 detected | 37.1 detected | 34.7 detected |
| Bayer VNG | 25.0 detected | 18.5 detected | 26.4 detected | 25.4 detected |
| upscale 1.15 then Bayer | 33.9 detected | 29.8 detected | 38.4 detected | 36.0 detected |
| barrel k1=0.06 | 19.9 detected | 14.2 detected | 20.2 detected | 18.5 detected |
| scanline ±0.8 px | 31.5 detected | 26.7 detected | 35.7 detected | 32.5 detected |
| shift 2 px | 23.1 detected | 15.9 detected | 24.7 detected | 22.7 detected |
| 16-32 phase scramble | 24.6 not_detected | 19.0 not_detected | 25.2 not_detected | 23.2 not_detected |

Camera pipeline and mild geometry do not hit the decoder basis. A 2 px
shift, which kills `pipeline_lattice`, left s1/s2/s3/fish `detected`.
Scramble remains the residual kill on 4/4 sources.
`.local-eval/synthid/prc-oklab-attack-2026-08-15/bayer-geometry-2026-08-22/`.
Manifest `status` is `oracle_complete` (2026-08-22 22:07).

## Attack ladders (OpenAI oracle)

Pilot 2026-08-17 (n=3): JPEG q40, 0.5x, noise8+jpeg85, 0.35x+jpeg50 all
`detected` (s2 0.35x+jpeg50 at 20.1 dB still detected).

Kill and flip (s1), then replication 3/3:

| Rung | s1 | s2 | s3 |
| --- | --- | --- | --- |
| blur sigma 6 | detected | detected | detected |
| blur sigma 7 | not_detected | not_detected | not_detected |
| keep 0.50 linear | detected | detected | detected |
| keep 0.40 linear | not_detected | not_detected | not_detected |
| elastic ~24 dB | detected 24.6 | detected 17.9 | detected 26.1 |
| elastic ~21 dB | not_detected 20.8 | not_detected 14.8 | detected 22.0 |
| pad white 40% linear | detected | detected | detected |
| hstack with photo | not_detected | not_detected | not_detected |
| blend 25% marked | detected | detected | detected |
| inset native 1:1 on 2x photo | not_detected | not_detected | not_detected |
| JPEG q5 | detected | detected | detected |

Holds on 3/3: blur 6 vs 7, crop keep 0.50 vs 0.40, white pad 40%
`detected`, hstack `not_detected`, blend 25% `detected`, JPEG q5
`detected`. Elastic at ~21 dB does not hold. Crop keep-0.40 and hstack
are presentation or support, not a quiet residual wipe.

Surround: photo fill at the white-pad geometries is `not_detected` on
3/3; white pad at those sizes was `detected`. Unmarked photo strip flips
between 25% width (`detected`) and 35% (`not_detected`). Photo frame 15%
each side is `not_detected` on 3/3; 12% does not hold.

## Wild removers (oracle 2026-08-23)

Preregistered on s1, one pass, 25 s gap. Manifest:
`.local-eval/synthid/prc-oklab-attack-2026-08-15/wild-attacks-2026-08-23/oracle-manifest.json`.

| Attack | PSNR | Verdict | Note |
| --- | ---: | --- | --- |
| Replace 16-32 with a COCO photo's 16-32 | 25.2 | not_detected | Same annulus as cartesian scramble (24.6 dB). Substituting a camera band kills the decoder, 0.6 dB quieter than scramble on s1, not a new quality class |
| File named polar-1632 | 25.6 | not_detected | Misnamed. The raster randomizes cartesian FFT phase in the 16-32 annulus, same family as scramble (24.6 dB). It is a scramble replicate, not a `(r, θ)` polar test |
| 64-color median-cut palette | 35.6 | detected | Quieter than scramble and still marked. Posterize-4 already stayed `detected`; a smarter quantizer is not enough |
| PIL RGB to CMYK to RGB | inf | not submitted | No-op on this PNG |

The 16-32 kill is luma phase in that annulus. Cartesian, Fourier-angle,
and radial-phase all silence the decoder near 25 dB. A 90° sector of the
same ring does not (27.5 dB `detected`). Cb-only and Cr-only 16-32
scrambles stay `detected` at 44-45 dB. A foreign-scene transplant of the
same band also silences the decoder near 25 dB. Palette, Baker-map, seam
carve, Poisson, nested LSB, and ICC do not.

Follow-up 2026-08-23, s1, 25 s gap, `remaining-2026-08-23/oracle-manifest.json`:

| Attack | PSNR | Verdict |
| --- | ---: | --- |
| Fourier-angle 16-32 scramble | 24.1 | not_detected |
| Cartesian 16-32 scramble (replicate) | 24.8 | not_detected |
| Baker-map of the 16-32 band | 27.8 | detected |
| Poisson noise | 30.7 | detected |
| Nested LSB in blue | 55.9 | detected |
| Seam carve 8 | 27.7 | detected |
| ICC sRGB rewrite | inf | not submitted, no-op |

Non-local codecs, 2026-08-23, s1, 25 s gap:

| Attack | PSNR | Verdict |
| --- | ---: | --- |
| HEIF q80 | 46.3 | detected |
| HEIF q50 | 39.3 | detected |
| AV1 CRF 32 | 37.2 | detected |
| Print-scan simulation | 24.95 | detected |

Physical print-scan is still blocked unattended (Brother DCP-L2520DW idle and
accepting, no `scanimage`, no ImageCapture pyobjc). Face-gated scramble is
unnecessary: Haar on s1 put *more* 16-32 energy on faces. Generic 25 dB is
not the kill: this simulation stays `detected` at the PSNR where 16-32
phase scramble does not.

Waveform-shell splits, 2026-08-23, s1, 25 s gap,
`waveforms-shells-2026-08-23/oracle-manifest.json`:

| Attack | PSNR | Verdict |
| --- | ---: | --- |
| Y-only 16-32 scramble | 24.6 | not_detected |
| Cb-only 16-32 scramble | 45.0 | detected |
| Cr-only 16-32 scramble | 43.9 | detected |
| 90° Fourier sector of 16-32 | 27.5 | detected |
| Radial-phase-only 16-32 | 25.0 | not_detected |

## External literature (surveyed through 2026-10-19)

Primary sources. Detector papers live in
[detector research](synthid-detector-research.md). Forensic stealth of
regeneration is already in [synthid.md](synthid.md#23-removal-attacks-and-forensic-detectability).

This survey used 12 broad bibliographic queries across arXiv, OpenReview,
conference proceedings, provider publications, and linked code repositories.
The arXiv harvest alone produced 443 unique records; 160 attack-, removal-,
forgery-, and robustness-related title/abstract candidates were screened, and
22 central papers were read from full text. The search covered classical
watermark attacks, post-hoc and in-generation AI watermarks, black-, beige-,
and white-box threat models, benchmarks, removal forensics, and code-release
status. It excluded text-watermark attacks except where a theorem explicitly
claims to apply across modalities. This is an engineering evidence map, not a
claim of exhaustive bibliographic completeness.

The broad answer is clear: image-watermark removal is a mature adversarial
research problem, and the literature repeatedly breaks open schemes. The much
narrower result needed here remains absent. No primary source found in this
sweep demonstrates a no-box attack on current production OpenAI or Google
SynthID at native 1024 px that both reliably clears the official verifier and
preserves roughly 40 dB PSNR / 0.99 SSIM. Results on an open decoder, an
external SynthID variant, a local surrogate, a resized input, or semantic
regeneration do not establish that result.

| Source | Attack | Against SynthID? | Map to this campaign |
| --- | --- | --- | --- |
| Gowal et al., [SynthID-Image](https://arxiv.org/abs/2510.09263) | Documents the production threat model and evaluates the external 512 x 512 SynthID-O variant against common transformations and weak VAE regeneration | The paper says production SynthID has marked more than ten billion images and frames, but publishes experimental results for SynthID-O, not the deployed model | Authoritative evidence that the production system is post-hoc, proprietary, adversarially trained, and explicitly hardened against weak VAE regeneration; it is not a public production benchmark |
| Zhao et al., [arXiv:2306.01953](https://arxiv.org/abs/2306.01953) (NeurIPS 2024) | Add noise, then denoise or regenerate (VAE / diffusion). Pixel-level invisible marks are provably removable. Semantic watermarks proposed as the alternative | Open post-hoc schemes, not production SynthID | This is the family our product uses (`qwen-zimage` / `sdxl-zimage`). Gowal trains SynthID-O against *weak* VAE regeneration. Our foreign-VAE round-trip at 22.3 dB stayed `detected`. Regeneration works when it redraws, not when it is a light codec |
| Liu et al., [arXiv:2410.05470](https://arxiv.org/abs/2410.05470) (CtrlRegen, ICLR 2025) | Controllable diffusion from clean noise, with a knob on how many noise steps to add | SOTA open watermarks | Same family. Goonatilake later finds CtrlRegen+ the *most* forensically detectable remover (AUROC 0.9999) |
| Kassis and Hengartner, [arXiv:2405.08363](https://arxiv.org/abs/2405.08363) (UnMarker, IEEE S&P 2025) | No decoder feedback. Two adversarial spectral optimizations. Breaks even some semantic watermarks (best remaining detection 43%) | Not production SynthID | Spectral disruption without an oracle is the honest analog of our 16-32 scramble, except UnMarker is optimized and we used a one-octave phase shuffle. Goonatilake: UnMarker TPR 98.28% at 0.1% FPR as a *forensic* leftover |
| Tallam et al., [arXiv:2505.08234](https://arxiv.org/abs/2505.08234) (SemanticRegen) | Partial, label-free regeneration of main objects | Tree-Ring, StegaStamp, StableSig, DWT/DCT. Not SynthID | Partial redraw. Our collage / photo-pad `not_detected` is a presentation gate, not this attack |
| Cao et al., [arXiv:2608.10166](https://arxiv.org/abs/2608.10166) (MarkNull, USENIX Security 2026) | On-manifold latent decorrelation via a public diffusion proxy. Claims 100% on 20 Imagen-3 Gemini-verify images. PSNR 25.36 dB, SSIM 0.80 | Small Gemini-verify set | Independent evidence that a no-box latent reconstruction can confuse Gemini. Does not meet this project's 40 dB / 0.99 SSIM release gate. Still generation, not a pixel-only wipe |
| Cao et al., [arXiv:2602.15364](https://arxiv.org/abs/2602.15364) (MarkSweep, ICASSP 2026) | Learned frequency decomposition and fusion trained on amplified high-frequency watermark noise | HiDDeN and Stable Signature, not production SynthID; reported bit accuracy below 67% | A learned denoiser is a distinct route from our fixed filters, but the paper does not establish transfer to the current OpenAI decoder |
| Kong et al., [arXiv:2602.01513](https://arxiv.org/abs/2602.01513) (MarkCleaner) | Mask-guided encoder and 2D Gaussian Splatting decoder trained to tolerate micro-geometric displacement | The public abstract does not report production SynthID; code is promised after acceptance | The closest published objective to quiet phase disruption, but there is no released implementation to test here yet |
| Li et al., [arXiv:2609.31693](https://arxiv.org/abs/2609.31693) (DnD) | Routes a reconstructed grayscale semantic carrier separately from a residual branch, then drops the residual | Seven representative watermark families; the public abstract does not report production SynthID | Another learned representation-level route rather than a fixed coefficient search; the arXiv record does not link an implementation as of this survey |
| Goonatilake and Ateniese, [arXiv:2605.09203](https://arxiv.org/abs/2605.09203) | Six removers all leave a forensic residue a ResNet-50 sees at >98% TPR @ 1% FPR | Applies to UnMarker, Zhao's WatermarkAttacker, CtrlRegen+ | Defeating a provider oracle is not deniability. This is the product remainder |
| An et al., [arXiv:2401.08573](https://arxiv.org/abs/2401.08573) (WAVES, ICML 2024) | 26 attacks on StegaStamp, Stable Signature, Tree-Ring. Regeneration, not JPEG, is the attack that matters. StegaStamp TPR@1%FPR 1.00 to 0.01; Tree-Ring 0.99 to 0.12 | Open watermarks | Protocol. Our blur-sigma-7 and 16-32 scramble are closer to WAVES "distortion" than to regeneration |
| Bulychev et al., [arXiv:2605.16796](https://arxiv.org/abs/2605.16796) (Watermarks Attack Watermarks) | Apply a second watermark, usually with the victim's own post-processing encoder and a different message. On MS-COCO, its end-to-end pipeline lowers Video Seal victim bit accuracy from 0.998 to 0.520 (TPR@1%FPR 0.046) and Pixel Seal from 0.999 to 0.514 (TPR 0.029); the same-method attacker message recovers at 0.99 bit accuracy for both schemes. Quality is reported as an eight-metric normalized composite, not a raw PSNR operating point | Eight open image schemes, not production SynthID; Video Seal is tested on images | Directly motivated the [local open-encoder replication](#re-watermarking-on-open-encoders-2026-09-27). Its MIT [code](https://github.com/MariaBulychev/Watermarks-Attack-Watermarks/tree/0444f52ad972da9e009555f2dc1028d9abe0610e) calls external encoder packages and weights; the top-level license does not license those dependencies |
| Yang et al., [arXiv:2609.01249](https://arxiv.org/abs/2609.01249) (One Prompt Is Enough) | One reconstruction prompt to a closed image editor (GPT Image 1, 1.5 and 2; Nano Banana, Pro and 2) launders the payload over 1,800 outputs; OpenAI models disrupt it most | DwtDct, DwtDctSvd and RivaGAN only. "SynthID was not tested" | Regeneration through a provider's own model. It breaks the scheme our DWT-DCT detector reads, and says nothing about production SynthID, which the same editors add to their output |
| Yao et al., [arXiv:2610.11290](https://arxiv.org/abs/2610.11290) (ProxyEraseAgent) | Ranks a pool of open decoders by calibrated response and attacks the strongest as proxy boundary estimators; 94.8% success over 11 systems against 79.5% for the best fixed Regen-VAE | Open schemes, TrustMark and VideoSeal among them. Not SynthID | Needs a decoder that responds to the mark. No public decoder responds to production SynthID, so it does not transfer to an oracle-only target |
| Bao et al., [arXiv:2609.08213](https://arxiv.org/abs/2609.08213) (DRIFT) | Deflects the diffusion trajectory. The adaptive variant searches a strength ladder per image for "the first verifier-rejected rung" from binary verifier feedback; 98-100% success on nine marks | In-generation diffusion marks (Tree-Ring family, Gaussian Shading and others). Not SynthID | The ladder stop is our [attack ladders](#attack-ladders-openai-oracle) run per image. Against a provider verifier that is the adaptive query loop its terms forbid, so it applies to local oracles only |
| Ye et al., [arXiv:2610.03166](https://arxiv.org/abs/2610.03166) (LiBRA) | White-box latent optimization with the key and decoder, steering decoding confidence toward chance from both sides so the mark is not left inverted but detectable; Stable Signature detection 1.00 to 0.03 | Released checkpoints of Stable Signature, the YU1 GAN fingerprint, HiDDeN and MBRS | Needs the decoder, so it is out of reach here. The inverted-mark point applies to any bit-flip attack |
| Aistov et al., [arXiv:2610.02010](https://arxiv.org/abs/2610.02010) (Latent Frequency Masking, ICDM 2026) | Replaces selected Fourier coefficients of the latent; [code](https://github.com/alvitrioliks/lfm) | Stable Signature, Tree-Ring, RingID, Gaussian Shading (resists), Maxsive, METR. Not SynthID | In-generation latent marks. Not the post-hoc encoder family Gowal describes |
| Li et al., [arXiv:2609.31693](https://arxiv.org/abs/2609.31693) (Disentangle and Drop) | Splits the image into a grayscale carrier and a residual branch, then suppresses the residual, with one shared operating setting | SSL, DwtDct, DwtDctSvd, RivaGAN, StegaStamp, Stable Signature, Tree-Ring | Open schemes only |
| Yang et al., [arXiv:2609.31722](https://arxiv.org/abs/2609.31722) (Push-Pull) | Key-free and decoder-free at deployment; average BER 0.3958 at 31.07 dB PSNR on a four-method sweep | Seven open methods. Not SynthID | A BER near 0.40 leaves much of the payload intact, as with SPFM-Net below |
| Ding et al., [arXiv:2609.34003](https://arxiv.org/abs/2609.34003) (DeMark, audio) | Query-free black box that suppresses the time-frequency artifacts the embedding leaves; average attack success 0.92 and 0.96 on two speech sets | AudioSeal, WavMark, Timbre, AudioMarkNet. Not audio SynthID | A candidate cohort for the pinned AudioSeal oracle in the [benchmark kernel](benchmark-kernel.md). No code located |
| Wen et al., [arXiv:2305.20030](https://arxiv.org/abs/2305.20030) (Tree-Ring) | In-generation Fourier pattern in initial noise | Not SynthID | Kill is DDIM inversion plus latent wipe, not a pixel scramble. Lin and Juarez [arXiv:2506.10502](https://arxiv.org/abs/2506.10502) (USENIX 2025) remove it from public knowledge |
| Fernandez et al., Stable Signature, ICCV 2023 | Fine-tuned VAE decoder | Not SynthID | Regeneration that replaces the decoder is in-family. Our foreign VAE at 22.3 dB did not kill OpenAI SynthID, which is the expected mismatch |
| Google to [The Verge, 2026-04-14](https://www.theverge.com/ai-artificial-intelligence/911579/google-synthid-ai-watermarking-system-reverse-engineered) | reverse-SynthID does not systematically remove SynthID | Google spokesperson on the spectral bypass | Agrees with our V4 audit and with Bypass: reconstruction or decoder confusion, not a payload delete |

### Historical attack roots

The modern attack families are not conceptually new. Petitcolas, Anderson, and
Kuhn's 1998 [StirMark work](https://doi.org/10.1007/3-540-49380-8_16) already
used geometric desynchronization, cropping, resampling, compression, and
mosaic attacks. Kalker, Linnartz, and van Dijk's 1998
[detector-analysis attack](https://doi.org/10.1109/ICIP.1998.723516) treated a
public verifier as an oracle from which an attacker could estimate the mark.
Kutter, Voloshynovskiy, and Herrigel's 2000
[copy attack](https://doi.org/10.1117/12.384991) estimated a signal from one
image and transferred it to another instead of deleting it. Estimation-based
and collusion attacks then formalized the use of watermark statistics and
multiple marked copies. Current surrogate attacks, re-watermarking, paired
clean/marked training, and query optimization are learned versions of these
same threat models.

### Theory and defensive directions

The theory supports a narrower claim than "all watermarks are removable."
[Watermarks in the Sand](https://arxiv.org/abs/2311.04378) proves that strong
watermarking is impossible when an attacker has suitable quality and mixing
oracles, even with private detection, but its experiments are on text. It does
not directly prove a 40 dB image attack on SynthID. In the other direction,
[PRC watermarking](https://proceedings.iclr.cc/paper_files/paper/2025/hash/1331202ea3bb0a53ae897af0bb16e309-Abstract-Conference.html)
uses pseudorandom error-correcting codes in diffusion latents and reports that
existing removal attacks fail without substantial quality loss. That defense
is tied to the generator and does not describe SynthID's post-hoc production
mark. [Fairoze et al.](https://proceedings.mlr.press/v258/fairoze25a.html)
show a separate deployment tension: no existing construction simultaneously
delivers robustness, unforgeability, and public detectability, although such a
construction exists in theory. These results explain why production systems
combine private detection, rate limits, payloads, metadata, and retrieval
instead of relying on one universally robust pixel signal.

### Modern attack families

| Family | Strong primary examples | What the evidence establishes | Limit for this campaign |
| --- | --- | --- | --- |
| Adaptive decoder-aware optimization | [WEvade](https://arxiv.org/abs/2305.03807), [adaptive attacks](https://arxiv.org/abs/2309.16952), [LiBRA](https://arxiv.org/abs/2610.03166) | Near-chance decoding or low detection is attainable when the decoder, a close surrogate, or a keyed objective is available | Production decoders and scores are unavailable; our surrogate-gradient attack transferred poorly |
| Transfer attacks | [Watermark Transfer Attack](https://arxiv.org/abs/2403.15365) and its [pragmatic replication](https://arxiv.org/abs/2412.02576) | Transfer can work under favorable architectural alignment; the independent replication found no more than 21.1% evasion after relaxing those assumptions | A surrogate success is weak evidence for current closed production models |
| Single-image projection and reconstruction | [Deep Image Prior](https://arxiv.org/abs/2502.13998), [Hide&Seek](https://arxiv.org/abs/2603.01067), [DAWN](https://arxiv.org/abs/2510.07538), [MarkSweep](https://arxiv.org/abs/2602.15364) | An untrained or pretrained image prior can discard high-frequency open marks without paired inference data | DIP reaches about 35-36 dB on the easiest high-frequency marks and performs much worse on TrustMark, RoSteALS, and StegaStamp; none tests production SynthID |
| Learned paired clean/marked removal | [Push-Pull](https://arxiv.org/abs/2609.31722), [DnD](https://arxiv.org/abs/2609.31693), [FDDWAN](https://arxiv.org/abs/2607.27800), [SPFM-Net](https://arxiv.org/abs/2607.27811) | Training on clean/marked pairs can learn residual separation better than fixed denoisers; Push-Pull reports average BER 0.3958 at 31.07 dB / 0.9554 SSIM across four methods | Requires representative paired data; reported schemes and resolutions are open and mostly 256-512 px |
| Generative purification and semantic reconstruction | [Zhao et al.](https://arxiv.org/abs/2306.01953), [CtrlRegen](https://arxiv.org/abs/2410.05470), [SemanticRegen](https://arxiv.org/abs/2505.08234), [TokenPure](https://arxiv.org/abs/2512.01314), [RAVEN](https://arxiv.org/abs/2601.08832), MarkNull | This is the most consistently transferable no-box family. RAVEN reports average TPR@1%FPR 0.026 across 15 open schemes; the NeurIPS challenge winner reports 95.7% removal | It re-synthesizes texture, structure, or viewpoint. RAVEN reports distributional FID/CLIP rather than paired 40 dB fidelity; MarkNull reports 25.36 dB / 0.80 SSIM on 20 Gemini images |
| Super-resolution reconstruction | [SRAttack](https://openreview.net/forum?id=i05MM4h1WZ) | Pre-degrade, super-resolve, then downsample can replace texture while recovering apparent sharpness; it is black-box and training-free | The ICLR submission still says code will be released; it does not test production SynthID and its quality-improvement claim is not pixel identity |
| Microgeometry and desynchronization | [MarkCleaner](https://arxiv.org/abs/2602.01513), Tree-Ring translation in the [NeurIPS winning solution](https://arxiv.org/abs/2508.21072), RAVEN | Some decoders are more sensitive to subpixel geometry or latent-view shifts than to visible noise | Our current production target survived 2 px translation and several warps; results are scheme-specific |
| Latent and in-generation watermark attacks | [A Crack in the Bark](https://arxiv.org/abs/2506.10502), [SHIFT](https://arxiv.org/abs/2603.29742), [DRIFT](https://arxiv.org/abs/2609.08213), [Latent Frequency Masking](https://arxiv.org/abs/2610.02010) | Public model knowledge, inversion, or detector-gated resampling can collapse Tree-Ring and related diffusion watermarks | These attacks target a generative model's latent watermark, while production SynthID-Image is post-hoc |
| Overwriting, copying, and forgery | [Watermarks Attack Watermarks](https://arxiv.org/abs/2605.16796), [WMCopier](https://arxiv.org/abs/2503.22330), [WmForger](https://arxiv.org/abs/2510.20468) | A second encoder or learned foreign residual can erase, replace, or forge open payloads | Requires an encoder, representative training marks, or a reusable residual; WmForger averages 31.2 dB and does not test production SynthID |
| Forensic detection of removal | [Forensic Stealth](https://arxiv.org/abs/2605.09203), [Forensic Cost](https://arxiv.org/abs/2604.25491), [RemTraceNet](https://arxiv.org/abs/2609.31694) | Clearing the watermark decoder does not clear attack traces. Current removers are readily detected at low FPR, including in few-shot settings | A provider-oracle success is insufficient for forensic deniability or source restoration |

### Benchmarks and evidence quality

Three benchmark generations answer different questions:

- [WAVES](https://arxiv.org/abs/2401.08573) standardized 26 attacks on three
  influential open methods and established regeneration as the serious attack
  family rather than JPEG-style corruption.
- The NeurIPS 2024
  [Erasing the Invisible technical report](https://anirudhsatheesh.com/assets/publications/2025_eti/paper.pdf)
  records 2,722 submissions from 298 teams. The top five teams in both black-
  and beige-box tracks removed at least 89% of marks on average while retaining
  high benchmark quality. The released data and evaluator cover six open
  watermark families; they do not contain production SynthID.
- [WARP](https://arxiv.org/abs/2609.40031) evaluates 32 watermark methods and
  34 attack families. Its cross-resolution study spans 299 x 299 through 2040 x
  1300 and shows that many fixed-pixel attacks weaken as resolution rises,
  while regeneration degrades much less. Its Apache-2.0
  [implementation](https://github.com/ispras/wibe) is the best available open
  integration base for broad robustness comparisons, but it still cannot
  measure a closed provider decoder.

These results also explain why published "high quality" is not a single
standard. Some work reports FID or CLIP similarity over a distribution, some
reports a normalized multi-metric challenge score, and some reports paired
PSNR/SSIM. Across the strongest removal papers, paired quality ranges from
roughly 18 dB to 45 dB. A semantic match, an attractive redraw, and a 40 dB
source-preserving edit are different product outcomes.

### MarkNull released-code reproduction, 2026-10-19

The authors subsequently released [MarkNull's implementation](https://github.com/JieCaoSec/MarkNull)
without a top-level license. A local, untracked reproduction pinned commit
`4d4067d0ecd0cb2af2bcbf45132efae69b4b703f`, kept the published optimization
parameters, and added only a deterministic PyTorch seed plus hash-bound input
and output capture. No upstream code was copied into this public repository.

The unchanged optimization failed before producing an output on the first native
1024 x 1024 OpenAI image, during the first optimization backward pass. The
published SynthID case study uses 512 x 512 inputs, so the same source and one
prompt-matched sibling from the other dated OpenAI model were resized to 512 x
512 before a second run. Both attacks completed on an H100. Against those resized
controls, their outputs measured 22.24/23.22 dB grayscale PSNR, 0.620/0.665
grayscale SSIM, and 0.805/0.761 tolerant edge F1. Visual review confirmed
obvious texture smoothing and changed fine scene details. The local report is
`marknull-baseline-v1/report.json` (SHA-256
`8611df172b739f98cae4d333655f1eb30a1ffcd67c59780fec3c104021c0c135`).

No OpenAI oracle request was made. These outputs already fail the local fidelity
requirement by a wide margin, and the resized controls had not independently
established that the OpenAI watermark survived input preparation. This
reproduction therefore measures portability and quality, not OpenAI attack
success. It reinforces the distinction in the paper result: MarkNull is a useful
semantic reconstruction baseline, but it is not evidence for quiet, nearly
pixel-preserving removal from current OpenAI images.

Quiet pixel-only removal is not a published result on production
OpenAI or Google SynthID (still true in the 2026-10-17 literature sweep).
Against open encoders the fidelity band has moved: WmForger
([arXiv:2510.20468](https://arxiv.org/abs/2510.20468)) and Hide&Seek
([arXiv:2603.01067](https://arxiv.org/abs/2603.01067)) report roughly 30 dB,
and SPFM-Net and FDDWAN (arXiv:2607.27811, 2607.27800) claim 40-45 dB, but on
small images and with bit error rates that leave much of the payload intact.
The re-watermarking paper reports normalized quality degradation, not a raw
PSNR aggregate; our separate local measurements are below. None of these is a
result on a production closed watermark.

## Product remainder for removal

Invisible removal in this package regenerates through `qwen-zimage` or
`sdxl-zimage`. It is lossy. There is no shipped pixel-only OpenAI or
Google SynthID wipe. Do not add Bayer or geometry as remover arms.

### Re-watermarking on open encoders (2026-09-27)

The CC BY 4.0 [paper](https://arxiv.org/abs/2605.16796), v1 submitted on
2026-05-16, tests eight open image watermarks: Stable Signature and Tree-Ring
(in-generation), and StegaStamp, RoSteALS, ZoDiac, Pixel Seal, WAM, and Video
Seal (post-processing). Its policy
reapplies the victim encoder with a different message for post-processing
marks and uses ZoDiac against in-generation marks. Its Video Seal evaluation
is on images, not video. The [MIT repository](https://github.com/MariaBulychev/Watermarks-Attack-Watermarks/tree/0444f52ad972da9e009555f2dc1028d9abe0610e)
is pinned at `0444f52` and imports separate upstream encoders. We reproduced
the same-encoder, different-message operation with the project's pinned
oracles, not the paper's full WAVES dataset, classifier, or exact dependency
stack. TrustMark and DWT-DCT are project extensions, not paper subjects.

Twelve publication-cleared, provider-paired images from six content strata
were fitted to 512 x 512 pixels. Message A was embedded and serialized to PNG;
message B was then embedded into that decoded artifact and serialized again.
All decoder and fidelity readings used the saved RGB bytes. A successful case
requires a positive A control, an A-negative final verdict, and a B-positive
final verdict under that scheme's pinned rule. The table reports mean final
bit accuracy and median clean-to-final PSNR over valid A controls only.

| Encoder and direction | Valid A controls / all | B replaces A / valid | Final accuracy A / B | Median total PSNR |
| --- | ---: | ---: | ---: | ---: |
| DWT-DCT, FLUX codeword to SDXL codeword | 6 / 12 | 6 / 6 | 0.563 / 1.000 | 39.80 dB |
| DWT-DCT, SDXL codeword to FLUX codeword | 6 / 12 | 6 / 6 | 0.566 / 0.997 | 39.73 dB |
| TrustMark P, 61-bit messages | 12 / 12 | 12 / 12 | 0.541 / 1.000 | 44.15 dB |
| VideoSeal image mode, 256-bit messages | 12 / 12 | 12 / 12 | 0.479 / 0.990 | 43.89 dB |

The DWT-DCT codewords differ at only 21 of 48 bits, so A accuracy near 0.56
after B is compatible with complete replacement; it is not evidence of a
surviving A signal. Conversely, its 6/12 A-positive rate in each direction
precludes an unconditional success claim. These are fixed messages and a
small, deliberately stratified cohort, not a calibrated TPR@1%FPR estimate.
The worst-valid-case contact sheet shows no obvious coarse artifacts at
256-pixel viewing size, but PSNR and that sheet do not establish full-resolution
perceptual, face, or text fidelity.

The [corrected forgery study](watermark-forgery-study.md#corrected-videoseal-measurements-2026-09-08)
already showed VideoSeal replacement on saved video. A fresh run added
decoded-artifact fidelity on two 64-frame, 256 x 256, H.264 CRF 8 clips:
the synthetic moving gradient went from A accuracy 1.000 to 0.469 and B
accuracy 1.000 at 42.88 dB mean clean-to-final PSNR; the publication-cleared
Sora clip went from A 1.000 to 0.473 and B 0.996 at 37.60 dB. Both meet the
fixed-message replacement rule. This is an extension to video, not a paper
replication or a guarantee across codecs and sources.

`scripts/rewatermarking_study.py` and `scripts/rewatermarking_video_study.py`
write case rows, artifact hashes, and reports under the untracked
`.local-eval/rewatermarking-2026-09-27/` and
`.local-eval/rewatermarking-video-2026-09-27/`. Case-row SHA-256 values are
`3270df31320c0c58091f34b9c2e1f4885190fe65577e0dbbe03446b2b8bda890`
and `150e6584d5f253e52ddb0024ab9ad17f94b03b64dbfd4c293d57f6c6510607c6`.
The retained PNGs and MP4s were independently rehashed and decoded for PSNR
verification. Both runs used the local CPU; no Modal GPU was used and there
was no cloud GPU charge. This establishes a local open-encoder overwrite
primitive, not a production SynthID remover. An open encoder's foreign message
may coexist with a secret-keyed provider mark.

### Production SynthID overmark probe (2026-09-27 local)

One previously oracle-positive, publication-cleared original per provider
was selected from `data/synthid/manifest.csv`. The initial preparation made a
native-resolution RGB pixel control and a VideoSeal image-mode 256-bit
message-B overlay. It stripped AI metadata without changing decoded pixels,
but that rule was insufficient: the Google source retained its visible Gemini
sparkle. Its Gemini Web checks therefore cannot serve as pixel-only SynthID
positive controls. The OpenAI case had no visible mark; it remains 1122 x 1402
at 43.04 dB control-to-overlay PSNR, with B decoded at 1.000. The pair is
deliberately small and tests coexistence with an *unrelated* open watermark,
not application of a secret SynthID encoder.

The official OpenAI Content Provenance API reported SynthID `detected` on
both the metadata-free pixel control and its VideoSeal overlay, with C2PA
`not_present` for each (2026-09-28 UTC). Thus the successful open-encoder
overwrite did **not** remove OpenAI SynthID on this carrier.

The separately approved Google control upload reached Gemini Web's exact
`Connecting to Verify AI` state on 2026-09-28 and remained there well beyond
the project's documented 90-second indeterminate threshold. A separately
approved retry of the same prepared SHA-256 reached that state, then returned
only a generic visual-content answer: Gemini attributed the image to Google AI
from a visible four-pointed logo and text-rendering characteristics. It exposed
no settled SynthID tool outcome. Both observations are watermark
`indeterminate` and provenance `unavailable`, not clean or `detected`. The
VideoSeal-overlaid Google candidate was not uploaded because the positive
control gate was not satisfied. Therefore these runs supply no Google SynthID
verdict and do not test re-watermarking against production Google SynthID.

The preparation protocol now removes detected visible AI marks and AI metadata
before deriving either arm. On this Google source, the project-native Gemini
remover validated removal of the sparkle and changed 0.213% of pixels. VideoSeal
was then applied to that cleaned control: B accuracy is 0.992 and
control-to-overlay PSNR is 42.86 dB. Visual inspection found no remaining logo;
the local sparkle detector scored the prepared control 0.300, below its 0.35
detection threshold. The corrected control SHA-256 is
`14ed25fa58a0abc928ea869431248b450892facdf85b4621b3bf959c16a78cf3`;
the corrected candidate is
`86000c8e143339adde675522dc7709830c8ff230977e276c748cabb5d7cfadb8`.
The separately approved corrected-control upload first received the generic
question about whether Google AI created or edited the image. Gemini said the
amount of text made reliable confirmation difficult and could not confirm its
origin. That origin question was the wrong contract for a SynthID experiment;
its answer remains `indeterminate`. A confirmed follow-up asked directly
whether the same attached image contains a SynthID watermark, required the
SynthID verification tool, and prohibited inference from visible content,
logos, text, or metadata. Gemini then returned its settled verification-tool
positive: the image was created or edited with Google AI, with the Verify AI
SynthID help link. The corrected control is therefore watermark `detected` and
provenance `unavailable`. The separately approved candidate upload then used
the same direct SynthID question on 2026-09-29. Gemini explicitly refused it
because the verification-tool quota had been exceeded. That result is
watermark `refused` and provenance `unavailable`, not clean, `detected`, or
`indeterminate`. With separate approval, the exact same candidate upload was
then checked once in the `/u/2` slot. Its settled verification-tool response
said the image contained signals indicating Google-AI generation or editing.
That batch is watermark `detected` and provenance `unavailable`. Thus the
42.86 dB VideoSeal overlay did **not** remove Google SynthID on this carrier.
The control and usable candidate verdict came from different authenticated
account slots because `/u/1` exhausted its rolling quota; this is a one-carrier
coexistence result, not an account-invariance or broad production guarantee.

Files, hashes, API response payloads, and result verification live under the
untracked `.local-eval/rewatermarking-synthid-2026-09-27/`. The OpenAI batch's
two prepared upload SHA-256 values are
`f79189bcc98c6e2c0bf9737fa033b83870475560f3bff897c6e80508d90a3336`
and `6949efa56bbfb285a580994536f8ec623af801187e26ba0f27da895488571340`.
That two-result immutable batch passed `verify --require-complete`. The first
Google batch passed hash verification with 1/2 rows recorded. A one-row retry
batch for the same control passed `verify --require-complete` with one
`indeterminate` result. The submitted control SHA-256 in both batches is
`fdb34c868e533a2c3847da868c708b0c6bd5e586523ee7e6d7ee1773b321fbc4`.
Those batches are retained as evidence of the flawed visible-logo control, not
as SynthID controls. The corrected local artifacts and direct-SynthID-question
batches live under `.local-eval/rewatermarking-synthid-logo-clean-2026-09-28/`.
The control batch's single `detected` record and the candidate batch's single
`refused` record in `/u/1`, plus the separately approved `/u/2` candidate
batch's single `detected` record, each passed `verify --require-complete`. No
cloud GPU was used.

### Color restoration after regeneration (2026-09-27)

The NeurIPS 2024 "Erasing the Invisible" winner
([arXiv:2508.21072](https://arxiv.org/abs/2508.21072)) restores color after
its beige-box VAE attack in CIELAB: the output's `L` is moment-matched to the
watermarked source and the source's `a,b` replace the output's. It was tested
as post-processing on the shipped `qwen-zimage` profile at its vendor floors
(OpenAI 0.15625, Google 0.35, seed 0) over the seven tracked originals in
`data/synthid/full-pipeline-quality.csv`. Arms: `L` (moment-matched `L`,
output `a,b`) and `AB` (output `L`, source `a,b`).

- `L` changed nothing measurable: the regeneration does not shift global
  lightness at these strengths.
- `AB` lowered mean CIEDE2000 on all seven (OpenAI 3.1-3.6 to 1.9-2.2, Google
  6.0-8.6 to 4.5-6.4) and LPIPS by 5-19%.
- Official OpenAI API: all three base and all three `AB` outputs
  `not_detected`.
- Gemini: all four base outputs were settled "no SynthID" answers; the four
  `AB` outputs gave one settled "no SynthID", two "couldn't confirm" answers
  (one naming an inconclusive tool result, "edits that are too subtle or
  small to detect") and one empty `[source: 2]` answer. Recorded as one
  `not_detected` and three `indeterminate`; no row was retried. Only the
  "inconclusive" answer is an explicit tool verdict. Forty minutes later the
  same Gemini account answered "a tool error or quota limit", so the empty
  and bare "couldn't confirm" answers may be tool failures rather than signal.
- At 0.35 the regeneration redraws objects, and transplanted source chroma
  paints the old objects' colors onto the new ones as visible ghosts.

Not shipped. Source chroma is not shown safe for Google's mark: one explicit
"inconclusive" against four clean untouched outputs is a warning, not a
measured leak. The Y/Cb/Cr scramble splits above placed OpenAI's mark in luma;
if Google's does come back, either its decoder reads more than luma or the
Lab-to-RGB conversion carries source structure back into it, and these arms
do not separate the two. A
structure-gated transplant restricted to OpenAI is
the only arm left open, and its gain would be color fidelity at a floor that
already clears with margin. Hash-bound batch and verdicts:
`.local-eval/color-restoration-2026-09-27/` (`run/report.json`,
`variants.json`, `oracle/`, `gemini-batch/`).
