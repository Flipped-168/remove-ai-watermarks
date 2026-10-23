---
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
  - "scripts/**/*.py"
  - "skills/**"
  - "pyproject.toml"
  - "uv.lock"
  - "maintain.sh"
  - ".github/workflows/*.yml"
description: Command contracts, project gate, typing boundaries, model-adjacent test invariants, the agent-skill parity seam, and the detection-path measurement rule.
---

# Development invariants

## Command contracts

Every single-image command declares `source` with `dir_okay=False`; `batch` declares its directory with `file_okay=False`. Keep `tests/test_cli_robustness.py::TestDirectoryInputIsRejected` as the regression guard.

Exit-code and no-signal behavior is a public contract. Read the command-line section of [`../../docs/module-internals.md`](../../docs/module-internals.md) before changing it. The dev `.venv` always carries the pixel stack, so it cannot show what the default install does. To check a no-signal or fail-closed change there, build a throwaway venv outside the repository (`uv venv /tmp/bare && VIRTUAL_ENV=/tmp/bare uv pip install .`) and run `/tmp/bare/bin/remove-ai-watermarks` against it. Keep [`../../skills/remove-ai-watermarks/`](../../skills/remove-ai-watermarks/) in the same change when command routing, extras, exit codes, mark keys, or the intended-use boundary move.

`tests/test_agent_skill.py` enforces that by comparing the skill's prose against the live Click tree, and `test_every_cli_command_is_named_somewhere_in_the_skill` covers the whole command set, because per-flag comparisons let `--vendor`, `--pipeline auto`, `classify` and `verify-openai-synthid` ship undocumented with a green suite. Raise `MIN_CLI_VERSION` in the skill's probe whenever a reference names a command, flag or value the previous release lacked, or the probe tells an agent its CLI is current right before it types something that build rejects.

Provider verification services and provenance APIs are development-only oracles. Keep
their SDKs in the development extra and their adapters out of the installed CLI,
top-level Python API, and runtime detection/removal pipelines.

The unified maintainer entry point is `scripts/provider_oracles.py`; its workflow and
slot schema live in `docs/provider-oracles.md`. Multi-account and multi-network work
selects each named slot explicitly from the gitignored repository-local
`.oracle-slots.json` by default and snapshots it into a separate immutable batch
manifest. A provider check walks that provider's existing order: the official API
surface, then its Web oracle, then the remaining configured account slots.
After a refusal, quota response, transport error, or indeterminate verdict,
record the response and continue with the next item as its own command.
Deviation from the global rules: do not ask for confirmation before the switch,
because anyone doing the task holds standing permission to run the configured
checks. Do not add new logins, IP rotation, or unbounded retries.
Do not walk a prepared route list or rotate addresses inside one call; the next
run is a new command and picks a new session. Do not merge results from
different sessions into one response. Never commit the local
slot file.
Every manual result stays bound to the exact sanitized upload hash and preserves the
provider response verbatim.

Provider surface selection is API-first. OpenAI and Microsoft use their official API
adapters before their Web surfaces when the requested media and local configuration are
supported. Google and Meta currently use Web because this tooling has no usable API route
for them. Google's Web surfaces are `gemini-web` and `synthid-web`
(`https://synthid.com/`). After the current surface is exhausted, record the
response and continue with the next surface as its own command. One call does
not upload the same file to the next surface, and the verdicts stay separate.

