# Creative AI Studio — GitHub Audit

Audit date: 2026-11-13 · Method: shallow clones and file-by-file inspection. No repository script was executed. No API keys were used or stored.

---

## 1. Bottom line

| | |
|---|---|
| Repos you listed | 15 (one URL is wrong, two have moved; see §2) |
| Repos that contain real Agent Skills | 7 (anthropics/skills, taste-skill, ui-ux-pro-max-skill, vercel-labs/agent-skills, hyperframes, remotion, OpenMontage) |
| Extra upstream skill repos found | 2: `greensock/gsap-skills` (official GSAP) and `CloudAI-X/threejs-skills`. OpenMontage copied its GSAP and Three.js skills from these two. |
| Skills packaged as ZIPs | **30** (27 recommended, 3 optional), all checked against the claude.ai upload rules |
| Skills not packaged | Remotion (you already have the same version), HyperFrames (needs its CLI), taste-skill (too large), API-key and CLI skills (see §5) |
| Software, models and frameworks | 10 of them. **These are not Skills and cannot run inside claude.ai.** See §3. |

**The honest limit:** claude.ai runs code in a small sandbox with **no GPU**. It can write code, HTML, React, Three.js, GSAP and Remotion source files, ComfyUI workflow JSON, Blender Python scripts and FFmpeg commands. It **cannot** run ComfyUI, Blender, LivePortrait, OpenVoice, AnimateDiff or a 4K render. For those you need a GPU PC or a rented cloud GPU. Skills make Claude better at *authoring* this work. They don't replace the hardware that renders it.

---

## 2. Corrections to your URL list

| You gave | Reality |
|---|---|
| `comfyanonymous/ComfyUI` | Redirects to **`Comfy-Org/ComfyUI`** |
| `KwaiVGI/LivePortrait` | Redirects to **`KlingAIResearch/LivePortrait`** |
| `threejs/three.js` | **Does not exist.** The official repo is **`mrdoob/three.js`**. |
| `blender/blender`, `FFmpeg/FFmpeg` | Read-only GitHub mirrors. Development happens at projects.blender.org and ffmpeg.org. |

---

## 3. Classification of all repositories

Star counts are from GitHub search on the audit date. "Last push" is the latest commit on any branch.

### A. Agent Skill repositories (contain valid `SKILL.md` skills)

| Repo | ★ | License | Last push | What it is | Verdict |
|---|---|---|---|---|---|
| anthropics/skills | 194,040 | Apache-2.0 per skill (docx/pdf/pptx/xlsx are source-available) | 2026-11-06 | Anthropic's official example skills | Packaged `frontend-design`. Optional: `web-artifacts-builder`, `algorithmic-art`, `canvas-design`. Skipped docx/pdf/pptx/xlsx/skill-creator because they are **already on your account**. |
| nextlevelbuilder/ui-ux-pro-max-skill | 149,004 | MIT | 2026-11-10 | UI/UX design intelligence: styles, palettes, font pairings, UX rules. Uses a local Python search over CSV files. | **Packaged** `ui-ux-pro-max`. The scripts are offline CSV search only. Reviewed: no network calls or keys needed. |
| Leonxlnx/taste-skill | 114,844 | MIT | 2026-11-08 | Excellent anti-generic website skill (v2.5.1) | **Not packaged.** It has 1,631 files and 38 MB of assets. Its quality gate drives a real browser through Node/Playwright scripts. That exceeds the reported ~200-file limit for claude.ai skills and won't work in the web sandbox. Best used in Claude Code or the desktop app. |
| vercel-labs/agent-skills | 34,004 | MIT (stated in SKILL.md) | 2026-11-12 | Vercel's React/Next.js engineering skills | **Packaged** react-best-practices, composition-patterns, react-view-transitions, web-design-guidelines. Skipped deploy/CLI/token skills and react-native. |
| heygen-com/hyperframes | 83,795 | Apache-2.0 | 2026-11-13 | HTML-to-video framework plus 9 public skills | **Not packaged** (see §5). Every workflow requires `npx hyperframes`, headless Chrome and FFmpeg. The main skill also runs a telemetry "usage beacon" on each start. |
| remotion-dev/remotion | 72,956 | Remotion License (free for individuals and companies with ≤3 employees; paid company license above that) | 2026-11-13 | Official 13 Remotion skills, v4.0.543 | **Preserved yours.** Your `remotion-best-practices` is **v4.0.543, identical to upstream**, so it's already current. `remotion-motion-graphics` was untouched. |
| OpenMontageInc/OpenMontage | 80,220 | **AGPL-3.0** | 2026-11-09 | AI video *pipeline* that bundles ~90 skills, mostly copies | **Not packaged from here.** Its GSAP, Three.js, Vercel and Remotion skills are copies of upstream repos. I packaged the originals instead, which have cleaner MIT licensing and no duplicates. The remaining skills mostly need paid APIs (ElevenLabs, HeyGen, Kling, BFL and others). |
| *greensock/gsap-skills* (found) | 18,402 | MIT | 2026-07-29 | **Official** GSAP skills: 8 pure-Markdown skills | **Packaged all 8.** |
| *CloudAI-X/threejs-skills* (found) | 4,170 | MIT | 2026-10-19 | 13 pure-Markdown Three.js skills | **Packaged all 13.** |

