# AnimeWwise-Dialogue mapping version-by_sshd

An enhanced version of AnimeWwise with built-in ASR (Automatic Speech Recognition), **full-language direct dialogue mapping** for **Honkai: Star Rail**, **Genshin Impact**, and **Zenless Zone Zero**, plus a portable Python environment.

**Version**: v2026.8.26
**Main Author**: [sshd-123](https://github.com/sshd-123)

![image](https://github.com/user-attachments/assets/ce2c8b19-82a2-42fc-a149-ed9ffbb7c54b)

---

## Table of Contents

- [Features](#features)
- [Supported Games](#supported-games)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Zenless Zone Zero (ZZZ) Support](#zenless-zone-zero-zzz-support)
- [ASR (Speech Recognition)](#asr-speech-recognition)
- [Voice Text Matching](#voice-text-matching)
- [Text to List Tool](#text-to-list-tool)
- [GPU Acceleration](#gpu-acceleration)
- [Portable Environment](#portable-environment)
- [Language Settings](#language-settings)
- [Bug Reporting](#bug-reporting)
- [Credits](#credits)

---

## Features

This integration package builds upon the original AnimeWwise with the following enhancements:

### Core Features
- ✅ Extract audio from anime games (`.pck`, `.hdiff`, `.wem`)
- ✅ Restore original filenames and paths using mapping files
- ✅ Support for multiple output formats (wem, wav, mp3, ogg)
- ✅ Batch extraction of selected files or entire packages
- ✅ Real-time extraction progress tracking
- ✅ One audio file → one `.txt` file with dialogue text

### Enhanced Features
- 🎤 **Built-in ASR**: FunASR (达摩ASR) and Faster Whisper for speech-to-text conversion
- 📝 **Voice Text Matching**: Accurate matching for Honkai: Star Rail, Genshin Impact, and Zenless Zone Zero
- 📥 **Voice Text Data Download**: Built-in tool to download and update voice text data for all games
- 🔄 **Auto-update**: Automatic background update checks for voice text data
- 📋 **Text to List**: Generate training set manifests with ASR-transcribed text
- 🚀 **GPU Acceleration**: NVIDIA CUDA 12.8 support, including RTX 50 series (Blackwell sm_120)
- 📦 **Portable Python**: No system Python installation required
- 🌐 **Bilingual Interface**: English and Chinese support
- ⚡ **Parallel Download**: Configurable download threads (1-8, default 4) for faster data updates

### ZZZ Exclusive Features
- 🎮 **Full ZZZ Dialogue Mapping**: Complete voice-text mapping for Zenless Zone Zero
- 📊 **GalGamePerform TSV Builder**: Built-in tool to build `galgame-perform-links.tsv` for story dialogue mapping
- 🌍 **Multi-language Support**: Chinese (CHS), English (EN), Japanese (JP), Korean (KR)
- 🔍 **TSV Version Detection**: Automatic version mismatch detection between map and TSV files
- 🛠️ **Built-in HoyoDown + Node.js**: No external tools required for TSV building

### Included Tools
- `ffmpeg` - Audio conversion
- `vgmstream` - Wwise audio parsing
- `hpatchz` - Update package extraction
- `hoyodown` - Game resource downloader (for ZZZ TSV building)
- `node` - Node.js runtime (for ZZZ TSV parsing)

---

## Supported Games

| Game | Mapping Version | Voice Text Matching | Notes |
|------|----------------|---------------------|-------|
| **Genshin Impact** | 7.0 | ✅ Full (direct mapping) | Full-language support, music names updated to version 5.3 |
| **Honkai: Star Rail** | 4.4 | ✅ Full (direct mapping) | Full-language support, enhanced voice text matching |
| **Zenless Zone Zero** | 3.1 | ✅ Full (direct + TSV) | Multi-language (CHS/EN/JP/KR) |
| **Arknights Endfield** | 1.3 | ❌ | VFS-based audio storage |

---

## Quick Start

1. **Download the package** and extract it to a directory of your choice
2. **Run `setup.bat`** to set up the portable Python environment
3. **Select PyTorch version**:
   - Option 1: CPU version (works on all PCs)
   - Option 2: CUDA 12.8 version (NVIDIA GPU acceleration)
4. **Wait for installation** to complete (includes dependencies and model downloads)
5. **Run `run.bat`** to start the application

---

## Usage

### Basic Workflow

1. **Select input folder** containing `.pck` files
   - Genshin: `GenshinImpact_Data\StreamingAssets\AudioAsset\...`
   - Star Rail: `StarRail_Data\Persistent\Audio\AudioPackage\Windows\...`
   - ZZZ: `ZenlessZoneZero_Data\StreamingAssets\Audio\Windows\Full\...`
   - Endfield: `Endfield_Data\StreamingAssets\VFS\...` (see note below)

2. **Select hdiff folder** (optional) - for update package extraction

3. **Select a mapping file** to restore original filenames

4. **Enable "Extract Dialogue"** checkbox to generate `.txt` files with dialogue text

5. **Browse and select files** to extract

6. **Choose output format** and output folder in the `Extract` menu

7. **Extract** and enjoy!

### Endfield Notes

Endfield uses VFS-based storage. The path mapping is:
- `InitAudio` ↔ `07A1BB91`
- `Audio` ↔ `24ED34CF`
- `AudioEnglish` ↔ `A31457D0`
- `AudioChinese` ↔ `E1E7D7CE`
- `AudioKorean` ↔ `E9D31017`
- `AudioJapanese` ↔ `F668D4EE`

Load only the `.chk` files from the appropriate folder.

---

## Zenless Zone Zero (ZZZ) Support

### Dialogue Mapping

ZZZ uses a two-layer dialogue mapping system:
1. **Direct Mapping**: Tips, Subtitles, Clue, Message config tables → TextMap
2. **GalGamePerform TSV**: Story dialogue voice keys → TextMap IDs (requires TSV file)

### Building TSV File

The `galgame-perform-links.tsv` file is required for story dialogue mapping. You can build it using:

**Method 1: Auto-build during data download**
1. Go to `Tools` → `Update Voice Data`
2. Select `Zenless Zone Zero`
3. Check "Also build GalGamePerform dialogue mapping"
4. Click "Start Update"

**Method 2: Build TSV only**
1. Go to `Tools` → `Update Voice Data`
2. Select `Zenless Zone Zero`
3. Click "Build TSV Only"
4. Wait for completion (2-5 minutes)

### TSV Version Management

- The main interface displays TSV version next to the map selector
- **Green**: TSV version matches map version
- **Red**: Version mismatch detected - click to rebuild
- **Orange**: TSV not generated - click to build

### Multi-language Support

ZZZ supports 4 languages for dialogue text:
- Chinese (CHS) - `TextMapTemplateTb.json`
- English (EN) - `TextMap_ENTemplateTb.json`
- Japanese (JP) - `TextMap_JATemplateTb.json`
- Korean (KR) - `TextMap_KOTemplateTb.json`

Switch language via `Tools` → `Language` → `Dialogue Language`.

---

## ASR (Speech Recognition)

The integrated ASR system supports two engines:

### FunASR (达摩ASR)
- **Language**: Chinese (Mandarin), Cantonese
- **Model**: Speech Paraformer Large + VAD + Punctuation
- **Precision**: float32
- **Best for**: Accurate Chinese transcription with punctuation

### Faster Whisper
- **Language**: Multilingual (Auto, Chinese, English, Japanese, Korean, Cantonese)
- **Model Sizes**: tiny, base, small, medium, large, large-v1, large-v2, large-v3
- **Precision**: float32, float16, int8
- **Best for**: Multi-language support and different accuracy/speed trade-offs

### GPU Compatibility

The ASR system automatically detects GPU compatibility. If your GPU's compute capability is not supported by the installed PyTorch version (e.g., RTX 5060 with sm_120), it will automatically fall back to CPU mode.

For full GPU acceleration on RTX 50 series (Blackwell), select **CUDA 12.8** during setup.

---

## Voice Text Matching

### Honkai: Star Rail
Enhanced voice text matching using data from `turnbasedgamedata`:
- **TalkSentenceConfig**: Chapter/story dialogue matching
- **VoiceAtlas**: Character profile voice lines
- **VoiceConfig**: Cutscene/story voice configuration
- **AvatarConfig**: Character name mapping
- **TextMapCHS**: Chinese text localization

Match rate: **>85% overall**, **>90% for archive-type paths**

### Genshin Impact
Full-language direct dialogue mapping with ASR fallback:
- Direct path matching for all voice files
- Full multi-language dialogue text support
- ASR-based transcription for unmatched files
- Variable placeholder handling

### Zenless Zone Zero
Two-layer mapping system (see [ZZZ Support](#zenless-zone-zero-zzz-support) for details):
- Direct mapping from config tables
- GalGamePerform TSV for story dialogue
- Multi-language support (CHS/EN/JP/KR)

---

## Text to List Tool

This tool generates training set manifests from audio files:

### Features
- Scan audio directories for voice files
- Auto-detect language of audio content
- Apply ASR to transcribe speech
- Support for variable placeholder replacement
- Review mode for manual correction
- Skip short audio or audio with variables

### Output Format
```
audio_path|character_name|language|text
```

### Usage
1. Go to `Tools` > `Text to List`
2. Select audio directory and output directory
3. Configure options (language, replace mode, etc.)
4. Click `Start generating`
5. Review and confirm each item (optional)

---

## GPU Acceleration

### Requirements
- NVIDIA GPU with CUDA support
- NVIDIA driver supporting CUDA 12.8
- At least 4GB VRAM (8GB+ recommended for large ASR models)

### Setup
During `setup.bat`, select **Option 2** for CUDA 12.8:
```
[1/6] Select PyTorch version:
  [1] CPU version (works on all PCs)
  [2] CUDA 12.8 version (NVIDIA GPU acceleration, sm_120 Blackwell support)
```

### Supported GPUs
- RTX 5090/5080/5070/5060 (Blackwell, sm_120) - requires CUDA 12.8
- RTX 4090/4080/4070/4060 (Ada Lovelace, sm_89)
- RTX 3090/3080/3070/3060 (Ampere, sm_86)
- And older NVIDIA GPUs with sm_50+

---

## Portable Environment

This package includes a portable Python environment:

### Benefits
- No system Python installation required
- All dependencies isolated in the package directory
- Works on Windows without admin rights
- Easy to copy and transfer

### Directory Structure
```
AnimeWwise-Dialogue mapping version-by_sshd/
├── python/              # Portable Python installation
├── tools/               # ffmpeg, vgmstream, hpatchz, hoyodown, node
│   ├── ffmpeg/
│   ├── vgmstream/
│   ├── hpatchz/
│   ├── hoyodown/        # Game resource downloader
│   ├── node/            # Node.js runtime
│   ├── zzz_galgame/     # ZZZ TSV builder scripts
│   └── asr/             # ASR models and configs
├── maps/                # Game mapping files
├── i18n/                # Translation files (en.json, zh.json)
├── zenlessdata/         # ZZZ voice text data (TextMap, FileCfg, TSV)
├── turnbasedgamedata-main/  # HSR voice text data
├── animegamedata2-main/ # Genshin voice text data
├── _runtime_tmp/        # Runtime temporary files
├── _hf_cache/           # HuggingFace model cache
├── app.py               # Main application
├── setup.bat            # Environment setup
├── run.bat              # Application launcher
└── version.json         # Version information
```

---

## Language Settings

The application supports English and Chinese interfaces:

- **Default**: English
- **Switch**: `View` > `Language` > Select your preferred language
- **Persistent**: Language preference is saved in `config.json`

### Dialogue Language
For ZZZ and HSR, you can also select the dialogue text language:
- `Tools` > `Language` > `Dialogue Language`
- Supported: Chinese (Simplified), English, Japanese, Korean

---

## Bug Reporting

If you encounter any issues, please report them on GitHub:


Please include:
- Steps to reproduce
- Error message (if any)
- Screenshots (if applicable)
- Game and version
- GPU model (for ASR/GPU issues)

---

## Credits

### Main Author
- [@sshd-123](https://github.com/sshd-123) - Creator and maintainer of the AnimeWwise-Dialogue mapping version

### Special Thanks
- [@simon300000](https://github.com/simon300000) - Mapping method and algorithm support ([zenless-voice](https://github.com/simon300000/zenless-voice))
- [@Dimbreath](https://github.com/Dimbreath) - Dataset support (AnimeGameData, TurnBasedGameData, ZZZData)
- [@Escartem](https://github.com/Escartem) - Original [AnimeWwise](https://github.com/Escartem/AnimeWwise) program

### Original AnimeWwise
- [@Escartem](https://github.com/Escartem) - Original creator
- [@Razmoth](https://github.com/Razmoth) - Keys parsing for Genshin and ZZZ
- [@Dimbreath](https://github.com/Dimbreath) - AnimeGameData, TurnBasedGameData, ZZZData
- [@Eleiyas](https://github.com/Eleiyas) - Keeping games updated
- [@Kei-Luna](https://github.com/Kei-Luna) - Genshin music name recovery
- [@davispuh](https://github.com/davispuh) - Star Rail keys bruteforce
- [@bnnm](https://github.com/bnnm) - Wwise audio exploration
- @hcs - Wwise audio extraction script
- [@vgmstream](https://github.com/vgmstream) - Wwise headers parsing

### Enhanced Features
- [FunASR](https://github.com/alibaba-damo-academy/FunASR) - Speech recognition engine
- [Faster Whisper](https://github.com/SYSTRAN/faster-whisper) - Whisper inference
- [turnbasedgamedata](https://github.com/Dimbreath/TurnBasedGameData) - Star Rail data
- [ZenlessData](https://git.mero.moe/dimbreath/ZenlessData) - ZZZ data
- [HoyoDown](https://github.com/Scighost/HoyoDown) - Game resource downloader
- [zenless-voice](https://github.com/simon300000/zenless-voice) - ZZZ voice mapping reference

---

---

# AnimeWwise-Dialogue mapping version-by_sshd

AnimeWwise 的增强版本，内置 ASR（自动语音识别）、**崩坏：星穹铁道**、**原神**和**绝区零**的**全语言台词直接映射**功能，以及便携 Python 环境。

**版本**: v2026.8.26
**主要作者**: [sshd-123](https://github.com/sshd-123)

![image](https://github.com/user-attachments/assets/ce2c8b19-82a2-42fc-a149-ed9ffbb7c54b)

---

## 目录

- [功能特性](#功能特性)
- [支持的游戏](#支持的游戏)
- [快速开始](#快速开始)
- [使用方法](#使用方法)
- [绝区零（ZZZ）支持](#绝区零zzz支持)
- [ASR 语音识别](#asr-语音识别)
- [语音台词匹配](#语音台词匹配)
- [文本转换工具](#文本转换工具)
- [GPU 加速](#gpu-加速)
- [便携环境](#便携环境)
- [语言设置](#语言设置)
- [问题反馈](#问题反馈)
- [致谢](#致谢)

---

## 功能特性

此整合包在原版 AnimeWwise 的基础上增加了以下增强功能：

### 核心功能
- ✅ 从动漫游戏提取音频（`.pck`, `.hdiff`, `.wem`）
- ✅ 使用映射文件恢复原始文件名和路径
- ✅ 支持多种输出格式（wem, wav, mp3, ogg）
- ✅ 批量提取选中文件或整个包
- ✅ 实时提取进度跟踪
- ✅ 一个音频文件 → 一个 `.txt` 台词文本文件

### 增强功能
- 🎤 **内置 ASR**: FunASR（达摩ASR）和 Faster Whisper 语音转文字
- 📝 **语音台词匹配**: 星穹铁道、原神、绝区零精准台词匹配
- 📥 **语音台词数据下载**: 内置工具下载和更新所有游戏的语音台词数据
- 🔄 **自动更新**: 后台自动检查语音台词数据更新
- 📋 **文本转换 list**: 生成带 ASR 转录文本的训练集清单
- 🚀 **GPU 加速**: NVIDIA CUDA 12.8 支持，包括 RTX 50 系列（Blackwell sm_120）
- 📦 **便携 Python**: 无需系统 Python 安装
- 🌐 **双语界面**: 英文和中文支持
- ⚡ **并行下载**: 可配置下载线程数（1-8，默认4），加快数据更新速度

### 绝区零专属功能
- 🎮 **完整 ZZZ 台词映射**: 绝区零完整的语音-文本映射
- 📊 **GalGamePerform TSV 构建器**: 内置工具构建 `galgame-perform-links.tsv` 用于剧情对话映射
- 🌍 **多语言支持**: 中文（CHS）、英文（EN）、日文（JP）、韩文（KR）
- 🔍 **TSV 版本检测**: 自动检测 map 和 TSV 文件版本不匹配
- 🛠️ **内置 HoyoDown + Node.js**: 构建 TSV 无需外部工具

### 内置工具
- `ffmpeg` - 音频转换
- `vgmstream` - Wwise 音频解析
- `hpatchz` - 更新包提取
- `hoyodown` - 游戏资源下载器（用于 ZZZ TSV 构建）
- `node` - Node.js 运行时（用于 ZZZ TSV 解析）

---

## 支持的游戏

| 游戏 | 映射版本 | 语音台词匹配 | 备注 |
|------|---------|-------------|------|
| **原神** | 7.0 | ✅ 完整（直接映射） | 全语言支持，音乐名称更新至 5.3 版本 |
| **崩坏：星穹铁道** | 4.4 | ✅ 完整（直接映射） | 全语言支持，增强语音台词匹配 |
| **绝区零** | 3.1 | ✅ 完整（直接 + TSV） | 多语言支持（CHS/EN/JP/KR） |
| **明日方舟：终末地** | 1.3 | ❌ | VFS 音频存储 |

---

## 快速开始

1. **下载整合包**并解压到任意目录
2. **运行 `setup.bat`** 安装便携 Python 环境
3. **选择 PyTorch 版本**:
   - 选项 1: CPU 版本（所有电脑均可使用）
   - 选项 2: CUDA 12.8 版本（NVIDIA GPU 加速）
4. **等待安装完成**（包括依赖和模型下载）
5. **运行 `run.bat`** 启动应用

---

## 使用方法

### 基本流程

1. **选择输入文件夹**（包含 `.pck` 文件）
   - 原神: `GenshinImpact_Data\StreamingAssets\AudioAsset\...`
   - 星穹铁道: `StarRail_Data\Persistent\Audio\AudioPackage\Windows\...`
   - 绝区零: `ZenlessZoneZero_Data\StreamingAssets\Audio\Windows\Full\...`
   - 终末地: `Endfield_Data\StreamingAssets\VFS\...`（见下方备注）

2. **选择 hdiff 文件夹**（可选）- 用于提取更新包

3. **选择映射文件**恢复原始文件名

4. **勾选"提取台词"**生成带台词文本的 `.txt` 文件

5. **浏览并选择要提取的文件**

6. **在 `提取` 菜单中选择输出格式和输出文件夹**

7. **点击提取**并享受！

### 终末地备注

终末地使用 VFS 存储，路径映射如下：
- `InitAudio` ↔ `07A1BB91`
- `Audio` ↔ `24ED34CF`
- `AudioEnglish` ↔ `A31457D0`
- `AudioChinese` ↔ `E1E7D7CE`
- `AudioKorean` ↔ `E9D31017`
- `AudioJapanese` ↔ `F668D4EE`

仅加载对应文件夹中的 `.chk` 文件。

---

## 绝区零（ZZZ）支持

### 台词映射

绝区零使用两层台词映射系统：
1. **直接映射**: Tips、Subtitles、Clue、Message 配置表 → TextMap
2. **GalGamePerform TSV**: 剧情对话语音键 → TextMap ID（需要 TSV 文件）

### 构建 TSV 文件

`galgame-perform-links.tsv` 文件是剧情对话映射所必需的。可以通过以下方式构建：

**方法 1：下载数据时自动构建**
1. 点击 `工具` → `更新台词数据`
2. 选择 `绝区零`
3. 勾选"同时构建 GalGamePerform 台词映射"
4. 点击"开始更新"

**方法 2：仅构建 TSV**
1. 点击 `工具` → `更新台词数据`
2. 选择 `绝区零`
3. 点击"仅构建 TSV 文件"
4. 等待完成（2-5 分钟）

### TSV 版本管理

- 主界面在 map 选择器旁边显示 TSV 版本
- **绿色**: TSV 版本与 map 版本一致
- **红色**: 检测到版本不匹配 - 点击重新构建
- **橙色**: TSV 未生成 - 点击构建

### 多语言支持

绝区零支持 4 种语言的台词文本：
- 中文（CHS）- `TextMapTemplateTb.json`
- 英文（EN）- `TextMap_ENTemplateTb.json`
- 日文（JP）- `TextMap_JATemplateTb.json`
- 韩文（KR）- `TextMap_KOTemplateTb.json`

通过 `工具` → `语言` → `台词语言` 切换语言。

---

## ASR 语音识别

集成的 ASR 系统支持两个引擎：

### FunASR（达摩ASR）
- **语言**: 中文（普通话）、粤语
- **模型**: Speech Paraformer Large + VAD + 标点恢复
- **精度**: float32
- **最佳场景**: 精准中文转录，带标点

### Faster Whisper
- **语言**: 多语种（自动、中文、英文、日文、韩文、粤语）
- **模型尺寸**: tiny, base, small, medium, large, large-v1, large-v2, large-v3
- **精度**: float32, float16, int8
- **最佳场景**: 多语言支持，不同精度/速度权衡

### GPU 兼容性

ASR 系统自动检测 GPU 兼容性。如果 GPU 算力不在已安装 PyTorch 支持列表中（例如 RTX 5060 的 sm_120），会自动降级为 CPU 模式。

要在 RTX 50 系列（Blackwell）上启用完整 GPU 加速，请在安装时选择 **CUDA 12.8**。

---

## 语音台词匹配

### 崩坏：星穹铁道
使用 `turnbasedgamedata` 数据实现增强的语音台词匹配：
- **TalkSentenceConfig**: 章节/剧情对话匹配
- **VoiceAtlas**: 角色档案语音
- **VoiceConfig**: 过场/剧情语音配置
- **AvatarConfig**: 角色名称映射
- **TextMapCHS**: 中文文本本地化

匹配率: **>85% 整体**, **>90% 存档路径**

### 原神
全语言台词直接映射，带 ASR 回退：
- 所有语音文件的直接路径匹配
- 完整多语言台词文本支持
- 未匹配文件的 ASR 转录
- 变量占位符处理

### 绝区零
两层映射系统（详见 [绝区零支持](#绝区零zzz支持)）：
- 配置表直接映射
- GalGamePerform TSV 剧情对话映射
- 多语言支持（CHS/EN/JP/KR）

---

## 文本转换工具

此工具从音频文件生成训练集清单：

### 功能特性
- 扫描音频目录查找语音文件
- 自动检测音频内容语言
- 应用 ASR 转录语音
- 支持变量占位符替换
- 审查模式支持手动修正
- 可跳过短音频或含变量的音频

### 输出格式
```
audio_path|character_name|language|text
```

### 使用方法
1. 点击 `工具` > `文本转换 list`
2. 选择音频目录和输出目录
3. 配置选项（语言、替换模式等）
4. 点击 `开始生成`
5. 逐条审查确认（可选）

---

## GPU 加速

### 要求
- 支持 CUDA 的 NVIDIA GPU
- 支持 CUDA 12.8 的 NVIDIA 驱动
- 至少 4GB VRAM（大型 ASR 模型建议 8GB+）

### 设置
在 `setup.bat` 中选择 **选项 2** 安装 CUDA 12.8：
```
[1/6] Select PyTorch version:
  [1] CPU version (works on all PCs)
  [2] CUDA 12.8 version (NVIDIA GPU acceleration, sm_120 Blackwell support)
```

### 支持的 GPU
- RTX 5090/5080/5070/5060（Blackwell, sm_120）- 需要 CUDA 12.8
- RTX 4090/4080/4070/4060（Ada Lovelace, sm_89）
- RTX 3090/3080/3070/3060（Ampere, sm_86）
- 其他支持 sm_50+ 的 NVIDIA GPU

---

## 便携环境

此包包含便携 Python 环境：

### 优点
- 无需系统 Python 安装
- 所有依赖隔离在包目录内
- 在 Windows 上无需管理员权限运行
- 易于复制和传输

### 目录结构
```
AnimeWwise-Dialogue mapping version-by_sshd/
├── python/              # 便携 Python 安装
├── tools/               # ffmpeg, vgmstream, hpatchz, hoyodown, node
│   ├── ffmpeg/
│   ├── vgmstream/
│   ├── hpatchz/
│   ├── hoyodown/        # 游戏资源下载器
│   ├── node/            # Node.js 运行时
│   ├── zzz_galgame/     # ZZZ TSV 构建脚本
│   └── asr/             # ASR 模型和配置
├── maps/                # 游戏映射文件
├── i18n/                # 翻译文件（en.json, zh.json）
├── zenlessdata/         # 绝区零语音台词数据（TextMap, FileCfg, TSV）
├── turnbasedgamedata-main/  # 星穹铁道语音台词数据
├── animegamedata2-main/ # 原神语音台词数据
├── _runtime_tmp/        # 运行时临时文件
├── _hf_cache/           # HuggingFace 模型缓存
├── app.py               # 主应用
├── setup.bat            # 环境安装
├── run.bat              # 应用启动器
└── version.json         # 版本信息
```

---

## 语言设置

应用支持英文和中文界面：

- **默认**: 英文
- **切换**: `视图` > `语言` > 选择偏好语言
- **持久化**: 语言偏好保存在 `config.json` 中

### 台词语言
对于绝区零和星穹铁道，还可以选择台词文本语言：
- `工具` > `语言` > `台词语言`
- 支持：简体中文、英文、日文、韩文

---

## 问题反馈

如遇到任何问题，请在 GitHub 上报告：


请提供：
- 复现步骤
- 错误信息（如有）
- 截图（如适用）
- 游戏名称和版本
- GPU 型号（如涉及 ASR/GPU 问题）

---

## 致谢

### 主要作者
- [@sshd-123](https://github.com/sshd-123) - AnimeWwise 台词映射版本的创建者与维护者

### 特别感谢
- [@simon300000](https://github.com/simon300000) - 映射方法与算法支持（[zenless-voice](https://github.com/simon300000/zenless-voice)）
- [@Dimbreath](https://github.com/Dimbreath) - 数据集支持（AnimeGameData, TurnBasedGameData, ZZZData）
- [@Escartem](https://github.com/Escartem) - 原始 [AnimeWwise](https://github.com/Escartem/AnimeWwise) 程序

### 原版 AnimeWwise
- [@Escartem](https://github.com/Escartem) - 原始开发者
- [@Razmoth](https://github.com/Razmoth) - 原神和绝区零的密钥解析
- [@Dimbreath](https://github.com/Dimbreath) - AnimeGameData, TurnBasedGameData, ZZZData
- [@Eleiyas](https://github.com/Eleiyas) - 保持游戏更新
- [@Kei-Luna](https://github.com/Kei-Luna) - 原神音乐名称恢复
- [@davispuh](https://github.com/davispuh) - 星穹铁道密钥暴力破解
- [@bnnm](https://github.com/bnnm) - Wwise 音频探索工具
- @hcs - Wwise 音频提取脚本
- [@vgmstream](https://github.com/vgmstream) - Wwise 头解析

### 增强功能
- [FunASR](https://github.com/alibaba-damo-academy/FunASR) - 语音识别引擎
- [Faster Whisper](https://github.com/SYSTRAN/faster-whisper) - Whisper 推理
- [turnbasedgamedata](https://github.com/Dimbreath/TurnBasedGameData) - 星穹铁道数据
- [ZenlessData](https://git.mero.moe/dimbreath/ZenlessData) - 绝区零数据
- [HoyoDown](https://github.com/Scighost/HoyoDown) - 游戏资源下载器
- [zenless-voice](https://github.com/simon300000/zenless-voice) - 绝区零语音映射参考