A signed-in account is required only for `gemini-web`. That surface uses the user's
existing authenticated real Chrome session and an explicit `/u/N/` account index.
Every other Web surface, including `synthid-web`, uses an isolated Playwright
context and may name a proxy. Those contexts must never attach to or copy state
from the user's real browser. `synthid-web` has no `/u/N/` index. Its terms forbid
bulk verification and quota evasion, so one run submits the prepared rows once
and does not start a sign-in. If the page says `Please sign in before detection.`
and returns no watermark label, keep that row and continue the same prepared
upload in the user's existing real Chrome. That Chrome session stays on the
direct route: no proxy, no new login, and no cookie copy into Playwright. If
that Chrome also asks for sign-in, leave its row unsubmitted. API calls
stay on the direct SDK transport and do not take `proxy_url_env`. Proxy credentials are read only through a slot's named environment variable
and never enter a manifest. Dotenv interpolation may derive routed proxy URLs from
one secret key without mutating the process environment. A selected proxy context may
accept that proxy's TLS interception certificate; direct contexts keep normal TLS checks.
A ThorData exit is not prepared ahead of time. Each unauthenticated Web run picks
a new session and a country in Europe or the United States, and keeps that one exit
for the browser context so page requests do not change identity. A country or
`sessid` already written into the proxy URL is discarded. The next run picks again.
Upload readiness is surface-specific: OpenAI reaches it at page load but keeps background
requests alive, while Microsoft, Meta, and SynthID Detector require network idle. Preserve exact provider
errors as indeterminate evidence, then continue with the next configured route or surface.

OpenAI API slots likewise carry only `api_key_env`. Store multiple key values in the
gitignored `.env` and select one slot explicitly. The process environment may override
the matching `.env` value. Their SDK transport sets `trust_env=False`, so ambient proxy
variables do not reroute an API check, and the slot does not take `proxy_url_env`.
After a refusal or rate limit, continue with the next configured slot in a new call,
then with the Web surface.

Microsoft API slots use the Azure Content Safety and private Blob Storage resource
identities from the gitignored `.env`. The adapter reads resource keys only into memory
through authenticated Azure CLI, downloads and hashes the private blob before requiring
equality with the named local source, keeps `trust_env=False`, and makes one submit
inside that call. Ambient proxy settings do not apply, and the slot does not take
`proxy_url_env`. The next slot or the Web surface is a new call and runs after a
refusal, quota response, transport error, or indeterminate verdict. Report
Watermark independently from C2PA.

Do not add an option whose only outcome is an error. Model id, step count and CFG are fixed by the profile, so none of them is a parameter of the CLI, `InvisibleEngine`, or `WatermarkRemover` -- they were accepted-then-rejected for a while, which moved the failure several frames below the caller and advertised choices the pinned stack cannot honor. If a value cannot vary, delete the knob rather than validating it.

`device` is the deliberate exception and stays a library parameter: `None`/`"auto"` detect, `"cuda"` pins without detecting, and everything else raises at construction. On the image path it is not a CLI option, because the only value a user could usefully type is the one auto-detection already finds. The video SynthID commands (`video invisible`, `video all`, `video batch`) do expose `--device`, whose VAE runs on cuda, mps, or cpu, so a user can usefully pick one. `test_device_exists_exactly_where_the_skill_says_it_does` pins that split; do not read this paragraph as licence to delete the video flag.

The same rule applies to install hints: name the extra that actually makes the command work (`qwen-zimage`, not `diffusion`), and keep the printed command shell-quoted -- bare `pkg[extra]` is a glob in zsh.

## Local gate

Run `bash maintain.sh` from the repository root. The authoritative type gate is scoped to `src/`; full-project Pyright can exhaust Node memory on the ML dependency graph.

The full gate outlasts the agent's 10-minute foreground shell cap, which kills it mid-suite, so run it detached with its exit code written to a file and poll that file. To stop a stray run, kill its own PID, never `pkill -f pytest`, which also takes down other sessions' suites on the machine.

The security scanner's exit status is authoritative, including a failure after a success
message. `tests/test_maintenance.py` checks clean, vulnerable, and broken scanner
runs through the real shell entry point, and pins the CI `security` job to the
same scanner line with no `continue-on-error`. Recheck unresolved advisories using the
procedure in `docs/development.md`; do not revive the old text-matching bypass.

Boundary modules for cv2, Torch, and Diffusers may carry narrow per-file relaxations for unknown third-party types. Keep pure-logic files strict, preserve the local piexif stub, and fix real errors before widening a pragma.