### B. Frameworks and libraries (code you use; not skills)

| Repo | ★ | License | Maintained | Hardware | Role in your studio |
|---|---|---|---|---|---|
| greensock/GSAP | 30,571 | GSAP Standard "no charge" license. 100% free including SplitText and MorphSVG, also for commercial use. | Yes | Any browser | Web and motion animation. **The repo contains no skills**, so use the `gsap-*` skills. |
| mrdoob/three.js | 118,300 | MIT | Very active | WebGL/WebGPU in the browser | 3D websites (requirement 9) |
| remotion-dev/remotion | 72,956 | Remotion License | Very active | CPU rendering; Chrome plus FFmpeg on your machine or Lambda | React video, logo intros, brand films |
| heygen-com/hyperframes | 83,795 | Apache-2.0 | Very active | Node 22+, Chrome, FFmpeg | HTML+GSAP to deterministic video |

### C. Desktop and server software (installed on a computer; not skills)

| Repo | ★ | License | Maintained | Hardware |
|---|---|---|---|---|
| Comfy-Org/ComfyUI | 146,658 | GPL-3.0 | Very active | NVIDIA (20-series+), AMD, Intel, Apple Silicon. README claims it can run large models on 4 GB VRAM with offloading. In practice, plan for **12–24 GB VRAM** for modern video models. |
| blender/blender | 21,949 | GPL-2.0-or-later | Very active | Any GPU. Cycles is fastest on NVIDIA (OptiX), AMD (HIP) or Apple Metal. |
| FFmpeg/FFmpeg | 67,186 | LGPL-2.1+ (GPL in some builds) | Very active | CPU. NVENC, QSV and VideoToolbox add hardware encoding. |
| OpenMontageInc/OpenMontage | 80,220 | AGPL-3.0 | Active | Python plus Node. Optional GPU for local WAN/Hunyuan. Most quality paths depend on paid API keys. |

### D. AI models and research code (not skills)

| Repo | ★ | License | Maintained | Hardware |
|---|---|---|---|---|
| KlingAIResearch/LivePortrait | 19,475 | MIT code, **but the bundled InsightFace models are non-commercial**. Replace them before any client or commercial work. | Last push 2026-06 | NVIDIA CUDA recommended. Apple Silicon works but is "~20× slower than RTX 4090" per the README. |
| myshell-ai/OpenVoice | 38,233 | MIT (V1 and V2, commercial OK) | **Slowing**: last push 2025-04 | NVIDIA GPU recommended |
| guoyww/AnimateDiff | 12,295 | Apache-2.0 | **Stale**: last push 2024-07. Based on SD 1.5 and an SDXL beta. | NVIDIA GPU. Motion modules are ~1.5–1.9 GB. |

**Quality note:** AnimateDiff is superseded. For smooth anime and character motion today, use the video-model workflows inside ComfyUI (for example WAN 2.x, which OpenMontage also lists). Don't treat AnimateDiff as a separate install. OpenVoice still works for voice cloning but sees little maintenance. Treat it as an option, not the default.

