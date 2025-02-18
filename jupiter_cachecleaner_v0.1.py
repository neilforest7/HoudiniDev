import hou
import os
from fractions import Fraction


def folder_size(path):
	total = 0
	for entry in os.scandir(path):
		if entry.is_file():
			total += entry.stat().st_size
		elif entry.is_dir():
			total += folder_size(entry.path)
	return total


def format_size(size: int) -> str:
	for unit in ("B", "K", "M", "G", "T"):
		if size < 1024:
			break
		size /= 1024
	return f"{size:.2f}{unit}"


def fsize(path):
	try:
		return format_size(folder_size(path))
	except TypeError:
		print('No Such Directory')


class SingleCacheNode:
	def __init__(self, node):
		self.nodetype = node.type().name()
		self.loaded = node.parm("loadfromdisk").eval()
		self.current_filemethod = node.parm("filemethod").eval()  # constructed, explicit
		self.current_filetype = node.parm("filetype").eval()
		print(self.current_filetype)
		self.current_timedependent = node.parm("timedependent").eval()

		self.current_cachename = node.parm("cachename").eval()
		self.current_cachefolder = node.parm("cachedir").eval().replace("\\", "/")
		self.current_version = node.parm("version").evalAsInt()

		self.current_framerange = node.parmTuple("f").eval()  # float3 use __getitem__(index)
		self.current_substeps = node.parm("substeps").evalAsInt()
		self.current_descriptlabel = node.parm("descriptivelabel").eval()

		self.local_versions = []  # list of scandir entries
		self.local_main_folder = os.path.dirname(self.current_cachefolder)
		try:
			self.local_main_folder_size = fsize(self.local_main_folder)
			for entry in os.scandir(self.local_main_folder):
				if not entry.name.startswith('.') and entry.is_dir():
					self.local_versions.append(entry)
		except FileNotFoundError:
			print("no node_main_folder exist on drive")

		# for version in self.local_versions:
		# 	self.createversionfolder(version)
		if self.local_versions:
			for i in range(0, len(self.local_versions)):
				versionfolder = self.local_versions[i]
				path = versionfolder.path.replace('\\', '/')
				name = versionfolder.name
				exec(f"self.version_folder_{i + 1} = VersionFolder('{path}', '{name}', '{self.current_filetype}')")
			# print(f"versionfolder{i+1} is ====", f"self.version_folder_{i+1}")


class VersionFolder:
	def __init__(self, path, name, filetype_index):
		# self.version_name = name
		self.version_size = fsize(path)
		self.mark_dirty = 0
		self.version_inc = 1
		self.version_substep = 1
		filetype = [".bgeo.sc", ".vdb"][int(filetype_index)]
		cache_files = os.scandir(path)

		print(f"=========={name}============")
		has_substep = 0
		no_substep = 0
		frames_list = []
		float_frames_list = []

		for f in cache_files:
			d = f.name.rstrip(filetype).split(name + '.')[-1]
			if '.' in d:
				# has substeps like: high_v3.0006.000.bgeo.sc
				frame = d.split('.')[0]
				has_substep = 1
			else:
				# has no substeps like: high_v3.0006.bgeo.sc
				frame = d
				no_substep = 1
			frames_list.append(frame)
			float_frames_list.append(float(d))

		if has_substep and no_substep:
			self.mark_dirty = 1
			print("==========sequence is dirty============")
		else:
			self.version_files = len(frames_list)
			self.maxframe = max(frames_list)
			self.minframe = min(frames_list)
			if self.version_files > 0:
				fct = Fraction((float(float_frames_list[1]) - float(float_frames_list[0])) / 1)
				self.version_inc = fct.numerator
				self.version_substep = fct.denominator
				# print(self.version_inc)
				# print(self.version_substep)
				# print(f"version_framerange ==== {self.minframe} to {self.maxframe} "
				# 	  f"with Inc of {self.version_inc} and Subframe of {self.version_substep}"
				# 	  f" total {self.version_files} cache files")


pane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
pane_node = pane.pwd()

fileCacheNode = []
prismCacheNode = []
all_sop_nodes = hou.node("/obj/").allSubChildren()
for i in all_sop_nodes:
	if "filecacheprism" in i.type().name():
		print("found filecacheprism node: ", i.path())
		# print(i.type())
		prismCacheNode.append(i)
	if i.type().name() == "filecache::2.0":
		print("found hou filecache node: ", i.path())
		fileCacheNode.append(i)

for n in prismCacheNode:
	test = SingleCacheNode(n)
	print(test.version_folder_3.version_substep)
	pass