From a worktree without its own `.venv`, `uv run` imports the package from the MAIN checkout, because that is where the editable install points; a worktree with its own `.venv` imports its own `src`. Either way, a script measuring a worktree's edit must assert `module.__file__` resolves inside that worktree (insert its `src` at `sys.path[0]` when it does not), or it silently compares unmodified code against itself.

## Research harnesses stay out of this repository

A research script that needs a cloud GPU account to run is not kept here, and
`scripts/` carries no `modal` import; `test_scripts_carry_no_cloud_gpu_harness`
is the canary. The identifier half of the boundary audit is deliberately not
mechanized here, because a denylist written into a tracked file publishes the
strings it exists to keep out. Twelve such harnesses were moved out on
2026-09-07; the pages that cite their findings
([chroma1](../../docs/chroma1-engine-research.md),
[module internals](../../docs/module-internals.md)) name them as harnesses kept
outside this repository, and the tracked inputs under `data/evaluations/` plus
the recorded verdicts are the durable record. Keep a new one outside too, and
leave only its offline analysis step here, the way
`scripts/analyze_engine_selection_study.py` stayed with its test.

## Visible-mark example gallery

Every registered mark carries a committed example: `data/fixtures/visible/<key>/example.png`
(image marks) and `example.mp4` (video marks), regenerated by
`scripts/render_visible_examples.py`. `tests/test_visible_examples.py` is the canary: it
fails when a mark is registered without an example and when an engine stops detecting its
own example. The examples are deterministic synthetic composites of the committed
silhouettes. When the generator fails after a geometry or gate change, fix the generator
(and the engine) together; do not hand-edit the binaries.

Visible-mark content must distinguish the registry key, the provider's canonical
product name (from the provider's official source, never an asset filename or OCR
text), and the literal text rendered in the mark whenever those differ.

## Model-adjacent tests

Do not classify an entire module as untestable because its main path downloads a model. Keep pure behavior covered without downloads, including:

- target-size selection in `test_invisible_engine.py`;
- unsharp and adaptive-polish helpers in `test_humanizer.py`;
- tiling geometry and blending in `test_tiling.py`;
- prompt-embedding cache keying, storage round-trip, and the cross-pipeline reuse
  that lets a stack load without its text encoder, in `test_qwen_zimage_pipeline.py`;
- the face stack's dtype, in `test_qwen_zimage_pipeline.py`. A subclass that changes
  the pipeline dtype for its own global model must not change the inherited face
  stage's; `sdxl-zimage` shipped doing exactly that and crashed on every image with a
  face. When one profile inherits another's stage, guard the invariants that stage
  relies on, not just the code path.
- the photo-classify gate in `test_classify.py`: DEFINITELY is ridge AND MLP,
  POSSIBLY does not emit a provider, and `identify` does not import
  `remove_ai_watermarks.classify`.
- the source-export classifier in `test_source_classify.py`: the Hub revision
  and artifact hash are immutable, the pickle-free schema and exact GELU are
  validated, threshold mutation changes the real decision, and `identify`
  never consumes the result as watermark evidence.
- the `InvisibleOptions` defaults, in `test_api.py`, compared field by field with the
  signature they mirror. Two of these defaults drifted in practice and neither needed a
  GPU to catch; the incident is recorded in `docs/module-internals.md`. Keep the
  comparison free of an exception table: a field that needs one is a field that belongs
  elsewhere, which is what `force` turned out to be.

Deviation from the global rules: reaching the real seam is not enough here; one
forwarding test sets every `InvisibleOptions` field off its default and asserts each
VALUE arrives (`test_every_field_arrives_at_the_engine_with_the_caller_s_value`),
because `_run_invisible` passed the whole suite with `controlnet_conditioning_scale`
hardcoded. A defaults comparison does not replace it.