---

## 4. Packaged skills (30 ZIPs)

All ZIPs are in `skills-zips/`, and every one was checked automatically:
- The skill folder is the ZIP root, and the folder name equals the `name` field.
- Names are lowercase with hyphens, ≤64 characters, and don't contain "claude" or "anthropic".
- Descriptions are ≤1,024 characters with no XML tags. Your account already accepted a 666-character description, so the 200-character figure in one help article isn't enforced.
- Each skill has ≤200 files and no symlinks.
- The upstream LICENSE is included in every ZIP where the folder didn't already have one.
- None of them need an API key.

### Tier 1: Web, UI/UX, React and Next.js (6) → requirements 6, 7

| ZIP | Source | Notes |
|---|---|---|
| `ui-ux-pro-max.zip` | nextlevelbuilder | Design-system generator. Runs local Python only. |
| `frontend-design.zip` | anthropics | Anthropic's anti-generic frontend aesthetics guide |
| `vercel-react-best-practices.zip` | vercel-labs | Performance rules for React and Next.js |
| `vercel-composition-patterns.zip` | vercel-labs | Component architecture patterns |
| `vercel-react-view-transitions.zip` | vercel-labs | **One patch:** I removed the angle brackets around `ViewTransition` in the description, because claude.ai rejects tags there. The body is unchanged. |
| `web-design-guidelines.zip` | vercel-labs | **Heads-up:** this skill downloads its rule list from `raw.githubusercontent.com/vercel-labs/...` every time it runs. That needs web access, and it means its instructions can change upstream without you seeing it. |

### Tier 2: GSAP motion (8, official GreenSock) → requirement 10

`gsap-core`, `gsap-timeline`, `gsap-scrolltrigger`, `gsap-react`, `gsap-plugins` (SplitText, MorphSVG, MotionPath), `gsap-utils`, `gsap-performance`, `gsap-frameworks`

### Tier 3: Three.js 3D (13) → requirement 9

`threejs-fundamentals`, `-geometry`, `-materials`, `-lighting`, `-textures`, `-shaders`, `-postprocessing`, `-animation`, `-interaction`, `-loaders`, `-asset-pipeline`, `-performance`, `-react-three-fiber`

### Tier 4: Optional creative (3)

| ZIP | Use | Note |
|---|---|---|
| `web-artifacts-builder.zip` | Larger React + Tailwind + shadcn artifacts in claude.ai | Runs `npm`/`pnpm` installs in the sandbox, so package-manager network access must be allowed |
| `algorithmic-art.zip` | Generative p5.js art for brand backgrounds | |
| `canvas-design.zip` | Posters and static brand art | 83 files (bundled fonts), 2.5 MB |

**If you want fewer skills:** start with Tier 1 plus `gsap-core`, `gsap-timeline`, `gsap-scrolltrigger`, `gsap-react`, `threejs-fundamentals`, `threejs-materials`, `threejs-lighting`, `threejs-postprocessing` and `threejs-react-three-fiber`. That's 15 skills. Add the rest when you need them.

---

## 5. Real skills I deliberately did NOT package

| Skill(s) | Reason |
|---|---|
| Remotion: 13 official skills | You already have `remotion-best-practices` **v4.0.543 = upstream**, and it routes to these. Re-uploading would create duplicates. Your `remotion-motion-graphics` was left alone. |
| HyperFrames: hyperframes, -cli, -registry, media-use, figma, slideshow, style-sampling, reverse-any-video, remotion-to-hyperframes | Every workflow calls `npx hyperframes` (render, check, preview) with Chrome and FFmpeg. The main skill also runs a telemetry command each time it starts. Several need HeyGen, ElevenLabs or OpenAI keys. **Use them in Claude Code or the Claude desktop app on a computer**, where the CLI can be installed. |
| taste-skill | 1,631 files and 38 MB. Its checker drives a real browser through Node/Playwright scripts. |
| ui-ux-pro-max extras: banner-design, brand, design, design-system, slides, ui-styling | They overlap with `ui-ux-pro-max` and `frontend-design`, and `design` expects Gemini or other image API keys. Optional later. |
| vercel: deploy-to-vercel, vercel-cli-with-tokens, vercel-optimize | They need the Vercel CLI, tokens or the Vercel API. They aren't usable from a phone browser. |
| anthropics: docx, pdf, pptx, xlsx, skill-creator | Already on your account |
| anthropics: claude-api, mcp-builder, internal-comms, slack-gif-creator, others | Not relevant to your requirements |
| OpenMontage: about 90 skills | Duplicates of upstream sources, AGPL wrapper, or need paid provider keys |

