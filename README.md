# AnimeWwise-Dialogue-mapping-version



An enhanced version of AnimeWwise with built-in ASR (Automatic Speech Recognition), voice text matching for Honkai: Star Rail and Genshin Impact, and a portable Python environment.



---

## Table of Contents

- [Features](#features)
- [Supported Games](#supported-games)
- [Download](#download)
- [Quick Start](#quick-start)
- [Usage](#usage)
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

### Enhanced Features
- 🎤 **Built-in ASR**: FunASR and Faster Whisper for speech-to-text conversion
- 📝 **Voice Text Matching**: Multi-language matching for Honkai: Star Rail, and fuzzy matching for Genshin Impact (Chinese only, ~90% accuracy)
- 📥 **Voice Text Data Download**: Built-in tool to download and update voice text data
- 📋 **Text to List**: Generate training set manifests with ASR-transcribed text
- 🚀 **GPU Acceleration**: NVIDIA CUDA 12.8 support, including RTX 50 series (Blackwell sm_120)
- 📦 **Portable Python**: No system Python installation required
- 🌐 **Bilingual Interface**: English and Chinese support
- 🔧 **Fixed**: Resolved the issue where updated Wwise `.map` files would not load properly

### Included Tools
- `ffmpeg` - Audio conversion
- `vgmstream` - Wwise audio parsing
- `hpatchz` - Update package extraction

---

## Supported Games

| Game | Mapping Support | Notes |
|------|----------------|-------|
| **Genshin Impact** | Aligned with map files in the AnimeWwise repository | Fuzzy Chinese voice text matching (~90% accuracy); music names synced with latest map data |
| **Honkai: Star Rail** | Aligned with map files in the AnimeWwise repository | Multi-language voice text matching (Chinese, English, Japanese, Korean) |
| **Zenless Zone Zero** | Aligned with map files in the AnimeWwise repository | Audio storage changed, may be incomplete |
| **Arknights Endfield** | Aligned with map files in the AnimeWwise repository | VFS-based audio storage |

---

## Download

You can choose between the latest version and legacy versions according to your needs:
- **Latest version (2026.7.17)**: `AnimeWwise-Dialogue mapping version-by_sshd_2026.7.17` — full package with all new features
- **Legacy versions**: Still fully functional for basic audio extraction
- **Update tool (Chinese UI only)**: If you have already set up an older version and do not want to rebuild the environment, download `AnimeWwise-Updater.exe`, select your existing legacy package directory, and install the update files directly.

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

4. **Browse and select files** to extract

5. **Choose output format** and output folder in the `Extract` menu

6. **Extract** and enjoy!

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

## ASR (Speech Recognition)

The integrated ASR system supports two engines:

### FunASR
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

### Honkai: Star Rail — Multi-language Matching
This package includes enhanced voice text matching using data from `turnbasedgamedata`, now supporting 4 languages:
- **Supported languages**: Chinese, English, Japanese, Korean
- **Matching data sources**:
  - `TalkSentenceConfig`: Chapter/story dialogue matching
  - `VoiceAtlas`: Character profile voice lines
  - `VoiceConfig`: Cutscene/story voice configuration
  - `AvatarConfig`: Character name mapping
  - Corresponding multi-language TextMap files

The matching system maintains a high overall match rate, with >90% match rate for archive-type paths.

### Genshin Impact — Fuzzy Matching (Chinese Only)
- **Supported language**: Simplified Chinese
- **Matching accuracy**: ~90% for standard story and character voice lines
- **Matching mode**: Fuzzy matching based on audio path features and text corpus alignment
- **Note**: Some event-exclusive or special cutscene voice lines may have a slightly lower match rate

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
AnimeWwise-lite/
├── python/              # Portable Python installation
├── tools/               # ffmpeg, vgmstream, hpatchz, ASR
├── maps/                # Game mapping files
├── i18n/                # Translation files
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

---

## Bug Reporting

If you encounter any issues, please report them on GitHub:

[Report a Bug](https://github.com/sshd-123/AnimeWwise-Dialogue-mapping-version_Star-Rail/issues/new)

Please include:
- Steps to reproduce
- Error message (if any)
- Screenshots (if applicable)
- Game and version
- GPU model (for ASR/GPU issues)

---

## Credits

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

---

---

# AnimeWwise-Dialogue-mapping-version



AnimeWwise 的增强版本，内置 ASR（自动语音识别）、崩坏：星穹铁道与原神语音台词匹配功能，以及便携 Python 环境。

> ⚠️ **重要提示**：
> - 语音台词匹配功能：崩坏：星穹铁道支持中、英、日、韩四语言匹配；原神支持中文台词模糊匹配（准确度约90%）。
> - 其他 AnimeWwise 基础功能（绝区零、明日方舟：终末地的音频提取）仍然正常工作。



---

## 目录

- [功能特性](#功能特性)
- [支持的游戏](#支持的游戏)
- [下载说明](#下载说明)
- [快速开始](#快速开始)
- [使用方法](#使用方法)
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

### 增强功能
- 🎤 **内置 ASR**: FunASR 和 Faster Whisper 语音转文字
- 📝 **语音台词匹配**: 崩坏：星穹铁道多语言台词匹配，原神中文台词模糊匹配（准确度约90%）
- 📥 **语音台词数据下载**: 内置工具下载和更新语音台词数据
- 📋 **文本转换 list**: 生成带 ASR 转录文本的训练集清单
- 🚀 **GPU 加速**: NVIDIA CUDA 12.8 支持，包括 RTX 50 系列（Blackwell sm_120）
- 📦 **便携 Python**: 无需系统 Python 安装
- 🌐 **双语界面**: 英文和中文支持
- 🔧 **问题修复**: 修复了 Wwise `.map` 文件更新后无法正常加载的问题

### 内置工具
- `ffmpeg` - 音频转换
- `vgmstream` - Wwise 音频解析
- `hpatchz` - 更新包提取

---

## 支持的游戏

| 游戏 | 映射支持 | 备注 |
|------|---------|------|
| **原神** | 与 AnimeWwise 仓库 map 文件同步更新 | 新增中文台词模糊匹配（准确度约90%）；音乐名称随最新 map 文件同步 |
| **崩坏：星穹铁道** | 与 AnimeWwise 仓库 map 文件同步更新 | 支持中、英、日、韩四语言语音台词匹配 |
| **绝区零** | 与 AnimeWwise 仓库 map 文件同步更新 | 音频存储方式变更，可能不完整 |
| **明日方舟：终末地** | 与 AnimeWwise 仓库 map 文件同步更新 | VFS 音频存储 |

---

## 下载说明

你可以根据需求选择不同版本：
- **最新版本（2026.7.17）**：`AnimeWwise-Dialogue mapping version-by_sshd_2026.7.17` 完整整合包，包含全部新功能
- **旧版本**：基础音频提取功能仍可正常使用
- **更新工具（仅中文界面）**：如果你已搭建过旧版本环境且不想重新构建，可下载 `AnimeWwise-Updater.exe`，选择旧版本整合包目录即可安装更新文件。

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

4. **浏览并选择要提取的文件**

5. **在 `提取` 菜单中选择输出格式和输出文件夹**

6. **点击提取**并享受！

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

## ASR 语音识别

集成的 ASR 系统支持两个引擎：

### FunASR
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

### 崩坏：星穹铁道 — 多语言匹配
本整合包基于 `turnbasedgamedata` 数据实现增强台词匹配，现已支持 4 种语言：
- **支持语言**：中文、英文、日文、韩文
- **匹配数据源**：
  - `TalkSentenceConfig`：章节/剧情对话匹配
  - `VoiceAtlas`：角色档案语音
  - `VoiceConfig`：过场/剧情语音配置
  - `AvatarConfig`：角色名称映射
  - 对应多语言 TextMap 文本库

匹配系统整体保持高匹配率，其中档案类路径匹配率 >90%。

### 原神 — 模糊匹配（仅中文）
- **支持语言**：简体中文
- **匹配准确度**：常规剧情与角色语音匹配率约 90%
- **匹配模式**：基于音频路径特征与文本语料对齐的模糊匹配
- **说明**：部分活动限定、特殊过场语音的匹配率可能略低

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
AnimeWwise-lite/
├── python/              # 便携 Python 安装
├── tools/               # ffmpeg, vgmstream, hpatchz, ASR
├── maps/                # 游戏映射文件
├── i18n/                # 翻译文件
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

---

## 问题反馈

如遇到任何问题，请在 GitHub 上报告：

[报告问题](https://github.com/sshd-123/AnimeWwise-Dialogue-mapping-version_Star-Rail/issues/new)

请提供：
- 复现步骤
- 错误信息（如有）
- 截图（如适用）
- 游戏名称和版本
- GPU 型号（如涉及 ASR/GPU 问题）

---

## 致谢

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