Count the seams before believing a knob is covered. Each of `force` and
`controlnet_conditioning_scale` reaches the engine through TWO paths -- `remove_all`
versus `remove_batch(mode="all")` for the first, `_run_invisible` versus `_batch_engine`
for the second -- and in both cases guarding one path left the other free to hardcode a
constant with a green suite. The mode-parametrized guards in
`TestRemoveBatchLibrary::test_force_reaches_the_scrub_gate_in_every_scrubbing_mode` and
`TestBatchCommand::test_batch_controlnet_scale_flows_to_the_cached_engine` exist because
that is what actually happened.

Use availability checks only for paths that actually load large models.

A verdict branch must be reachable with the dependency stack as shipped. High-confidence
C2PA attribution required `signingCredential.trusted`, a code the reader emits only when a
trust anchor list is loaded, and none ships -- so the branch was dead in production for
every vendor while a hand-built info dict stamping that code kept it green from 0.27.0
through 0.30.0. `TestIdentifyRealSamples::test_no_committed_fixture_reports_a_trusted_signer`
asserts reachability against the committed fixtures. Read a capability the stack does not have
as a missing input, never as a negative finding.

## The docs are a seam, and they drift like one

`tests/test_docs_cover_the_public_surface.py` reads the live Click tree and the
live `InvisibleOptions` dataclass and requires every knob to be NAMED in the
user-facing pages. The code-to-code seams were already guarded and the
code-to-docs seam was not, so it drifted exactly the way an unguarded seam does:
`docs/cli.md` named none of `--adaptive-polish`, `--controlnet-scale`,
`--detect/--no-detect`, `--humanize`, `--strength`, `--tile-size`,
`--tile-overlap` or `--unsharp`, and `docs/python-api.md` named 9 of the 16
option fields.

Group option spellings by the Click parameter, never by a `--no-` prefix: pairs
such as `--strip-metadata/--keep-metadata` and `--keep-standard/--remove-all` are
documented by either spelling.

## One measurement, one gate seam

A detector is split into a trust-level-blind scan and a verdict that applies the
threshold, so `detect` and `detect_both` reach the same numbers by construction. Two
rules follow, and both were broken in practice before they were written down:

