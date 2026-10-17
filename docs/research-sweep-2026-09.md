# Research sweep, September 2026

A survey of every area the library works in, run on 2026-09-22 and 2026-09-23 to
find what changed since the topic pages were written and what earlier research
missed. Nine areas were covered: Google SynthID, other vendors' invisible
watermarks, the watermark attack literature, visible AI labels, metadata and
provenance standards, video and audio, AI image classifiers, law and regulation,
and fill or regeneration models with competing tools. Claims were checked
against primary sources (specifications, vendor documentation, legal texts,
arXiv pages); live captures from the maintainer's accounts settled several
questions directly.

This page is an index. Each finding lives in its canonical page.

## Where the findings went

| Area | Change | Page |
| --- | --- | --- |
| Law and regulation | Research purpose, no-liability notice, jurisdiction table (China, EU, India, US, South Korea), platform labeling behavior | [legal-and-safety.md](legal-and-safety.md) |
| SynthID adoption | 100B+ items, ElevenLabs and OpenAI audio (with OpenAI's verification API limits), Apple (announced), Vertex C2PA, Nano Banana 2 Lite and Gemini Omni Flash, optional visible mark, portal status | [synthid.md](synthid.md), [provider-oracles.md](provider-oracles.md) |
| Other vendors | Microsoft Foundry provenance for Azure-hosted Flux and MAI, Amazon Nova Reel, audio adopters | [watermarking-landscape.md](watermarking-landscape.md) |
| C2PA 2.3 and 2.4 | `c2pa.ai-disclosure` and ingredient `digitalSourceType` now read; parser claim corrected | [watermarking-landscape.md](watermarking-landscape.md) |
| Containers | GIF metadata stripped without re-encoding; TIFF and DNG refused; C2PA after large WAV and AVI data now scanned | [known-limitations.md](known-limitations.md) |
| TC260 in audio | WAV, MP3, OGG, Opus and FLAC label placements from the 2025-08 audio guide | [supported-signals.md](supported-signals.md) |
| Video labels | Sora discontinued; opening-only labels no longer filled over the whole clip; any video mark vetoed by another vendor's C2PA AI claim, Kling also by a non-Kling TC260 producer; TC260 video producers named | [supported-signals.md](supported-signals.md), [known-limitations.md](known-limitations.md) |
| Apple | Image Playground and Photos Clean Up credits attributed | [supported-signals.md](supported-signals.md) |
| New visible marks | `vidu` video mark and `wan` image mark, each calibrated on one real export | [supported-signals.md](supported-signals.md), [known-limitations.md](known-limitations.md) |
| Google Photos | AI edits attributed to "Google Photos (AI edit)". Four earlier edits and two later large edits were SynthID-positive; two later small edits were indeterminate. Presence inferred from provenance needs file-specific confirmation | [synthid.md](synthid.md), [supported-signals.md](supported-signals.md) |
| YouTube | Upload test: C2PA-driven "Made with AI" label, public streams without C2PA, Studio downloads re-signed by YouTube; re-encoded non-Google video no longer read as Google AI with SynthID | [supported-signals.md](supported-signals.md), [legal-and-safety.md](legal-and-safety.md), [module-internals.md](module-internals.md) |
| Audio | Generated audio from OpenAI, ElevenLabs and Microsoft passes through the video path unchanged | [known-limitations.md](known-limitations.md) |
| Attack literature | Fidelity band on open encoders now 30-45 dB; WmForger and WMCopier status | [synthid-removal-research.md](synthid-removal-research.md), [watermark-forgery-study.md](watermark-forgery-study.md) |
| Models | FLUX.2 klein has a strength-controlled pipeline in diffusers | [chroma1-engine-research.md](chroma1-engine-research.md) |
| Dependencies | TrustMark extra on every supported Python (`trustmark>=0.9.2`) | [installation.md](installation.md) |
| Live captures | Gemini Omni, Grok, Vidu, Wan, Apple, Google Photos, Nano Banana 2 Lite and Gemini Omni Flash through the API; Runway, Higgsfield and Dreamina | [watermarking-landscape.md](watermarking-landscape.md#live-captures-2026-09-23-and-2026-09-24) |

## Follow-up status

The original follow-up list now mixes completed experiments, deliberately
excluded claims, and acquisition gaps. Each row below names its current status
as of 2026-10-01 so this section can serve as the research backlog without
discarding the measured results.

- **Closed - Google Photos Reimagine manifests.** Magic Editor, and so
  Reimagine, is not offered in Google Photos on iOS, so no Reimagine file is
  captured. The
  question it was meant to answer is settled without one: Google's checker found
  SynthID in all four Photos AI edits tested on 2026-09-25, none of which
  records SynthID in its manifest.
- **Open - Vidu and Wan marks on more samples.** Both are registered from one
  real export each (`vidu` video, `wan` image); their gates are provisional until a
  wider cohort is measured, and a Wan video label is not yet captured. Public
  Vidu feed videos (2026-09-26) carry the TC260 label naming ShengShu, and one
  names Tongyi Yunqi as producer with Vidu as propagator, but none shows the
  visible `Vidu` mark; Wan's public demo videos show no mark either. Both marks
  appear only on account downloads.
- **Partially complete - TC260 practice guides.** The audio placements from
  TC260-PG-202510A are now read (the guide PDFs load in a browser from
  `tc260.org.cn/tc260/sjzn/list.shtml`, not to scripted requests). The text-file
  guide (TC260-PG-20258A) covers documents this image and video tool does not
  process. The security-protection guide (TC260-PG-202511A) records a
  `SecurityData` JSON object, a digital signature over the label and optionally
  the content, in `ReservedCode1` and `ReservedCode2`. MiniMax was the one
  producer in the local corpus writing a guide-shaped object when checked
  on 2026-09-29 (Honor RSA/content samples were added in the public-web
  follow-up below): four MiniMax videos served by Higgsfield and Runway, two of them
  tracked (`higgsfield-hailuo-2-3.mp4`, `higgsfield-minimax-h3.mp4`), carry
  `SecurityData` with two SM3withSM2 (`1.2.156.10197.1.501`) signatures and one
  public key, `KeyValue` `00a0b3b0...47e4fd` in all four. The label signature
  verifies on all four against the guide's appendix A.1 message, the ASCII string
  `"Label":"1","ContentProducer":"MiniMax","ProduceID":"<id>"`, with the default
  SM2 user ID `1234567812345678` and the key's x coordinate lifted to the even-y
  point; changing one `ProduceID` digit fails it. MiniMax's own spellings depart
  from the guide: `TBSData.Type` is `LabelMataData` (the guide's `Md`) and
  `Binding` with `BType` `0` (its `Bnd`); the second signature verifies over the
  compact JSON of the `Bindings` entry, also on all four. TC260-PG-202511A
  appendix A.2 was re-read from the
  [official PDF](https://www.tc260.org.cn/tc260/sjzn/202508/63ab55a3265f45c7865e9b8be15d4a29/files/dc379ec776f94abc8f1806affa1cda35.pdf)
  on 2026-10-01. MiniMax omits its `CntSel`, and none of the guide-derived
  byte selections reproduced its SM3 content hash on four measured videos, so
  the content binding remains unverified
  ([module internals](module-internals.md)). Other producers fill the same
  fields with opaque vendor strings (Qwen a base64 digest, Vidu 32 hex digits,
  Wan and HappyHorse `L-`/`K-` prefixed values), not `SecurityData`. The key sits
  in the file it signs, so a check proves authenticity only against a pinned
  MiniMax key. `identify` now verifies it with a built-in SM3/SM2 and a pinned
  MiniMax key. The remaining work is
  MiniMax content-binding verification if its byte-selection rule becomes known,
  and Honor's unsupported RSA/content form if an original export and signing
  contract become available.
- **Partially complete - experiments.** Five of the six follow-ups are closed:
  Z-Image-Turbo, Perth and PixelSeal, re-watermarking, VACE/ROSE, and newer
  frozen-backbone probes. Chroma
  restoration after regeneration (arXiv:2508.21072) was
  measured on 2026-09-27 and is not shipped: transplanted source chroma drew one
  explicit "inconclusive" and two unclear Gemini answers where the untouched
  outputs were all clean, and ghosts redrawn objects
  ([removal research](synthid-removal-research.md#color-restoration-after-regeneration-2026-09-27)).
  FLUX.2 klein 4B was measured the same day: stock inpainting copies the
  source through its reference tokens and keeps OpenAI SynthID, and without
  them it clears both vendors only at lower face and CJK-text fidelity than
  `qwen-zimage`
  ([Chroma1 research](chroma1-engine-research.md#flux2-klein-as-a-global-stage-2026-09-27)).
  Apache-2.0 temporal video inpainting was also measured: VACE and ROSE were
  less stable than MI-GAN on all three Sora, Veo, and Kling clips, VACE left a
  gray block on Veo, and ROSE retained the Veo wordmark on 17/17 frames. They
  are not shipped
  ([video inpainting research](video-inpainting-research.md)).
  Resemble Perth and Meta PixelSeal were added as exact-revision, MIT-licensed
  local benchmark oracles. The 2026-09-28 study found Perth on all three speech
  positives and confirmed that visible-video cleaning copies its marked AAC
  packets unchanged; PixelSeal survived JPEG q90 on both cleared image
  carriers, while its CUDA-only removal profiles could not run on this host
  ([benchmark study](benchmark-kernel.md#perth-and-pixelseal-local-oracle-study)).
  Re-watermarking (arXiv:2605.16796) was reproduced locally on 2026-09-27:
  same-encoder message B replaced A on all 12/12 valid TrustMark and 12/12
  VideoSeal image controls, both VideoSeal video clips, and all 6/6 valid
  controls in each DWT-DCT direction. Median image clean-to-output PSNR was
  39.73-44.15 dB; the DWT-DCT controls worked on only half the carriers.
  This is an open-encoder result, not a SynthID result
  ([removal research](synthid-removal-research.md#re-watermarking-on-open-encoders-2026-09-27)).
  A one-carrier production probe subsequently kept OpenAI SynthID `detected`
  on both its metadata-free control and 43.04 dB VideoSeal-overlaid image;
  a visible-clean, metadata-free Google control and its 42.86 dB VideoSeal
  overlay also remained `detected` under direct SynthID-tool checks. The Google
  control and candidate positives came from different approved account slots,
  so this remains a one-carrier coexistence result
  ([removal research](synthid-removal-research.md#production-synthid-overmark-probe-2026-09-27-local)).
  Z-Image-Turbo was measured on 2026-09-29. It is not a global replacement:
  at its OpenAI margin point it improves both no-face typography carriers but
  loses face identity, and the same face/text split is stronger in the Google
  fidelity probe. The Google no-face outputs at 0.40 also visibly redraw scene
  geometry and object detail, despite better OCR and aggregate metrics, so a
  face detector alone cannot make a safe complement. The last Google boundary
  is unresolved because the available oracle checks were quota-blocked or
  could not accept the prepared upload.
  The mflux arm works on an M5 with 32 GB and is the only measured native Apple
  Silicon image-regeneration path, since every shipped image profile is
  CUDA-only. It took 301-380 seconds per image. This proves M5 feasibility but
  is not a usable fallback at the measured quality
  ([Chroma1 research](chroma1-engine-research.md#z-image-turbo-as-a-global-stage-2026-09-29)).
  The experiment is closed with a decision not to add a global or mflux
  profile; retain its harness and local evidence for future comparison only.
  The existing source-conditioned Z-Image face-repair stage remains part of
  `qwen-zimage`, `sdxl-zimage`, and `chroma-zimage`.
  The pre-registered modern-backbone campaign found that neither frozen
  SigLIP2 Base nor PE-Core B could match the production model's combined photo,
  AI, and FLUX constraints, so the replacement hypothesis is closed
  ([classifier research](ai-generated-image-classifiers.md#modern-frozen-backbone-campaign-closed-2026-09-27)).
  Only RAVEN view-synthesis removal remains blocked. RAVEN's
  [official repository](https://github.com/fahadshamshad/raven-watermark-removal)
  now exists, but its 2026-08-08 README is still a release placeholder: the
  authors say they will publish code after their SynthID testing and Google
  Security Bounty submission. There is no implementation to evaluate as of
  2026-10-17, when the repository still held only that README (arXiv:2601.08832).
  MiniMax-Remover (CC-BY-NC-4.0 weights) and ProPainter (S-Lab License,
  non-commercial) are deliberately excluded on license and are not backlog
  items.
- **Open - new C2PA signers without a vendor row.** The
  [C2PA conformance list](https://github.com/c2pa-org/conformance-public/blob/main/conforming-products/conforming-products-list.json)
  names generator certificates `Amazon Bedrock`, `Getty Images
  AI-Generated Image` and `AI-Modified Image` (and the iStock pair), `Jasper`,
  `RefaceAI`, and vivo `vivo Albums` and `JOVI Albums`. It also lists `Google
  Photos` for both Android and iOS, the signer the Photos rule keys on. A
  real sample per vendor is still needed to confirm the manifest shape before
  adding a row. Runway is done: its own models sign as `RUNWAY AI, INC.`
  (measured 2026-09-24) and the row covers the conformance-list spelling too.
  Amazon is done: Nova Canvas and Nova Reel outputs published in
  `aws-samples/amazon-nova-samples` sign as `Amazon Web Services, Inc.` with
  claim generator `Amazon Bedrock` (2026-09-26), and had been reported as Canva
  because the byte fallback matched `Canva` inside `Nova Canvas`. A search on
  2026-09-26 found no public Getty, iStock, Jasper, RefaceAI or vivo Albums file
  carrying C2PA: their marketing and model-page images are unsigned. A vivo
  X300 camera capture carries a vivo device manifest (`digitalCapture`) that
  the bundled reader cannot open (`unknown algorithm`).
- **Open - Chinese phone galleries.** Huawei's help pages say the Xiaoyi photo-edit AI
  watermark can be switched off; vivo's Album setting is already covered.
  The public-web follow-up below found Honor YOYO metadata and additional
  primary-source labeling evidence, but not a controlled gallery export set. A live
  conformance-list recheck on 2026-09-30 also found `Xiaomi MediaEditor` as a
  generator product, `Xiaomi Gallery` as a validator, and both generator and
  validator entries for `vivo Albums` / `JOVI Albums`. These roles describe C2PA
  production and validation, not whether an edit is generative. Original exports
  of an unedited control, an ordinary crop, and a generative edit are still needed
  per app before selecting an AI attribution rule. Record the device, OS/app
  version, region, operation, and original download path with each sample.
- **Closed - claims not supported by a primary source.** Kling embedding SynthID
  (repeated by remover blogs; Kuaishou is not in Google's adopter list),
  Hailuo pixel watermarks, and platforms stripping C2PA on upload. None is used
  by the library.
- **Partially complete - Google Photos small edits (further work deferred,
  2026-10-01).** The
  maintainer deferred further photographic tiny Magic Eraser captures and
  verification retries for the inconclusive small edits. Resume only on an
  explicit request; retain the existing evidence and uncertainty. On
  2026-09-30, iPhone Mirroring successfully exposed the iOS
  editing toolbar. One source and five separate copies were captured: a large
  Magic eraser edit, a small removal through `Help me edit`, a small color
  change through the same tool, a watercolor restyle, and a crop-only control.
  The four AI exports carry Google Photos C2PA with valid signatures and asset
  bindings; the signer remains untrusted without a configured trust-anchor list.
  Neither the unchanged source nor the crop control has detected AI metadata.
  Original-quality downloads, hashes, operation records, and metadata reports
  are retained privately outside the repository. The restyle was exported at
  768 x 1365; the other AI copies retain the source's displayed dimensions.
  The hash-bound Gemini batch passed complete verification on 2026-10-01 UTC:
  large Magic Eraser and watercolor restyle were `detected`; small removal and
  recoloring through `Help me edit` were `indeterminate`, with a possibly
  too-small edit cited; source and crop were `not_detected`. AI metadata was
  stripped without changing decoded pixels. All six settled replies were
  recorded, one file per new chat. No quota refusal occurred and no request was
  repeated. The Photos-specific report caveat now names the inconclusive small
  edits rather than describing every tested AI edit as positive. A tiny photographic
  Magic Eraser mask remains unmeasured: its automatic selection expanded to a
  large region, so the small removal used `Help me edit` instead. One source and
  one export per operation cannot establish representative or repeatable behavior.
  Follow-up checks across two additional accounts left recoloring and the
  synthetic tiny Magic Eraser control inconclusive; small removal returned one
  negative and one inconclusive reply. The quota refusal, synthetic capture,
  pixel comparison, mode caveat, and hash-bound outcomes are recorded in
  [synthid.md](synthid.md).
- **Partially complete - direct captures blocked by region or device.** Direct,
  controlled captures remain blocked for Doubao, Jimeng, and Samsung. The
  public-web follow-up below later found one real marked Doubao video and
  validated its visible mark and TC260 metadata, but the file remains local
  because publication has not been cleared; it is not a controlled account
  capture or a redistributable fixture. Higgsfield, Runway, and Dreamina were
  captured on paid plans on 2026-09-24.

### Public-web sample search, 2026-10-01 UTC

The follow-up searched official product/model pages, support articles,
provider communities, public share links, and public sample repositories.
Candidates were downloaded unchanged to a gitignored local evidence directory,
with source URLs, referring pages, SHA-256 hashes, metadata inspection, and
contact sheets. Website assets include icons, UI screenshots, source images,
outputs, and duplicate size variants; their count is not a count of genuine
provider exports. No third-party photograph was added to tracked fixtures.

- **Honor YOYO: metadata sample found.** Two JPEGs in this
  [author's edit thread](https://club.honor.com/cn/thread-29898091-1-1.html)
  retain EXIF `UserComment` containing `AIGC`, producer
  `001191440300MA5G49LC9K1YO01`, and nested `TC260PG` blocks with RSA/SHA-256
  OID `1.2.840.113549.1.1.11`. The author's post reports a Magic6 Pro;
  OS/app versions are unknown. The downloaded files are 1312 x 736 and smaller
  than the attachment sizes displayed by the forum, so original export fidelity
  is unproven. Their visible overlay includes a community account attribution,
  which is not evidence of an AI disclosure badge. The reader now preserves
  nested reserved fields as JSON and attributes the measured code to Honor.
  It reports the RSA/content signature as unsupported.
  Public-key exponentiation on both signatures yields PKCS#1 type-1 padding
  followed by a bare 32-byte value, without the SHA-256 DigestInfo prefix;
  that value differs from the downloaded file hash. Together with null
  `Bindings.Value`, `TBSData.Type=Content`, no content-selection method, and
  forum resizing, this leaves asset integrity unverified. An embedded public
  key alone would not establish manufacturer identity either.
  Honor's [official privacy statement](https://agreement.itsec.honor.com/asm/agrFile/getHtmlFile?agrNo=1477&branchId=0&country=ru&langCode=en-US&version=20250517)
  independently confirms the producer's USCC. Historical replay also found
  that company code with a different product suffix; attribution names Honor,
  because the USCC alone does not establish the application. A publication-safe
  structural fixture and lossless metadata-removal test are documented in
  [the fixture catalog](../data/fixtures/README.md#honor-yoyo-metadata-reconstruction).
- **vivo and Huawei: UI/source evidence, not original gallery exports.**
  [vivo technical support](https://bbs.vivo.com.cn/newbbs/thread/39038829)
  enumerates image/video AI operations that add the label, while a
  [hands-on guide](https://bbs.vivo.com.cn/newbbs/thread/39038546?show_title=1)
  locates `AI生成` at the upper right. Downloaded community illustrations show
  settings and editing UI, not a verified signed Albums export.
  [Huawei's Xiaoyi support article](https://consumer.huawei.com/cn/support/content/zh-cn16070847/)
  supplies editing/save UI illustrations; those do not establish exported metadata.
- **OPPO: primary labeling statement found.** Its
  [imaging product manager interview](https://www.oppo.com/en/newsroom/stories/empowering-creative-freedom-and-expression-in-mobile-photography-with-ai/)
  states that AI-generated content is labeled. It does not specify the export
  label's shape or metadata. Its downloadable press kit supplies before/after
  JPEG pairs for Clarity Enhancer, Reflection Remover, and Unblur, with several
  3072 x 4096 images. These fetched pairs had no recognized C2PA/AIGC label;
  they are useful local comparison material but not verified generative-edit
  exports. Camera AI enhancement and ordinary camera-brand
  watermarks remain separate from generative-edit provenance.
- **Jasper, Getty/iStock, RefaceAI: C2PA gaps remain.** Downloaded assets from
  [Jasper's endpoint examples](https://images.jasper.ai/cleanup),
  [Getty's generator page](https://www.gettyimages.com/ai/generation),
  [iStock's generator page](https://www.istockphoto.com/ai/generation), and
  [Reface's product site](https://reface.ai/) did not carry locally recognized
  C2PA. A 2026-10-01 recheck of Jasper's current official Image landing page
  reached its pre-rendered endpoint outputs directly and again found no C2PA.
  Jasper explicitly distinguishes input/mask/output examples, but an unsigned
  web derivative cannot establish its signed export's manifest shape.
  Conformance certificates alone still do not justify fabricating that shape.
- **Visible-image/video provider-original gaps remain.** Every registered mark
  already has a publication-safe synthetic detector fixture in the
  [visible-mark gallery](../data/fixtures/visible/README.md); the sample ledgers
  now point to those fixtures and distinguish them from provider evidence. The
  downloaded RunningHub workflow
  illustrations are explanatory/branding assets, not verified output examples;
  Liblib API documentation's cat illustration has no visible historical wordmark.
  A public [Inkpainting model page](https://www.liblib.art/modelinfo/2acd393c23924ff9b5363c9c1ec9129f)
  explicitly attributes its example generation to Liblib; its read-only model
  lookup supplied nine full PNG examples. These show ink-style illustrations
  and a model cover, without the historical LiblibAI wordmark.
  A public Vidu homepage MP4 was obtainable, but the inspected frame has no Vidu
  mark. Seedance and Wan marketing assets, Dola extension screenshots, and
  the Doubao share page did not initially yield marked consumer videos. A
  subsequent public `samantha/media/get_play_info` lookup returned a 720 x 960,
  10.08-second H.264/AAC MP4 (SHA-256
  `0a000352e6f9b3e8417e57403572ef4a7a0e94fc8840217162e90c199a478def`).
  Its decoded frame visibly carries `豆包AI生成` at bottom right; the file
  remains local because publication has not been cleared. `identify_video`
  attributes it to ByteDance Doubao and detects the mark on all 241 frames;
  its MP4 TC260 producer is `001191110102MACQD9K64010000`.
  Samsung's support illustrations are UI evidence, not a controlled original
  export set. No new visible template or proprietary-watermark verdict follows
  from these candidates. Xiaomi labeling tutorials surfaced, but their attribution
  and original exports remain unverified.

Next acquisition targets remain a signed export per missing C2PA signer, an
unedited/crop/generative-edit set per gallery, and original marked consumer
videos. Honor's nested RSA signature form is a separate verification gap; the
synthetic fixture deliberately does not pretend to close it.

## Decisions

- **Dreamina `AI` badge: not registered (2026-09-26).** Dreamina stamps a small
  boxed `AI` badge top-left on images and video, and calls it its visible AI
  watermark. It stays unregistered for three reasons. A generic boxed `AI` is the
  shape of the disclosure icon the EU Code of Practice defines, which this
  project does not template, so a template would remove any such label. The same
  generic shape would match other platforms' badges and plain `AI` text and
  misattribute them to Dreamina. And it adds nothing to attribution: Dreamina
  exports are identified by their C2PA (`ByteDance Media Transcode Service`
  signer with a `Dreamina/7.5.0` ingredient), and Dreamina's own "Remove watermarks" setting
  removes the badge. Revisit only if the badge becomes a distinctive brand mark.
