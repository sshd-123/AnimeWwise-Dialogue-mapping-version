import os
import io
import json
import wwise
import voicetext
import voiceid_mapper
import tempfile
import wavescan
import platform
import subprocess
from vfs import decrypt
from mapper import Mapper
from allocator import Allocator
from filereader import FileReader

try:
	import fuzzy_matcher
	_FUZZY_MATCHER_AVAILABLE = True
except ImportError:
	_FUZZY_MATCHER_AVAILABLE = False

try:
	import asr_helper
	_ASR_HELPER_AVAILABLE = True
except ImportError:
	_ASR_HELPER_AVAILABLE = False

cwd = os.getcwd()
path = lambda *args: os.path.join(*args)

def call(args):
	try:
		subprocess.call(args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
	except Exception as e:
		print(f"[WARNING] failed to extract, {e}")


_worker_index_cache = None
_worker_matcher_cache = None
_worker_game_type = None

def _init_worker(game_type, fallback_second_char):
	"""
	进程池初始化函数：每个子进程启动时调用一次，预加载台词索引。
	"""
	global _worker_index_cache, _worker_matcher_cache, _worker_game_type
	import os
	import sys
	
	current_dir = os.path.dirname(os.path.abspath(__file__))
	if current_dir not in sys.path:
		sys.path.insert(0, current_dir)
	
	import fuzzy_matcher
	import voicetext
	
	_worker_game_type = game_type
	
	prebuilt = voicetext.load_fuzzy_index(game_type=game_type)
	if prebuilt is not None:
		original_list, clean_list, py_tone_list, py_notone_list = prebuilt
		text_index = fuzzy_matcher.TextLibraryIndex.from_prebuilt(
			original_list, clean_list, py_tone_list, py_notone_list
		)
	else:
		all_texts = voicetext.get_all_texts(game_type=game_type)
		if not all_texts:
			_worker_index_cache = None
			_worker_matcher_cache = None
			return
		text_index = fuzzy_matcher.TextLibraryIndex(all_texts)
	
	_worker_index_cache = text_index
	_worker_matcher_cache = fuzzy_matcher.SequentialFuzzyMatcher(
		text_index, window_size=20000, full_search_threshold=0.95,
		fallback_second_char=fallback_second_char
	)
	print(f"[fuzzy] 子进程 {os.getpid()} 索引加载完成")

def _process_single_worker_fast(args):
	"""
	多进程 worker 函数：处理单个文件。
	使用进程初始化时预加载的索引。
	"""
	global _worker_index_cache, _worker_matcher_cache
	
	import os
	
	audio_path, asr_text = args
	seq_matcher = _worker_matcher_cache
	txt_path = os.path.splitext(audio_path)[0] + ".txt"
	
	try:
		if not asr_text or not asr_text.strip():
			best_text = "……"
			best_ratio = 0.0
			status = "empty"
		elif seq_matcher is None:
			best_text = "……"
			best_ratio = 0.0
			status = "error"
		else:
			result = seq_matcher.match_next(asr_text)
			best_text = result.text
			best_ratio = result.ratio
			if best_ratio >= 0.5:
				status = "matched"
			elif best_ratio > 0:
				status = "low_ratio"
			else:
				status = "failed"
		
		try:
			with open(txt_path, "w", encoding="utf-8") as tf:
				tf.write(best_text)
		except Exception:
			pass
		
		return (audio_path, best_text, best_ratio, status)
		
	except Exception as e:
		print(f"[fuzzy] 模糊匹配失败 {os.path.basename(audio_path)}: {e}")
		try:
			with open(txt_path, "w", encoding="utf-8") as tf:
				tf.write("……")
		except Exception:
			pass
		return (audio_path, "……", 0.0, "error")


class WwiseExtract:
	def __init__(self):
		self.allocator = Allocator()
		self.hdiff_dir = None
		self.maps = {}
		self._fuzzy_text_index = None
		self._asr_model_loaded = False
		self._fuzzy_stats = {"total": 0, "matched": 0, "low_ratio": 0, "asr_failed": 0}

	### loading files ###

	def load_map(self, _map):
		map_name = _map.split(".")[0]
		map_path = path(cwd, f"maps/{_map}")

		# If exact file not found, try to find actual file with version suffix
		# e.g. hkrpg.map -> hkrpg_4.5.map
		if not os.path.isfile(map_path):
			maps_dir = path(cwd, "maps")
			if os.path.isdir(maps_dir):
				import glob
				# Find files like hkrpg_*.map
				candidates = glob.glob(path(maps_dir, f"{map_name}_*.map"))
				if candidates:
					# Pick the most recently modified
					candidates.sort(key=os.path.getmtime, reverse=True)
					map_path = candidates[0]
					print(f"Map file {_map} not found, using actual file: {os.path.basename(map_path)}")

		try:
			file_mtime = os.path.getmtime(map_path)
		except OSError:
			file_mtime = 0

		cached = self.maps.get(map_name)
		if cached is not None:
			cached_mtime = getattr(cached, '_file_mtime', 0)
			if cached_mtime == file_mtime and file_mtime > 0:
				print("Mapping already loaded, skipping (unchanged)")
				return cached
			else:
				print("Map file changed, reloading...")

		print("Map load required !")
		mapper = Mapper(map_path)
		mapper._file_mtime = file_mtime
		self.maps[map_name] = mapper

		return mapper

	def load_folder(self, _map, files, diff_path, base_path, progress):
		self.progress = progress
		self.steps = 1

		self.mapper = None
		if _map is not None:
			self.mapper = self.load_map(_map)
		
		self.file_structure = {"folders": {}, "files": []}

		hdiff_files = []
		if diff_path != "":
			hdiff_files = [f for f in os.listdir(diff_path) if f.endswith(".pck.hdiff")]
			
			# TODO: hdiff mode will only use .hdiff files and ignore .pck even in the update folder, i need to implement it, eventually

			# remove alone pck / hdiff
			base_files = [os.path.basename(f) for f in files]
			hdiff_files = [f for f in hdiff_files if os.path.basename(f.replace(".hdiff", "")) in base_files]
			base_hfiles = [os.path.basename(f) for f in hdiff_files]
			files = [f for f in files if f"{os.path.basename(f)}.hdiff" in base_hfiles]

		if len(files) == 0:
			return None

		pos = 0
		print(f"\nLoading {len(files)} files...")
		for file in files:
			pos += 1
			self.update_progress(pos, len(files), 1)

			hdiff = None
			if f"{os.path.basename(file)}.hdiff" in hdiff_files:
				hdiff = path(diff_path, hdiff_files[hdiff_files.index(f"{os.path.basename(file)}.hdiff")])
			self.load_file(file, hdiff, base_path)

		# VoicePath → VoiceID mapping is now loaded from the data repository
		# (VoiceConfig.json + TalkSentenceConfig.json). The mapper above is
		# used only to provide the mapped_path from hkrpg.map to the text lookup.

		return self.file_structure

	def load_file(self, _input, hdiff, base_path):
		with open(_input, "rb") as f:
			data = f.read()
			f.close()

		self.get_wems(data, os.path.basename(_input), hdiff, os.path.relpath(_input, start=base_path))

	def get_wems(self, data, filename, hdiff, relpath):
		files = wavescan.get_data(data, filename)
		
		if hdiff is not None:
			with open(hdiff, "rb") as f:
				hdiff_data = f.read()
				f.close()
			
			hdiff_files, data = self.get_hdiff_files(data, hdiff_data, filename)
			files = self.compare_diff(files, hdiff_files)

		self.map_names(files, filename, relpath, hdiff is not None, data)

	def compare_diff(self, old, new):
		old_dict = {file[0]:file[2] for file in old}
		new_files = [file for file in new if file[0] not in list(old_dict.keys())]
		changed_files = [file for file in new if file[0] in list(old_dict.keys()) and file[2] != old_dict[file[0]]]

		return [new_files, changed_files]

	def get_hdiff_files(self, data, hdiff_data, source_name):
		working_dir = tempfile.TemporaryDirectory()
		if self.hdiff_dir is None:
			self.hdiff_dir = tempfile.TemporaryDirectory()

		with open(path(working_dir.name, "source.pck"), "wb") as f:
			f.write(data)
			f.close()

		with open(path(working_dir.name, "patch.pck.hdiff"), "wb") as f:
			f.write(hdiff_data)
			f.close()

		args = [
			path(cwd, "tools/hpatchz/hpatchz.exe"),
			"-f",
			path(working_dir.name, "source.pck"),
			path(working_dir.name, "patch.pck.hdiff"),
			path(working_dir.name, "patch.pck")
		]

		if platform.system() != "Windows":
			args.insert(0, "wine")

		call(args)

		if not os.path.exists(path(working_dir.name, "patch.pck")):
			print(f"[ERROR] failed to patch {source_name}, skipping")
			return []

		with open(path(working_dir.name, "patch.pck"), "rb") as f:
			data = f.read()
			f.close()

		with open(path(self.hdiff_dir.name, source_name), "wb") as f:
			f.write(data)
			f.close()

		files = wavescan.get_data(data, source_name)

		working_dir.cleanup()

		return files, data
	
	def map_names(self, files, filename, relpath, hdiff=False, data=None, skip_source=True):
		# disable skip source if required
		mapper = self.mapper
		base = self.file_structure

		if hdiff:
			old_files = files
			filename = f"{filename} (hdiff)"
			files = [*files[0], *files[1]]

		# in case of manual use of mapping, use this
		# load json here

		# handle = open("banks.json", "r")
		# banks = json.loads(handle.read())
		# handle.close()

		def process_file(file):
			if mapper is not None:
				key = mapper.get_key(file[0].split(".")[0])

				# and override the method with a manual dict lookup
				
				# _id = file[0].split(".")[0]
				# if _id in list(banks["banks"].keys()):
				# 	key = [banks["banks"][_id], ""]
			else:
				key = None

			file_data = {
				"source": relpath,
				"size": file[2],
				"offset": file[1],
				"original_name": file[0],
				"metadata": {},
				"mapped_path": None  # filled below if mapper found a path
			}

			wem_data = data[file_data["offset"]:file_data["offset"]+file_data["size"]]
			parsed_wem = wwise.parse_wwise(wem_data, f"{file[3]}:{file[0]}:{file[1]}", file[0])

			if not parsed_wem:
				return

			file_data["metadata"] = parsed_wem

			if key is not None:
				file_data["mapped_path"] = key[0]  # store hkrpg.map path

				if hdiff:
					if file in old_files[0]:
						key[0] = f"new_files\\{key[0]}"
					else:
						key[0] = f"changed_files\\{key[0]}"

				parts = f"{filename}\\{key[0]}.wem".split("\\")
				if skip_source:
					parts = parts[1:]

				self.add_to_structure(parts, file_data)
			else:
				temp = base["folders"]

				if not skip_source:
					if filename not in temp:
						temp[filename] = {"folders": {}, "files": []}
					temp = temp[filename]["folders"]
				
				if hdiff:
					if file in old_files[0]:
						if "new_files" not in temp:
							temp["new_files"] = {"folders": {}, "files": []}
						temp = temp["new_files"]["folders"]

					if file in old_files[1]:
						if "changed_files" not in temp:
							temp["changed_files"] = {"folders": {}, "files": []}
						temp = temp["changed_files"]["folders"]

				if "unmapped" not in temp:
					temp["unmapped"] = {"folders": {}, "files": []}
				temp["unmapped"]["files"].append([file[0], file_data])
		
		pos = 0
		for file in files:
			process_file(file)
			pos += 1
			self.update_progress(pos, len(files), 1)

		self.file_structure = base

	def add_to_structure(self, parts, meta):
		current_level = self.file_structure
		for part in parts[:-1]:
			if "folders" not in current_level:
				current_level["folders"] = {}
			if part not in current_level["folders"]:
				current_level["folders"][part] = {"folders": {}, "files": []}
			current_level = current_level["folders"][part]
		if "files" not in current_level:
			current_level["files"] = []
		current_level["files"].append([parts[-1], meta])

	### fuzzy matching ###

	def _build_fuzzy_index(self):
		"""
		构建模糊匹配的台词库索引。

		优先从本地缓存文件快速加载4个列表；缓存不存在则从仓库生成并保存缓存。
		索引只构建一次（缓存）。
		"""
		if self._fuzzy_text_index is not None:
			return self._fuzzy_text_index

		if not _FUZZY_MATCHER_AVAILABLE:
			print("[fuzzy] fuzzy_matcher 模块不可用，跳过模糊匹配")
			return None

		try:
			game_type = getattr(self, 'game_type', None)
			
			# 优先尝试从缓存文件加载
			try:
				prebuilt = voicetext.load_fuzzy_index(game_type=game_type)
				if prebuilt is not None:
					original_list, clean_list, py_tone_list, py_notone_list = prebuilt
					index = fuzzy_matcher.TextLibraryIndex.from_prebuilt(
						original_list, clean_list, py_tone_list, py_notone_list
					)
					self._fuzzy_text_index = index
					print(f"[fuzzy] 从缓存加载台词索引完成，共 {len(index)} 条")
					return index
			except Exception as cache_err:
				print(f"[fuzzy] 从缓存加载失败({cache_err})，改为从仓库构建...")
			
			# 回退：从仓库原始数据构建
			all_texts = voicetext.get_all_texts(game_type=game_type)
			if not all_texts:
				print("[fuzzy] 警告: 台词库为空，模糊匹配可能无法正常工作")
				return None

			print(f"[fuzzy] 正在构建台词索引，共 {len(all_texts)} 条台词...")
			if hasattr(self, 'progress') and self.progress:
				self.progress(["total", 0, f"正在构建台词索引（{len(all_texts)}条）...", None])
			index = fuzzy_matcher.TextLibraryIndex(all_texts)
			self._fuzzy_text_index = index
			print(f"[fuzzy] 台词索引构建完成，共 {len(index)} 条")
			
			# 后台尝试保存缓存（不阻塞主流程）
			try:
				import threading
				def _save_cache_bg():
					try:
						voicetext.build_and_save_cache(game_type=game_type)
					except Exception as e:
						print(f"[fuzzy] 后台保存缓存失败: {e}")
				t = threading.Thread(target=_save_cache_bg, daemon=True)
				t.start()
			except Exception:
				pass
			
			return index
		except Exception as e:
			print(f"[fuzzy] 构建索引失败: {e}")
			import traceback
			traceback.print_exc()
			return None

	def _run_fuzzy_match_for_folder(self, audio_folder):
		"""
		对指定目录下的所有音频文件运行 ASR 识别和模糊匹配（旧版本，保留兼容）。

		递归查找所有音频文件（.wav, .wem, .mp3, .ogg），
		对每个文件进行 ASR 识别和模糊匹配，并将结果写入同名 .txt 文件。

		Args:
			audio_folder: 音频文件所在目录
		"""
		if not _FUZZY_MATCHER_AVAILABLE or not _ASR_HELPER_AVAILABLE:
			print("[fuzzy] 模糊匹配或 ASR 模块不可用，跳过")
			return

		text_index = self._build_fuzzy_index()
		if text_index is None:
			print("[fuzzy] 台词索引未构建，跳过模糊匹配")
			return

		audio_exts = {'.wav', '.wem', '.mp3', '.ogg'}
		audio_files = []

		for root, dirs, files in os.walk(audio_folder):
			for f in files:
				ext = os.path.splitext(f)[1].lower()
				if ext in audio_exts:
					full_path = os.path.join(root, f)
					rel_path = os.path.relpath(full_path, audio_folder)
					audio_files.append(full_path)

		if not audio_files:
			print("[fuzzy] 未找到音频文件")
			return

		self._run_fuzzy_match_optimized(audio_files, self.steps - 1, self.steps, fallback_second_char=getattr(self, 'fuzzy_fallback_second_char', False))

	def _run_fuzzy_match_optimized(self, audio_files, asr_step, match_step, num_threads=24, mode="fuzzy", fallback_second_char=False):
		"""
		台词处理：分步骤处理音频文件。

		支持三种模式：
		- mode="asr": 仅ASR识别，结果直接作为台词写入txt
		- mode="fuzzy": ASR识别 + 全文模糊匹配
		- mode="none": 不做任何台词映射

		步骤：
		1. 对所有音频进行 ASR 识别，结果保存为同名 .txt 文件（已存在且非空则跳过）
		2. 如果是模糊匹配模式，读取ASR结果进行多线程全文模糊匹配

		Args:
			audio_files: 音频文件路径列表
			asr_step: ASR识别对应的进度步
			match_step: 模糊匹配对应的进度步
			num_threads: 模糊匹配使用的线程数，默认24
			mode: 处理模式，"asr" / "fuzzy" / "none"
		"""
		# [已禁用] 模糊匹配/ASR 台词映射已移除，直接跳过所有模糊匹配执行路径
		print("[fuzzy] 模糊匹配功能已禁用，跳过")
		return

		if not _ASR_HELPER_AVAILABLE:
			print("[fuzzy] ASR 模块不可用，跳过")
			return
		
		if mode == "none":
			print("[fuzzy] 已选择取消台词映射，跳过")
			return

		# 过滤掉不存在的文件
		audio_files = [f for f in audio_files if os.path.isfile(f)]
		if not audio_files:
			print("[fuzzy] 没有有效的音频文件")
			return

		# 按文件名排序（方便处理和查找）
		audio_files.sort()
		total = len(audio_files)
		self._fuzzy_stats = {"total": total, "matched": 0, "low_ratio": 0, "asr_failed": 0}

		# ===== 第一步：ASR识别所有音频，保存为txt文件 =====
		mode_name = "直接保存ASR" if mode == "asr" else "模糊匹配"
		print(f"[fuzzy] 开始{mode_name}处理，共 {total} 个音频文件")
		print(f"[fuzzy] 步骤1/2: 正在进行ASR语音识别...")
		asr_skip_count = 0

		for idx, audio_path in enumerate(audio_files, 1):
			filename = os.path.basename(audio_path)
			txt_path = os.path.splitext(audio_path)[0] + ".txt"
			status_msg = f"ASR识别中 [{idx}/{total}] {filename}"
			self.update_progress(idx, total, asr_step, status=status_msg, stats=self._fuzzy_stats.copy())

			# 如果txt文件已存在且非空，跳过ASR
			if os.path.isfile(txt_path):
				try:
					with open(txt_path, "r", encoding="utf-8") as tf:
						existing_text = tf.read().strip()
					if existing_text and existing_text != "……":
						asr_skip_count += 1
						continue
				except Exception:
					pass

			try:
				ext = os.path.splitext(audio_path)[1].lower()
				wav_path = None
				tmp_dir = None

				if ext == '.wav':
					wav_path = audio_path
				else:
					tmp_dir = tempfile.mkdtemp(prefix="fuzzy_asr_")
					tmp_wav = os.path.join(tmp_dir, f"tmp_{idx}.wav")
					vgmstream_path = path(cwd, "tools/vgmstream/vgmstream-cli.exe")
					ffmpeg_path = path(cwd, "tools/ffmpeg/ffmpeg.exe")

					if ext == '.wem' and os.path.isfile(vgmstream_path):
						args = [vgmstream_path, "-o", tmp_wav, audio_path]
						if platform.system() != "Windows":
							args.insert(0, "wine")
						subprocess.call(args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
						if os.path.isfile(tmp_wav):
							wav_path = tmp_wav
					elif os.path.isfile(ffmpeg_path):
						args = [ffmpeg_path, "-i", audio_path, "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", tmp_wav]
						if platform.system() != "Windows":
							args.insert(0, "wine")
						subprocess.call(args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
						if os.path.isfile(tmp_wav):
							wav_path = tmp_wav

				if wav_path and os.path.isfile(wav_path):
					asr_text = asr_helper.recognize_file(wav_path, language="zh")
					asr_text = asr_text if asr_text and asr_text.strip() else ""
					if mode == "asr":
						# 直接保存ASR结果作为台词
						save_text = asr_text if asr_text else "……"
						try:
							with open(txt_path, "w", encoding="utf-8") as tf:
								tf.write(save_text)
						except Exception:
							pass
						if asr_text:
							self._fuzzy_stats["matched"] += 1
						else:
							self._fuzzy_stats["asr_failed"] += 1
					else:
						# 模糊匹配模式：先保存ASR原始结果，后面再匹配
						try:
							with open(txt_path, "w", encoding="utf-8") as tf:
								tf.write(asr_text if asr_text else "")
						except Exception:
							pass
				else:
					self._fuzzy_stats["asr_failed"] += 1
					if mode == "asr":
						try:
							with open(txt_path, "w", encoding="utf-8") as tf:
								tf.write("……")
						except Exception:
							pass

				# 清理临时文件
				if tmp_dir and os.path.exists(tmp_dir):
					try:
						import shutil
						shutil.rmtree(tmp_dir, ignore_errors=True)
					except Exception:
						pass

			except Exception as e:
				print(f"[fuzzy] ASR识别失败 {filename}: {e}")
				self._fuzzy_stats["asr_failed"] += 1
				if mode == "asr":
					try:
						with open(txt_path, "w", encoding="utf-8") as tf:
							tf.write("……")
					except Exception:
						pass

		# 如果是直接ASR模式，到这里就结束了
		if mode == "asr":
			print(f"[fuzzy] ASR识别完成，成功 {total - self._fuzzy_stats['asr_failed']}/{total}（跳过已存在 {asr_skip_count} 个）")
			return

		# ===== 第二步：模糊匹配模式，读取所有txt文件进行匹配 =====
		if not _FUZZY_MATCHER_AVAILABLE:
			print("[fuzzy] fuzzy_matcher 模块不可用，跳过模糊匹配")
			return

		text_index = self._build_fuzzy_index()
		if text_index is None:
			print("[fuzzy] 台词索引未构建，跳过模糊匹配，保留ASR结果")
			return

		# 重新统计ASR成功数
		asr_success = 0
		for audio_path in audio_files:
			txt_path = os.path.splitext(audio_path)[0] + ".txt"
			if os.path.isfile(txt_path):
				try:
					with open(txt_path, "r", encoding="utf-8") as tf:
						t = tf.read().strip()
					if t and t != "……":
						asr_success += 1
				except Exception:
					pass
		self._fuzzy_stats["asr_failed"] = total - asr_success
		self._fuzzy_stats["matched"] = 0
		self._fuzzy_stats["low_ratio"] = 0
		print(f"[fuzzy] ASR识别完成，成功 {asr_success}/{total}（跳过已存在 {asr_skip_count} 个）")

		print(f"[fuzzy] 步骤2/2: 正在进行模糊台词匹配（多进程全文搜索）...")
		from concurrent.futures import ProcessPoolExecutor, as_completed
		import multiprocessing

		# 读取所有ASR结果
		asr_results = {}
		for audio_path in audio_files:
			txt_path = os.path.splitext(audio_path)[0] + ".txt"
			if os.path.isfile(txt_path):
				try:
					with open(txt_path, "r", encoding="utf-8") as tf:
						asr_text = tf.read().strip()
					asr_results[audio_path] = asr_text if asr_text and asr_text != "……" else ""
				except Exception:
					asr_results[audio_path] = ""
			else:
				asr_results[audio_path] = ""

		# 确定进程数（根据内存和CPU核心数动态调整）
		cpu_count = multiprocessing.cpu_count()
		
		# 估算每个进程的内存占用（实测约 500MB~800MB/进程）
		# 之前估算1.5GB过高，实际缓存加载后内存占用约 600MB/进程
		mem_per_process_gb = 0.8
		available_mem_gb = None
		
		# 尝试获取系统内存信息（跨平台）
		try:
			import platform
			total_mem_gb = None
			available_mem_gb = None
			if platform.system() == "Windows":
				import ctypes
				class MEMORYSTATUSEX(ctypes.Structure):
					_fields_ = [
						("dwLength", ctypes.c_ulong),
						("dwMemoryLoad", ctypes.c_ulong),
						("ullTotalPhys", ctypes.c_ulonglong),
						("ullAvailPhys", ctypes.c_ulonglong),
						("ullTotalPageFile", ctypes.c_ulonglong),
						("ullAvailPageFile", ctypes.c_ulonglong),
						("ullTotalVirtual", ctypes.c_ulonglong),
						("ullAvailVirtual", ctypes.c_ulonglong),
						("ullAvailExtendedVirtual", ctypes.c_ulonglong),
					]
				ms = MEMORYSTATUSEX()
				ms.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
				ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
				total_mem_gb = ms.ullTotalPhys / (1024**3)
				available_mem_gb = ms.ullAvailPhys / (1024**3)
			else:
				# Linux/macOS: 尝试用 psutil，失败则读 /proc/meminfo 或 sysctl
				try:
					import psutil
					mem = psutil.virtual_memory()
					total_mem_gb = mem.total / (1024**3)
					available_mem_gb = mem.available / (1024**3)
				except ImportError:
					if platform.system() == "Linux":
						with open("/proc/meminfo", "r") as f:
							for line in f:
								if line.startswith("MemTotal:"):
									total_mem_gb = int(line.split()[1]) / (1024**2)
								elif line.startswith("MemAvailable:"):
									available_mem_gb = int(line.split()[1]) / (1024**2)
					elif platform.system() == "Darwin":
						import subprocess
						result = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True)
						if result.returncode == 0:
							total_mem_gb = int(result.stdout.strip()) / (1024**3)
						# macOS 没有直接的 available memory，用 vm_stat 计算
						result = subprocess.run(["vm_stat"], capture_output=True, text=True)
						if result.returncode == 0:
							page_size = 4096
							free_pages = 0
							for line in result.stdout.split("\n"):
								if "Pages free" in line:
									free_pages = int(line.split(":")[1].strip().rstrip("."))
								elif "Pages inactive" in line:
									free_pages += int(line.split(":")[1].strip().rstrip("."))
							available_mem_gb = (free_pages * page_size) / (1024**3)

			if available_mem_gb is not None:
				max_by_mem = int((available_mem_gb * 0.65) / mem_per_process_gb)
				max_by_mem = max(1, max_by_mem)
				if total_mem_gb is not None:
					print(f"[fuzzy] 系统内存: {total_mem_gb:.1f}GB, 可用: {available_mem_gb:.1f}GB, 内存建议进程数: {max_by_mem}")
				else:
					print(f"[fuzzy] 可用内存: {available_mem_gb:.1f}GB, 内存建议进程数: {max_by_mem}")
			else:
				raise RuntimeError("Unable to get memory info")
		except Exception:
			# 如果获取不到内存信息，就按 CPU 核心数的 2/3 来
			max_by_mem = max(1, int(cpu_count * 0.75))
			print(f"[fuzzy] 无法获取内存信息，按 CPU 核心数的 3/4 设置进程数: {max_by_mem}")
		
		if num_threads is not None and num_threads > 0:
			num_workers = min(num_threads, total, cpu_count, max_by_mem)
		else:
			num_workers = min(cpu_count, total, max_by_mem)
		
		# 最少 1 个进程
		num_workers = max(1, num_workers)
		
		print(f"[fuzzy] 分为 {num_workers} 个进程并行处理，共 {total} 个文件")

		# 报告开始匹配
		self.update_progress(0, total, match_step, status=f"正在启动{num_workers}个进程并加载索引...", stats=self._fuzzy_stats.copy())

		# 准备任务列表（简化参数，game_type和fallback通过initializer传递）
		game_type = getattr(self, 'game_type', None)
		tasks = []
		for audio_path in audio_files:
			asr_text = asr_results.get(audio_path, "")
			tasks.append((audio_path, asr_text))

		# 使用进程池并行处理，用 submit + as_completed 实时获取结果
		from concurrent.futures import as_completed
		total_matched = 0
		total_low_ratio = 0
		done_count = 0
		
		with ProcessPoolExecutor(
			max_workers=num_workers,
			initializer=_init_worker,
			initargs=(game_type, fallback_second_char)
		) as executor:
			# 提交所有任务
			futures = [executor.submit(_process_single_worker_fast, task) for task in tasks]
			
			# 逐个处理完成的任务
			for future in as_completed(futures):
				try:
					result = future.result()
				except Exception as e:
					print(f"[fuzzy] 子进程任务异常: {e}")
					continue
				
				audio_path, best_text, best_ratio, status = result
				done_count += 1
				
				if status == "matched":
					total_matched += 1
				elif status == "low_ratio":
					total_low_ratio += 1
				
				# 每处理完一个文件就更新进度
				stats = {
					"total": total,
					"matched": total_matched,
					"low_ratio": total_low_ratio,
					"asr_failed": self._fuzzy_stats["asr_failed"]
				}
				status_msg = f"模糊匹配中 [{done_count}/{total}]"
				self.update_progress(done_count, total, match_step, status=status_msg, stats=stats)

		# 更新最终统计
		self._fuzzy_stats = {
			"total": total,
			"matched": total_matched,
			"low_ratio": total_low_ratio,
			"asr_failed": self._fuzzy_stats["asr_failed"]
		}

		print(f"[fuzzy] 模糊匹配完成: 总计 {self._fuzzy_stats['total']}, "
		      f"匹配成功(>=50%) {self._fuzzy_stats['matched']}, "
		      f"低匹配度 {self._fuzzy_stats['low_ratio']}, "
		      f"ASR失败 {self._fuzzy_stats['asr_failed']}")

	### extracting files ###

	def extract_files(self, _input, files, output, _format, progress, enable_voicetext=False, flat_folders=False, game_type=None, fuzzy_match=False, fuzzy_threads=24, fuzzy_mode="fuzzy", fuzzy_fallback_second_char=False, tsv_mapper=None, tsv_language=None):
		self.enable_voicetext = enable_voicetext
		self.flat_folders = flat_folders
		self.game_type = game_type
		self.fuzzy_match = fuzzy_match
		self.fuzzy_threads = fuzzy_threads
		self.fuzzy_mode = fuzzy_mode
		self.fuzzy_fallback_second_char = fuzzy_fallback_second_char
		self.tsv_mapper = tsv_mapper
		self.tsv_language = tsv_language
		
		# 扁平化文件夹模式: 仅保留主分类目录 (chapter4, archive, side4, vo 等)
		# 将 ["voice", "chapter4", "72", "cyrene"] 转换为 ["chapter4"]
		if flat_folders:
			for file in files:
				mapped_path = file.get("mapped_path")
				path_parts = file.get("path", [])
				new_path = []
				
				# 优先使用 mapped_path 推导主分类
				if mapped_path:
					parts = mapped_path.replace("\\", "/").split("/")
					if len(parts) >= 2:
						new_path = [parts[1]]
					elif len(parts) >= 1:
						new_path = [parts[0]]
				
				# 回退方案: 从 file["path"] 推导
				if not new_path:
					if len(path_parts) >= 2:
						new_path = [path_parts[1]]
					elif len(path_parts) >= 1:
						new_path = [path_parts[0]]
				
				file["path"] = new_path
		
		temp_dir = tempfile.TemporaryDirectory()
		self.progress = progress
		
		# 台词处理：
		# - mode="none": 不处理，0步
		# - mode="asr": 仅ASR，1步
		# - mode="fuzzy": ASR + 模糊匹配，2步
		do_asr = fuzzy_match and enable_voicetext and _ASR_HELPER_AVAILABLE and (fuzzy_mode in ("asr", "fuzzy"))
		do_fuzzy = do_asr and _FUZZY_MATCHER_AVAILABLE and fuzzy_mode == "fuzzy"
		
		base_steps = {
			"wem": 1,
			"wav": 2,
			"mp3": 3,
			"ogg": 3
		}[_format]
		# 台词处理步骤数
		extra_steps = 0
		if do_asr:
			extra_steps += 1
		if do_fuzzy:
			extra_steps += 1
		self.steps = base_steps + extra_steps

		# 构建输出文件路径列表（用于模糊匹配）
		output_files = []
		for file in files:
			file_path = path("/".join(file["path"]), file["name"])
			base_name = os.path.splitext(file["name"])[0]
			# 使用完整路径构建输出文件路径
			rel_dir = os.path.dirname(file_path)
			if _format == "wem":
				out_path = path(output, rel_dir, base_name + ".wem")
			elif _format == "wav":
				out_path = path(output, rel_dir, base_name + ".wav")
			else:
				out_path = path(output, rel_dir, base_name + "." + _format)
			output_files.append(out_path)

		# wem
		if _format == "wem":
			output_folder = output
		else:
			output_folder = path(temp_dir.name, "wem")

		self.extract_wem(_input, files, output_folder)

		if _format == "wem":
			if do_asr:
				mode_str = "ASR直接保存" if not do_fuzzy else "模糊匹配"
				print(f": Running {mode_str} on wem files")
				asr_step = base_steps + 1
				match_step = base_steps + 2 if do_fuzzy else base_steps + 1
				self._run_fuzzy_match_optimized(output_files, asr_step, match_step, num_threads=self.fuzzy_threads, mode=self.fuzzy_mode, fallback_second_char=self.fuzzy_fallback_second_char)
				self._print_fuzzy_stats()
			temp_dir.cleanup()
			return

		# wav
		new_input = output_folder
		files_paths = [path("/".join(file["path"]), file["name"]) for file in files]

		if _format == "wav":
			output_folder = output
		else:
			output_folder = path(temp_dir.name, "wav")

		self.extract_wav(new_input, files_paths, output_folder)

		if _format == "wav":
			if do_asr:
				mode_str = "ASR直接保存" if not do_fuzzy else "模糊匹配"
				print(f": Running {mode_str} on wav files")
				asr_step = base_steps + 1
				match_step = base_steps + 2 if do_fuzzy else base_steps + 1
				self._run_fuzzy_match_optimized(output_files, asr_step, match_step, num_threads=self.fuzzy_threads, mode=self.fuzzy_mode, fallback_second_char=self.fuzzy_fallback_second_char)
				self._print_fuzzy_stats()
			self._write_voicetext_to_output(files, output, _format)
			temp_dir.cleanup()
			return

		# mp3 & ogg
		files_paths = [path(os.path.dirname(file), f'{os.path.basename(file).split(".")[0]}.wav') for file in files_paths]
		new_input = output_folder
		output_folder = output

		self.extract_ffmpeg(new_input, files_paths, output_folder, _format)

		if do_asr:
			mode_str = "ASR直接保存" if not do_fuzzy else "模糊匹配"
			print(f": Running {mode_str} on {_format} files")
			asr_step = base_steps + 1
			match_step = base_steps + 2 if do_fuzzy else base_steps + 1
			self._run_fuzzy_match_optimized(output_files, asr_step, match_step, num_threads=self.fuzzy_threads, mode=self.fuzzy_mode, fallback_second_char=self.fuzzy_fallback_second_char)
			self._print_fuzzy_stats()

		self._write_voicetext_to_output(files, output, _format)
		temp_dir.cleanup()
		return

	def _get_dialogue_text(self, file):
		"""
		Get dialogue text for a file,优先使用 TSV 映射器，回退到 voicetext。

		Args:
			file: File metadata dict with 'original_name', 'name', 'mapped_path'

		Returns:
			str or None: Dialogue text (may include speaker prefix), or None
		"""
		tsv_mapper = getattr(self, 'tsv_mapper', None)
		tsv_language = getattr(self, 'tsv_language', None)

		# 1. Try TSV mapper first (direct hash-based mapping)
		if tsv_mapper is not None and getattr(tsv_mapper, 'loaded', False):
			# Try original_name (hash or numeric ID) and display name
			candidates = []
			for key_field in ('original_name', 'name'):
				val = file.get(key_field, '')
				if val:
					candidates.append(os.path.splitext(val)[0])

			for hash_key in candidates:
				if not hash_key:
					continue
				info = tsv_mapper.get_info(hash_key, tsv_language)
				if info:
					text = info.get('transcription', '')
					if text:
						# Output pure dialogue text only (no speaker prefix)
						return text

		# 2. Fall back to voicetext.get_text()
		try:
			audio_base = os.path.splitext(file.get("original_name", ""))[0]
			text = voicetext.get_text(
				audio_base,
				mapped_path=file.get("mapped_path"),
				game_type=getattr(self, 'game_type', None)
			)
			if text:
				return text
		except Exception:
			pass

		return None

	def _write_voicetext_to_output(self, files, output, _format):
		"""为每个音频文件在最终输出目录生成对应的 TXT 台词文件（仅存储台词文本）。"""
		if not getattr(self, 'enable_voicetext', False) or getattr(self, 'fuzzy_match', False):
			return
		print(": Writing voice text files to output")
		count = 0
		for file in files:
			filepath = path("/".join(file["path"]), file["name"])
			base_name = os.path.splitext(file["name"])[0]
			# 输出文件路径（使用最终格式的扩展名）
			out_filepath = path(output, os.path.dirname(filepath), base_name + "." + _format)
			txt_path = os.path.splitext(out_filepath)[0] + ".txt"
			# 获取台词（优先 TSV 映射，回退 voicetext）
			text = self._get_dialogue_text(file)
			if text:
				try:
					os.makedirs(os.path.dirname(txt_path), exist_ok=True)
					with open(txt_path, "w", encoding="utf-8") as tf:
						tf.write(text)
					count += 1
				except Exception:
					pass
		print(f": Wrote {count} voice text files")

	def _print_fuzzy_stats(self):
		"""打印模糊匹配统计信息。"""
		stats = self._fuzzy_stats
		total = stats.get("total", 0)
		if total == 0:
			return
		matched = stats.get("matched", 0)
		low_ratio = stats.get("low_ratio", 0)
		asr_failed = stats.get("asr_failed", 0)
		match_rate = (matched / total * 100) if total > 0 else 0
		print(f"[fuzzy] ===== 模糊匹配统计 =====")
		print(f"[fuzzy] 总文件数: {total}")
		print(f"[fuzzy] 匹配成功: {matched} ({match_rate:.1f}%)")
		print(f"[fuzzy] 低匹配度: {low_ratio}")
		print(f"[fuzzy] ASR失败: {asr_failed}")
		print(f"[fuzzy] =========================")

	def extract_wem(self, _input, files, output):
		print(": Extracting audio as wem")
		all_sources = list(set([e["source"] for e in files]))

		pos = 0
		for source in all_sources:
			# load source
			load_path = path(_input, source)
			if self.hdiff_dir is not None:
				source = source.split(" (hdiff)")[0]
				hdiff_path = path(self.hdiff_dir.name, source)
				
				if os.path.isfile(hdiff_path):
					load_path = hdiff_path
			
			self.allocator.load_file(load_path, source)

			# extract every file from this one
			for file in [file for file in files if file["source"] == source]:
				pos += 1
				self.update_progress(pos, len(files), 1)

				file["source"] = file["source"].split(" (hdiff)")[0]
				data = self.allocator.read_at(file["source"], file["offset"], file["size"])

				if data[0:4] not in [b"RIFF", b"RIFX"]:
					# file may be vfs encrypted
					data = bytearray(data)
					wem_id = 0
					try:
						wem_id = int(file["original_name"][:-4])
					except ValueError:
						try:
							wem_id = int(file["original_name"][:-4], 16)
						except ValueError:
							continue
					decrypt(data, 0, len(data), wem_id, 0)
					if data[0:4] not in [b"RIFF", b"RIFX"]:
						continue
							
				filepath = path("/".join(file["path"]), file["name"])
				fullpath = path(output, filepath)
				os.makedirs(os.path.dirname(fullpath), exist_ok=True)
				
				with open(fullpath, "wb") as f:
					f.write(data)
					f.close()

				# Write voice text file if enabled (skip if fuzzy match is enabled - will be done later)
				if getattr(self, 'enable_voicetext', False) and not getattr(self, 'fuzzy_match', False):
					text = self._get_dialogue_text(file)
					if text:
						txt_path = os.path.splitext(fullpath)[0] + ".txt"
						try:
							with open(txt_path, "w", encoding="utf-8") as tf:
								tf.write(text)
						except Exception:
							pass  # Don't fail extraction if .txt write fails

			# unload source
			self.allocator.unload_file(source)

		# security
		self.allocator.free_mem()

	def extract_wav(self, _input, files, output):
		print(": Converting audio to wav")
		pos = 0
		for file in files:
			pos += 1
			self.update_progress(pos, len(files), 2)

			filename = f'{os.path.basename(file).split(".")[0]}.wav'
			filepath = path(output, os.path.dirname(file), filename)
			os.makedirs(os.path.dirname(filepath), exist_ok=True)

			args = [
				path(cwd, "tools/vgmstream/vgmstream-cli.exe"),
				"-o",
				filepath,
				path(_input, file)
			]

			if platform.system() != "Windows":
				args.insert(0, "wine")

			call(args)

			# Copy voice text file if it exists
			wem_file = os.path.splitext(file)[0] + ".wem"
			src_txt = path(_input, os.path.splitext(wem_file)[0] + ".txt")
			if os.path.exists(src_txt):
				dst_txt = path(output, os.path.dirname(file), os.path.splitext(filename)[0] + ".txt")
				try:
					import shutil
					shutil.copy2(src_txt, dst_txt)
				except Exception:
					pass

	def extract_ffmpeg(self, _input, files, output, _format):
		print(f": Converting audio to {_format}")

		encoders = {
			"mp3": "libmp3lame",
			"ogg": "libvorbis"
		}
		
		encoder = encoders[_format]

		pos = 0
		for file in files:
			pos += 1
			self.update_progress(pos, len(files), 3)

			filename = f'{os.path.basename(file).split(".")[0]}.{_format}'
			filepath = path(output, os.path.dirname(file), filename)
			os.makedirs(os.path.dirname(filepath), exist_ok=True)

			args = [
				path(cwd, "tools/ffmpeg/ffmpeg.exe"),
				"-i",
				path(_input, file),
				"-acodec",
				encoder,
				"-b:a",
				"192k", # 192|4
				filepath
			]

			if platform.system() != "Windows":
				args.insert(0, "wine")

			call(args)
		
			# Copy voice text file if it exists
			wav_file = os.path.splitext(file)[0] + ".wav"
			src_txt = path(_input, os.path.splitext(wav_file)[0] + ".txt")
			if os.path.exists(src_txt):
				dst_txt = path(output, os.path.dirname(file), os.path.splitext(filename)[0] + ".txt")
				try:
					import shutil
					shutil.copy2(src_txt, dst_txt)
				except Exception:
					pass

	### other ###

	def update_progress(self, current, total, step, status=None, stats=None):
		base = 100 / self.steps
		total_pct = current * base / total + base * (step - 1)
		file_pct = current * 100 / total
		self.progress(["total", total_pct, status, stats])
		self.progress(["file", file_pct, status, stats])

	def reset(self):
		self.mapper = None
		for e in self.maps.values():
			e.reset()
		self.maps.clear()
		self.allocator.free_mem()
		if self.hdiff_dir is not None:
			self.hdiff_dir.cleanup()
			self.hdiff_dir = None