- A per-mark demotion goes in the `_post_gate` hook (or, for a whole-scan precondition
  like LibLibAI's size floor, in `_scan`) -- never in a `detect` override. An override
  is invisible to `detect_both`, so the RunningHub and Yuanbao anchor gates silently
  stopped applying on the arbiter's perception path. `TestSinglePassPerception` is the
  guard: it asserts `detect_both` equals two `detect` calls field for field.
- Detection and the removal mask must read ONE sweep. The winning box travels on
  `TextMarkDetection.match_box` and the registry threads the detection into the mask
  builder; a mask path that re-runs its own sweep is how the two drift apart.
- When the research lattice runtime in `scripts/synthid_runtime/` routes by image
  geometry, preserve the returned `SynthIDDetection.detector` in score manifests
  and downstream routers. Record an inactive expert as explicitly unsupported;
  never attribute a routed large-image score to the fixed expert. This expert is
  not part of the public package.

The C2PA manifest-store JSON is NOT stable across reads: the reader regenerates manifest
URNs and instance ids. Compare the derived `c2pa_info`, never the raw store.

A third seam reaches the same verdict: `collect_metadata_record` ->
`evidence_from_metadata_record` -> `identify_from_evidence`, the path a caller uses when
collection and verdict run on different machines. Its contract is equality with
`identify(path, check_visible=False, check_invisible=False)` on the same image, and it
can break from EITHER side -- a region the collector stops walking, or a placement the
file path learns to read and the record does not. `tests/test_metadata_record.py` pins
it over the tracked fixtures; a separate local evaluation corpus catches placements the
fixtures do not cover. Change either side and re-run both.

Before changing anything in the detection path, record the detectors' exact verdicts
over a local sample first and diff them after. A refactor here is only correct if that
record is byte-identical, and a green test suite does not establish that on its own. A
change that is meant to FIX detection is the exception that proves the rule: the diff
must then be exactly the files you intended to change, named in advance.

When the baseline is a published release rather than the previous commit, get it with
`uv run --isolated --no-project --with 'remove-ai-watermarks[heif]==<version>' python <script>`:
it resolves that release from PyPI without touching the working tree or the editable
install. Quote the extra -- bare `pkg[extra]` is a glob in zsh.

Two corollaries in `dwt_dct.py`, where "close enough" has an exact meaning. The bit test
is `peak % 36 > 18.0` and for uint8 input the exact Haar value is a multiple of 0.5, so it
lands ON the threshold once per 72 blocks and a 1-ulp difference flips real bits: leave the
transform to `pywt` however slow it looks, because its C convolution contracts into an FMA
that numpy has no ufunc for (`docs/module-internals.md` carries what that costs). And
`tests/test_invisible_watermark.py` skips the upstream-parity test without the `detect`
extra (`skipif(not is_available())`), so the verdict record is required here.

## A certified operating point is data, not a constant

The video SynthID default is only meaningful as a row in
`data/evaluations/video-synthid-oracle.csv`, so
`test_shipped_defaults_match_a_certified_manifest_row` derives the pin from that
manifest instead of restating literals. Pinning `noise_std` alone had let `long_side`
and `fps` -- two thirds of what the oracle was actually shown -- move with a green
suite.

The certified profile is a perturbation-to-signal ratio, not a bare `noise_std`, so
the latent scaling factor is gated in `load_video_vae_runtime`, carried on
`VideoVaeRuntime`, and passed into encode and decode: the validated value and the
applied value are one measurement. Anything that produces oracle evidence loads
through that function. `video_synthid_sweep.py` hand-rolled the load and was the one
path exempt from the gate it exists to feed, which is exactly backwards.

Prove a video-path refactor the same way the detection path is proven, and without
needing an oracle carrier: build a clip from a tracked fixture with ffmpeg, run the
engine before and after, and require an identical output sha256. Keep the generated
media outside the repository. Run both arms in one synced environment: a
full-extras `uv sync` changed re-encoded H.264 packet bytes with no code change
while every detection stayed identical (`docs/audio-provenance-experiment.md`).

Frame sampling compares `timestamp + 1e-9 >= next_sample_time`, so a `>=`-to-`>`
mutant survives; mutate the phase or the period instead (starting the accumulator
half a period late shifts the selection by one frame at an identical count), the drift
`test_pairing_follows_the_engine_sampling_rule_not_just_the_frame_count` catches.

Environment setup, dependency recovery, CI behavior, and fixture policy: [`../../docs/development.md`](../../docs/development.md).

## Audit regression contracts

Image output paths must describe the artifact published by the current call,
including skipped invisible stages and in-place writes. Carry explicit EXIF
decode state through image staging; equal dimensions do not prove that a
mirror or 180-degree rotation was applied. Metadata collection must propagate
late-read failures into an incomplete record, and stream-copy metadata removal
must map every input stream before atomically publishing the output.

Research observations must describe the decoded, hash-bound saved artifact.
Keep period selection independent of confirmation patches, require explicit
negative evidence. Use the metric's actual denominator in its name;
normalized edit distance is not reference-normalized character error rate.

Tests that reload a module after changing environment variables must restore
the environment before reloading the original state. Otherwise a temporary
cache path survives teardown and later model tests silently attempt downloads.
Dotenv configuration tests must clear every fixture variable from the invoked
process environment. Seed conflicting inherited values to prove isolation;
clearing only some fields lets the remaining host settings override the fixture.

Cross-platform tests must use host-absolute synthetic interpreter paths and
explicit unchanged decodes when comparing stored pixels. Execute Ubuntu Bash
workflow harnesses only on POSIX hosts with Bash; keep their pure Python checks
active on every platform. Round floating-point image output before uint8
conversion when quantization must preserve constant values across OpenCV builds.
OpenCV 5 draws Hershey `putText` glyphs smaller and heavier than 4.x, so a
calibrated template drawn with `putText` ships as a committed PNG whose recipe
refuses any OpenCV but 4.x (`scripts/render_video_hershey_templates.py`,
`scripts/build_openart_alpha.py`); never render one at import time.