---

## 6. Requirement → recommended stack

| # | Requirement | Inside claude.ai (Android) | Needs a GPU PC or cloud GPU |
|---|---|---|---|
| 1 | Photorealistic 3D CGI, 4K video | Claude writes Blender Python, ComfyUI workflow JSON and FFmpeg commands | **Blender** (Cycles) plus **ComfyUI** video models; FFmpeg for the 4K encode |
| 2 | Smooth anime and character animation | Workflow design and prompts | **ComfyUI** with modern video models. *Skip standalone AnimateDiff (stale).* |
| 3 | Talking characters, lip sync, voice | Scripts and timing sheets | **LivePortrait** (replace the InsightFace models for commercial use) plus **OpenVoice V2** |
| 4 | Editing, grading, sound design | FFmpeg filter chains, LUT and EDL logic, Remotion edit code | FFmpeg locally or a desktop editor |
| 5 | Logo intros, brand films | **Your Remotion skills** + GSAP skills; HTML previews in artifacts | Remotion render (CLI or Lambda) |
| 6 | Premium HTML/CSS/JS | `frontend-design` + `ui-ux-pro-max` + `web-design-guidelines` | — |
| 7 | React, Next.js, responsive UI | `vercel-react-best-practices` + `vercel-composition-patterns` + `vercel-react-view-transitions` | — |
| 8 | Advanced Python and backend | Claude's built-in ability; no extra skill needed | — |
| 9 | 3D websites (Three.js) | 13 `threejs-*` skills; previews as HTML artifacts | — |
| 10 | GSAP, Remotion, HyperFrames | 8 `gsap-*` skills + your Remotion skills | HyperFrames rendering requires its CLI on a computer |

### Hardware guide for the GPU tools
- **Minimum useful:** NVIDIA RTX with 12 GB VRAM (3060 12 GB / 4070), 32 GB RAM, NVMe SSD.
- **Comfortable 4K and video models:** 24 GB VRAM (RTX 3090/4090/5090-class), 64 GB RAM.
- **No PC:** rent a cloud GPU by the hour (A100, L40S or 4090 class) for ComfyUI, LivePortrait and Blender. Android plus claude.ai can drive the design, scripting and code side from anywhere.

---

## 7. Installing on Android (claude.ai website)

1. On your phone, download `ALL-SKILLS-BUNDLE.zip` from this folder on GitHub (branch `claude/ai-creative-studio-audit-fvn72e`).
2. In the **Files** app, extract it. You'll get folders of individual skill `.zip` files. **Upload those inner ZIPs one at a time. Don't unzip them.**
3. In claude.ai, open **Settings → Capabilities** and make sure **Code execution** is on. For `web-artifacts-builder` and `web-design-guidelines`, allow network or package access if offered.
4. Open **Customize → Skills → Upload skill** and pick each ZIP, then switch it on.
5. Test it, for example: *"Use gsap-scrolltrigger to build a pinned hero section."*

If an upload fails, the most likely causes are a ZIP that was re-zipped (the folder must be the ZIP root) or a duplicate skill name.

---

## 8. Safety notes
- No repository scripts were run. The scripts inside packaged skills were reviewed by reading them: ui-ux-pro-max (local CSV search; its tests folder only runs local subprocesses), web-artifacts-builder (npm/shadcn scaffold and a bundler), and algorithmic-art (a p5 template).
- None of the 30 skills contain or require secrets.
- Watch-outs: `web-design-guidelines` fetches its rules remotely; the LivePortrait/InsightFace models are non-commercial; OpenMontage is AGPL; Remotion needs a company license once a company has more than 3 employees.
