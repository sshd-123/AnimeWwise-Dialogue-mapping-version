# AnimeWwise-Dialogue mapping · by sshd

Extract voice & dialogue audio from **Genshin Impact**, **Honkai: Star Rail**, **Zenless Zone Zero** and **Arknights: Endfield** — with original filenames restored, optional dialogue text (`.txt` next to each clip), and a fully portable Python environment.

![version](https://img.shields.io/badge/version-2026.10.4-blue)
![platform](https://img.shields.io/badge/platform-Windows%20x64-lightgrey)
![python](https://img.shields.io/badge/python-3.11%20bundled-informational)
![license](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-lightgrey)

**Author:** [@sshd-123](https://github.com/sshd-123) · **Based on** [AnimeWwise](https://github.com/Escartem/AnimeWwise) by [@Escartem](https://github.com/Escartem)

![screenshot](https://github.com/user-attachments/assets/ce2c8b19-82a2-42fc-a149-ed9ffbb7c54b)

---

## 🆕 Use a self-made map (recommended)

This fork has been **re-developed**, and it works best with maps produced by the companion **map maker** included in the same release.

A `.map` is what turns meaningless hash filenames into real paths. A plain map can only name the audio the game stores by hash. Our maps go further:

| | Plain `.map` | **Our map** |
|---|---|---|
| Hash-named voice/music | ✅ | ✅ |
| **Audio embedded inside the sound banks** (HSR battle voice, monster voice, cast lines) | ❌ lands in `unmapped\` | ✅ **named** |
| Coverage of what is actually installed | partial | **100 %** — anything the dataset cannot name gets an explicit `_unresolved\...` path instead of disappearing |
| Works for every language from one file | — | ✅ bank names are derived per *bank*, not per language |
| Category folders for filtering (Genshin: `Dialog` / `Fetter` / `AnimatorEvent` / `Card` / …) | ❌ | ✅ |
| Self-check before shipping | ❌ | ✅ the builder refuses to emit a map that misses dataset paths |

**Result on the current versions:** Genshin 841,704 entries (99.6 % of the installed voice files), Star Rail 1,072,707 entries **plus** 5,764 named bank files — of which **3,011 are character battle voice covering 116 characters** (`voicbank\Ev_vo_avatar_atk_cast_feixiao.wem`, `voicbank\Ev_vo_avatar_skill_cast01_castorice_…`, …).

A map is self-contained: **one `.map` file is all you copy.** The optional `<map>.banks.tsv` next to it is just a readable copy of the bank table.

### ⚠️ Maps do not update themselves

The program's *check for updates* only reads the **upstream** project's index and pulls
the **upstream** `.map` files from it. It knows nothing about the maps published here, so
a map you downloaded from this repository will **never** be replaced or refreshed by the
program.

When a new game version arrives:

1. Download the matching map from this repository (or rebuild it with the map maker),
2. drop it into `maps\`,
3. and delete the old one.

Note that the updater compares version numbers and will happily add an upstream map next
to ours (for example an upstream `hk4e.map` beside our `hk4e_7.1.map`) if the upstream
index looks newer. If you end up with two maps for one game, keep the one you want and
remove the other — the program offers both in the map list.

---

## What's new — 2026.10.4

### New

- **Star Rail: bank audio is named.** Battle voice, monster voice and cast lines live inside the
  sound banks rather than the hash namespace, so they used to land in `unmapped\`. They are now
  named — **5,764 bank files, 3,011 of them character battle voice covering 116 characters**
  (20,841 named banks in the table). The naming is **language independent**: a Chinese install names
  Japanese / English / Korean bank audio from the same map.
- **Readable bank filenames.** Single-file banks become `voicbank\<event>.wem`; multi-file banks get
  an ordered suffix (`<event>_01.wem`) instead of a raw media id.
- **Map / dialogue self-test** (`test_map_text_join.py`). Verifies that the map's display paths
  resolve to TSV dialogue text *without extracting any audio* — under a minute, options
  `--map --tsv --keyword --all --audit --lang`, runs from any directory.
- **Pre-flight confirmation and a post-extraction report.** Before starting, a dialog shows the map,
  the output folder and whether the bank sidecar loaded; when it finishes, a summary reports how many
  files were named, how many are placeholders and how many are unmapped.
- **Map list hardened.** Entries are sorted newest-version-first, each carries its own filename (two
  files sharing a label are shown with their filename), a missing-file fallback no longer switches
  versions behind your back, and your last choice is remembered.

### Fixed

- **Version number unified.** The title and the About box now share one constant; About used to show
  an internal data counter instead of the version.
- **Startup no longer blocks on the network.** The version check ran synchronously while the window
  was being built, with a 10–15 s timeout; it now runs after the UI is up.
- **The startup "update available" notice no longer points at the upstream program.** It compared our
  index with the upstream repository and told you to update the program, which would have replaced
  this fork — losing the bank naming and the maps published here. (A typo is fixed too.)
- **A missing map file no longer silently loads a different version.** The fallback picked by
  modification time; it now takes the highest version and says so loudly.
- **Version parsing fixed.** A digit inside the game code (`hk4e`) was read as the version, so
  `version.json` could be written as `4`, and several Genshin map versions sorted arbitrarily.
- **`version.json` sync is deterministic** — the highest version wins, not the order
  `os.listdir()` happens to return.
- **Dialogue mis-lookups avoided** — bank-namespace paths are skipped by the text lookup (2 of
  6,722 ids collided with voice ids and produced wrong lines).
- **The bank table can no longer be mistaken for a dialogue TSV** by the speaker-lookup tool.
- **UI:** translated labels no longer leak raw keys, the log no longer keeps the previous game's
  version line, and extraction refuses to run silently with no map selected.
- **Portability:** every bundled helper is resolved relative to the package and no other machine's
  paths remain in the code.

### Maps in this release

| Map | Version | Notes |
|---|---|---|
| `hk4e_7.1.map` | 7.1 | 841,704 entries, category folders |
| `hkrpg_4.6.map` | 4.6 | 1,072,707 entries, **bank table embedded** (262,903 B) |
| `hkrpg_4.6.banks.tsv` | — | optional readable copy of the bank table |
| `nap_3.2.0.map` | 3.2.0 | |
| `beyond.map` | 1.3 | |

The Star Rail table gained **1,843 events** the game builds at runtime from templates
(`Ev_vo_avatar_turn_begin_{0}` …), which brings the in-battle triggers — turn begin, advantage,
high threat, heal, buff, revive, ultra ready, light hit, standby — into the names. The Genshin map
uses the deletion list as an extra name source (**+572** entries that used to be placeholders).

---

## Supported games

| Game | Map version | Dialogue text | Notes |
|------|-------------|---------------|-------|
| **Genshin Impact** | **7.1** | ✅ direct mapping | all 4 languages, category folders |
| **Honkai: Star Rail** | **4.6** | ✅ direct mapping | all 4 languages, bank audio named |
| **Zenless Zone Zero** | **3.2.0** | ✅ direct + TSV | CHS / EN / JP / KR |
| **Arknights: Endfield** | 1.3 | ❌ | VFS-based storage |

---

## Quick start — build first, then run

The download is **small on purpose**. It contains the program and the bundled helper
tools (~200 MB), but **not** the Python runtime, the datasets, the ASR models or the
maps. Those are built or fetched on your own machine the first time you use it. Expect
the folder to grow to roughly 15–20 GB once everything is in place.

### Step 1 — build the environment (one time per computer)

Run **`setup.bat`** and choose a build:

| Build | Download | Notes |
|---|---|---|
| CPU | ~2 GB | works on any PC, slower ASR |
| CUDA 12.8 | ~3.2 GB | NVIDIA GPU acceleration |

It installs the embedded Python 3.11, PyTorch and the ASR components from Chinese
mirrors and writes a log to `_setup.log`. Nothing else has to be installed by hand —
FFmpeg, vgmstream, hpatchz, Node.js and HoyoDown already ship with the program.

### Step 2 — get a map

Put the maps you need into `maps\`. Download them from this repository, or build them
yourself with the **map maker** companion tool. Maps are **not** fetched automatically —
see *Maps* below.

### Step 3 — run

Double-click **`run.bat`**, pick your **game folder**, **map file** and **output
folder**, then extract.

**Requirements:** Windows x64, plus ~10 GB free while building and ~20 GB once finished.

---

## Basic usage

1. **Input folder** — the game's audio packages:

   | Game | Folder |
   |---|---|
   | Genshin Impact | `GenshinImpact_Data\StreamingAssets\AudioAssets` (CN client: `YuanShen_Data\...`) |
   | Honkai: Star Rail | `StarRail_Data\Persistent\Audio\AudioPackage\Windows` |
   | Zenless Zone Zero | `ZenlessZoneZero_Data\StreamingAssets\Audio\Windows\Full` |
   | Arknights: Endfield | `Endfield_Data\StreamingAssets\VFS` (load only the `.chk` files) |

2. **hdiff folder** *(optional)* — for extracting from an update package.
3. **Map file** — restores the original filenames. Use a self-made map (see above).
4. **Tick "Extract Dialogue"** to also write a `.txt` with the matching line next to each clip.
5. Choose the output format and folder, then extract.

**Endfield VFS shortcuts:** `InitAudio` ↔ `07A1BB91`, `Audio` ↔ `24ED34CF`, `AudioChinese` ↔ `E1E7D7CE`, `AudioEnglish` ↔ `A31457D0`, `AudioJapanese` ↔ `F668D4EE`, `AudioKorean` ↔ `E9D31017`.

---

## Features

- **Direct dialogue mapping** without ASR for all four languages of Genshin / Star Rail, and CHS-EN-JP-KR for ZZZ.
- **Dialogue text files** — every extracted clip can get a matching `.txt`.
- **Category filtering** (Genshin) — voice is grouped under `Dialog`, `Fetter`, `AnimatorEvent`, `Card`, `DungeonReminder`, … so you can extract just one kind.
- **HDIFF update support** — extract from incremental packages, with `new_files` / `changed_files` split out.
- **ASR fallback** — FunASR (达摩 ASR) or Faster Whisper, optional GPU acceleration.
- **Text → list tool** — turn a folder of clips into a speaker/line list.
- **Timbre / speaker search** — find "who says this line" by dialogue text.
- **Portable** — everything bundled, no installer, all settings kept inside the folder.
- **Bilingual UI** — Chinese / English.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Extracted files all land in `unmapped\` | No map selected, or the map does not match this game/version. Pick the right map. |
| Bank audio (Star Rail `VoBanks*.pck`) has no names | Use a self-made map — the naming table is embedded in it. |
| Nothing happens when extracting | The tool now asks for confirmation; if the map is on `No map` it warns first. |
| `setup.bat` fails | Check the log `_setup.log`; a proxy or missing disk space is the usual cause. |
| Is the package usable on another PC? | Run `portable_check.bat` — it verifies the runtime, the bundled tools and the folder permissions. |

---

## Credits

### Main Author
- [@sshd-123](https://github.com/sshd-123) — creator and maintainer of the AnimeWwise-Dialogue mapping version

### Special Thanks
- [@simon300000](https://github.com/simon300000) — mapping method and algorithm support ([zenless-voice](https://github.com/simon300000/zenless-voice))
- [@Dimbreath](https://github.com/Dimbreath) — dataset support (AnimeGameData, TurnBasedGameData, ZZZData)
- [@Escartem](https://github.com/Escartem) — the original [AnimeWwise](https://github.com/Escartem/AnimeWwise) program

### Original AnimeWwise
- [@Escartem](https://github.com/Escartem) — original creator
- [@Razmoth](https://github.com/Razmoth) — keys parsing for Genshin and ZZZ
- [@Dimbreath](https://github.com/Dimbreath) — AnimeGameData, TurnBasedGameData, ZZZData
- [@Eleiyas](https://github.com/Eleiyas) — keeping games updated
- [@Kei-Luna](https://github.com/Kei-Luna) — Genshin music name recovery
- [@davispuh](https://github.com/davispuh) — Star Rail keys bruteforce
- [@bnnm](https://github.com/bnnm) — Wwise audio exploration
- @hcs — Wwise audio extraction script
- [@vgmstream](https://github.com/vgmstream) — Wwise header parsing

### Enhanced Features
- [FunASR](https://github.com/alibaba-damo-academy/FunASR) — speech recognition engine
- [Faster Whisper](https://github.com/SYSTRAN/faster-whisper) — Whisper inference
- [turnbasedgamedata](https://github.com/Dimbreath/TurnBasedGameData) — Star Rail data
- [ZenlessData](https://git.mero.moe/dimbreath/ZenlessData) — ZZZ data
- [HoyoDown](https://github.com/Scighost/HoyoDown) — game resource downloader
- [zenless-voice](https://github.com/simon300000/zenless-voice) — ZZZ voice mapping reference

---

## Disclaimer

Please read this before using the program.

- **Not affiliated.** This is an unofficial community tool. It is not affiliated with,
  authorised by, endorsed by or connected to miHoYo / HoYoverse, Cognosphere or any of
  their subsidiaries — nor to the authors of the datasets and libraries it uses.
- **Personal, non-commercial use.** Licensed CC BY-NC-SA 4.0. Do not sell it, do not
  include it in a paid product, and do not use what you extract commercially.
- **No game files are distributed.** The program ships no game assets, no audio and no
  datasets. It only reads files already on your computer. Maps and datasets come from
  third parties (see Credits) or are built by you from data you obtained yourself.
- **Extracted audio still belongs to its owners.** Voice lines, music and sound effects
  are the property of miHoYo / HoYoverse and their licensors. Extracting them transfers
  no rights to you. Do not redistribute them and do not use them in any way that
  infringes those rights.
- **You are responsible for complying with the rules that apply to you.** Using this
  tool may conflict with the game's terms of service, and the legality of reverse
  engineering differs by country. Do not use it to cheat, to gain an unfair advantage,
  to bypass payments, or to pirate anything.
- **Provided as is, with no warranty of any kind.** No guarantee that it works, that it
  keeps working after a game update, or that the output is complete or correct. The
  authors accept no liability for damage, data loss, account action or legal
  consequences arising from its use. Extraction writes many files — point the output
  somewhere you can afford to lose and keep backups of anything important.
- **Third-party components keep their own licenses.** PyTorch, FunASR, Faster Whisper,
  FFmpeg, vgmstream, hpatchz, Node.js, HoyoDown and the datasets are separate projects
  with separate terms; using them through this program means accepting those terms too.
- **Game updates can break things at any time.** Formats, keys and datasets change
  without notice. A working setup today may stop working tomorrow, and no support or
  fix is promised.
- **If you are not sure your use is allowed, do not use it.**

## License

[CC BY-NC-SA 4.0](LICENCE.md) — the same license as the upstream project: free to share
and adapt for non-commercial use, with attribution and share-alike.

---

# 中文说明

从**原神**、**崩坏：星穹铁道**、**绝区零**、**明日方舟：终末地**中提取语音与台词音频：还原原始文件名、可选生成台词 `.txt`、内置便携 Python 环境，**无需安装任何东西**。

**版本 2026.10.4** · 作者 [@sshd-123](https://github.com/sshd-123) · 基于 [@Escartem](https://github.com/Escartem) 的 [AnimeWwise](https://github.com/Escartem/AnimeWwise)

## ⚠️ 请使用自制 map（强烈建议）

本提取器已**重新开发**，配合同发布的 **map 制作器**生成的 map 效果最好。

map 决定哈希文件名能否还原成真实路径。普通 map 只能命名"按哈希存放"的音频；我们的 map 还额外做到：

- **bank 内嵌音频也有名字**（崩铁的战斗语音、怪物语音、技能/大招语音）—— 普通 map 只能丢进 `unmapped\`
- **装机覆盖率 100%**：数据集给不出名字的，也落在明确的 `_unresolved\...` 路径下，不会消失
- **一个 map 覆盖所有语言**（命名按 bank 推导，与语言无关）
- **分类目录**（原神：`Dialog` / `Fetter` / `AnimatorEvent` / `Card` 等，便于筛选）
- **发布前自检**：漏读数据集路径时构建器会拒绝产出

当前版本实测：原神 **841,704** 条（覆盖装机的 99.6%），崩铁 **1,072,707** 条，另有 **5,764** 个 bank 文件被命名，其中 **3,011 个是角色战斗语音、覆盖 116 个角色**。

map 是自包含的：**只需要复制一个 `.map` 文件**；旁边的 `.banks.tsv` 只是给人看的副本。

### ⚠️ map 不会自己更新

程序里的「检查更新」**只会去上游项目**拉取索引和它的 `.map` 文件，完全不知道本仓库发布的 map。
因此：**从本仓库下载的 map 永远不会被程序替换或刷新。**

游戏更新后请手动操作：

1. 从本仓库下载对应版本的 map（或用 map 制作器重建）
2. 放入 `maps\`
3. 删掉旧的

另外，更新器只比对版本号，**可能会在我们的 map 旁边额外加一份上游 map**
（例如在 `hk4e_7.1.map` 旁边出现 `hk4e.map`）。若同一游戏出现两份 map，
保留你要的那份、删掉另一份即可（地图下拉列表会同时列出）。

## 更新内容（2026.10.4）

### 新增

- **崩铁 bank 音频可命名**：战斗语音、怪物语音、技能/大招语音原本在 bank 内而落在 `unmapped\`，
  现在有名字 —— **5,764 个 bank 文件，其中 3,011 个是角色战斗语音、覆盖 116 个角色**
  （命名表 20,841 条）。命名**与语言无关**：中文安装也能命名日语/英语/韩语的 bank 音频。
- **bank 文件名可读**：单文件 bank 为 `voicbank\<事件名>.wem`；多文件带有序序号
  （`<事件名>_01.wem`），不再是裸 mediaId。
- **地图 / 台词匹配自检**（`test_map_text_join.py`）：**不提取任何音频**即可验证 map 的显示路径
  能否解析到 TSV 台词，一分钟内完成；支持 `--map --tsv --keyword --all --audit --lang`，可放任意目录运行。
- **提取前确认 + 提取后对账**：开始前弹窗显示所用的地图、输出目录、bank 命名表是否加载；
  结束后汇总报告命名数、占位符数、未映射数。
- **地图列表加固**：按版本号从新到旧排序；每项各自记住自己的文件名（同名时显示文件名以区分）；
  文件缺失时的兜底不再偷偷换版本；并记住你上次的选择。

### 修复

- **版本号统一**：标题栏与「关于」共用一个常量（以前「关于」显示的是内部数据计数器）。
- **启动不再被网络阻塞**：版本检查原本在窗口构建期间同步执行、超时 10–15 秒，现改为界面显示后再执行。
- **启动的「有新版本」提示不再指向上游程序**：原先拿本项目的索引与上游仓库比对并提示更新程序，
  照着做会替换成本仓库以外的版本 —— 从而**丢失 bank 命名与本仓库发布的 map**（顺带修掉一处拼写错误）。
- **地图文件缺失时不再静默换用别的版本**：兜底原先按修改时间挑，现改为取版本最高者并醒目告警。
- **版本号解析修复**：游戏代号里的数字（`hk4e` 的 `4`）曾被当作版本号，导致 `version.json`
  可能被写成 `4`，多个原神地图版本之间也会乱序。
- **`version.json` 同步确定化**：取版本最高者，不再受 `os.listdir()` 顺序影响。
- **避免台词错配**：bank 命名空间下的路径不再进入台词查找（6,722 个 id 中有 2 个与语音 id 撞号，会取到错误台词）。
- **bank 命名表不会再被当成台词 TSV** 喂给「通过台词查找说话人」。
- **界面**：语言标签不再泄漏未翻译的键名；运行日志不再残留上一个游戏的版本行；未选地图时不再静默无动作。
- **可移植**：所有内置组件相对定位，代码里已无他人机器路径。

### 本版随包地图

| 地图 | 版本 | 说明 |
|---|---|---|
| `hk4e_7.1.map` | 7.1 | 841,704 条，带分类目录 |
| `hkrpg_4.6.map` | 4.6 | 1,072,707 条，**内嵌 bank 命名表**（262,903 B）|
| `hkrpg_4.6.banks.tsv` | — | 命名表的可选可读副本 |
| `nap_3.2.0.map` | 3.2.0 | |
| `beyond.map` | 1.3 | |

崩铁命名表补回了游戏运行时用模板拼出的 **1,843 个事件名**（`Ev_vo_avatar_turn_begin_{0}` …），
使回合开始、优势、高威胁、治疗、增益、复活、大招就绪、轻击、待机等战斗触发进入命名；
原神地图新增删除清单作为名字来源（**+572 条**，此前会退化为占位符）。

## 支持的游戏

| 游戏 | map 版本 | 台词匹配 |
|---|---|---|
| **原神** | **7.1** | ✅ 直接映射（4 语言，带分类目录）|
| **崩坏：星穹铁道** | **4.6** | ✅ 直接映射（4 语言，bank 音频可命名）|
| **绝区零** | **3.2.0** | ✅ 直接映射 + TSV（中英日韩）|
| **明日方舟：终末地** | 1.3 | ❌（VFS 存储）|

## 快速开始 —— 先构建，再运行

**下载包是有意做小的**：里面只有程序本体与内置工具（约 200 MB），
**不包含** Python 运行时、数据集、ASR 模型和 map。这些东西会在你自己的电脑上
第一次使用时构建或下载，全部就位后目录会长到约 **15–20 GB**。

### 第 1 步 —— 构建环境（每台电脑一次）

运行 **`setup.bat`** 并选择版本：

| 版本 | 下载量 | 说明 |
|---|---|---|
| CPU | 约 2 GB | 任何电脑可用，ASR 较慢 |
| CUDA 12.8 | 约 3.2 GB | 需 NVIDIA 显卡，加速 ASR |

它会从国内镜像安装内嵌 Python 3.11、PyTorch 与 ASR 组件，日志写在 `_setup.log`。
FFmpeg、vgmstream、hpatchz、Node.js、HoyoDown 已随程序自带，无需手动安装。

### 第 2 步 —— 获取 map

把需要的 map 放进 `maps\`：从本仓库下载，或用配套的 **map 制作器** 自制。
map **不会自动下载**，详见下方「map 不会自己更新」一节。

### 第 3 步 —— 运行

双击 **`run.bat`**，依次选择**游戏目录**、**map 文件**、**输出目录**，然后提取。

**环境要求**：Windows x64；构建时需约 10 GB 空间，完成后约 20 GB。

## 基本用法

| 游戏 | 输入目录 |
|---|---|
| 原神 | `GenshinImpact_Data\StreamingAssets\AudioAssets`（国服为 `YuanShen_Data\...`）|
| 崩坏：星穹铁道 | `StarRail_Data\Persistent\Audio\AudioPackage\Windows` |
| 绝区零 | `ZenlessZoneZero_Data\StreamingAssets\Audio\Windows\Full` |
| 终末地 | `Endfield_Data\StreamingAssets\VFS`（只加载对应目录下的 `.chk`）|

勾选「提取台词」可为每个音频同时生成同名 `.txt` 台词文件。

**终末地 VFS 对照**：`InitAudio` ↔ `07A1BB91`、`Audio` ↔ `24ED34CF`、`AudioChinese` ↔ `E1E7D7CE`、`AudioEnglish` ↔ `A31457D0`、`AudioJapanese` ↔ `F668D4EE`、`AudioKorean` ↔ `E9D31017`。

## 常见问题

| 现象 | 处理 |
|---|---|
| 提取出来的文件全在 `unmapped\` | 没选 map，或 map 与该游戏/版本不匹配 |
| 崩铁 bank 音频没名字 | 使用自制 map（命名表内嵌在 map 里）|
| 点提取没反应 | 现在会先弹确认；若地图停在 `No map` 会先警告 |
| 换电脑能不能用 | 双击 `portable_check.bat` 自检（运行时、内置工具、目录权限）|

## 致谢

### 主要作者
- [@sshd-123](https://github.com/sshd-123) —— AnimeWwise-Dialogue mapping 版本的创建者与维护者

### 特别感谢
- [@simon300000](https://github.com/simon300000) —— 映射方法与算法支持（[zenless-voice](https://github.com/simon300000/zenless-voice)）
- [@Dimbreath](https://github.com/Dimbreath) —— 数据集支持（AnimeGameData、TurnBasedGameData、ZZZData）
- [@Escartem](https://github.com/Escartem) —— 原版 [AnimeWwise](https://github.com/Escartem/AnimeWwise) 程序

### 原版 AnimeWwise
- [@Escartem](https://github.com/Escartem) —— 原作者
- [@Razmoth](https://github.com/Razmoth) —— 原神与绝区零密钥解析
- [@Dimbreath](https://github.com/Dimbreath) —— AnimeGameData、TurnBasedGameData、ZZZData
- [@Eleiyas](https://github.com/Eleiyas) —— 持续跟进游戏更新
- [@Kei-Luna](https://github.com/Kei-Luna) —— 原神音乐名恢复
- [@davispuh](https://github.com/davispuh) —— 星穹铁道密钥爆破
- [@bnnm](https://github.com/bnnm) —— Wwise 音频探索
- @hcs —— Wwise 音频提取脚本
- [@vgmstream](https://github.com/vgmstream) —— Wwise 头解析

### 增强功能所用项目
- [FunASR](https://github.com/alibaba-damo-academy/FunASR) —— 语音识别引擎
- [Faster Whisper](https://github.com/SYSTRAN/faster-whisper) —— Whisper 推理
- [turnbasedgamedata](https://github.com/Dimbreath/TurnBasedGameData) —— 星穹铁道数据
- [ZenlessData](https://git.mero.moe/dimbreath/ZenlessData) —— 绝区零数据
- [HoyoDown](https://github.com/Scighost/HoyoDown) —— 游戏资源下载器
- [zenless-voice](https://github.com/simon300000/zenless-voice) —— 绝区零语音映射参考

## 免责声明

使用前请先阅读：

- **非官方。** 本工具由社区开发，与 miHoYo / 米哈游、Cognosphere 及其关联公司
  **无任何关系**，也与它所使用的数据集、开源库作者无关。
- **仅限个人非商用。** 采用 CC BY-NC-SA 4.0：不得售卖、不得纳入付费产品，
  也不得将提取出来的内容用于商业用途。
- **不分发任何游戏文件。** 程序内不包含游戏资源、音频或数据集，
  只读取你电脑上已有的文件。map 与数据集来自第三方（见致谢）或由你自行构建。
- **提取出的音频版权仍属于原权利人。** 语音、音乐与音效归 miHoYo / 米哈游
  及其许可方所有。提取行为**不会转移任何权利**，不要再分发，也不要以侵权方式使用。
- **合规责任在你。** 使用本工具可能与游戏用户协议冲突，逆向工程的合法性各地不同。
  不得用于作弊、获取不公平优势、绕过付费或侵权。
- **按「现状」提供，无任何担保。** 不保证可用、不保证游戏更新后仍可用、
  也不保证提取结果完整正确。因使用本工具导致的损失、数据丢失、账号处罚
  或法律后果，作者不承担责任。提取会写入大量文件，请指向你可以承受丢失的目录并做好备份。
- **第三方组件有各自的许可。** PyTorch、FunASR、Faster Whisper、FFmpeg、vgmstream、
  hpatchz、Node.js、HoyoDown 与各数据集均为独立项目，通过本程序使用即表示你同意其条款。
- **游戏更新随时可能导致失效。** 格式、密钥与数据集均可能无预告变更，今天能用不代表明天能用，
  也不承诺提供修复或支持。
- **如果你不确定自己的用途是否被允许，请不要使用。**

## 许可

[CC BY-NC-SA 4.0](LICENCE.md)，与原项目相同：
允许非商用传播与改变，需署名并以相同方式共享。游戏资源与数据集归各自所有者（miHoYo / HoYoverse、Dimbreath 等）——
本工具只是读取你已经拥有的文件。
