$Ó¦:(r÷¬ÝVÔ VpŒFZåXí¿3à>½¯«tions import Fraction
from PySide2 import QtUiTools, QtCore, QtWidgets

from widgets import jupiter_cacheclean_main_ui as main_ui
from widgets import jupiter_cacheclean_versionwidget_ui as widget_ui


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


class CacheCleanWindow(QtWidgets.QWidget):
	def __init__(self):
		super(CacheCleanWindow, self).__init__()
		# Initial UI A:\AppBase\Houdini\localLib\scripts\python\widgets\test_hou_ui.ui
		self.window = QtWidgets.QMainWindow()
		self.ui = main_ui.Ui_MainWindow()
		self.ui.setupUi(self.window)
		self.window.show()

	def createNewWidgets(self):
		self.mainBox = QtWidgets.QGroupBox()
		self.horizontalLayout = QtWidgets.QHBoxLayout(self.mainBox)
		self.nodeTable = QtWidgets.QTableWidget(self.mainBox)
		self.horizontalLayout.addWidget(self.nodeTable)
		self.versionsTable = QtWidgets.QTableWidget(self.mainBox)
		self.horizontalLayout.addWidget(self.versionsTable)
		self.ui.verticalLayout_4.addWidget(self.mainBox)

		# _newname = "mainBox_" + str(self.count)
		# self.count = self.count + 1
		# self.widget = QtWidgets.QWidget()
		# self.widget.setObjectName(_newname)
		# self.wui = widget_ui.Ui_Widget()
		# self.wui.setupUi(self.widget)
		# self.widget.show()
		# self.target_layout = QtWidgets.QVBoxLayout(self.ui.target_widget)
		# setattr(self.ui, _newname, self.wui.mainBox)
		# self.target_layout.addWidget(self.wui.mainBox)
		# return self.mainBox


class SingleCacheNode:
	def __init__(self, node, main_win):
		self.win = main_win
		self.nodetype = node.type().name()
		self.loaded = node.parm("loadfromdisk").eval()
		self.current_filemethod = node.parm("filemethod").eval()  # constructed, explicit
		self.current_filetype = node.parm("filetype").eval()
		self.filetype = [".bgeo.sc", ".vdb"][int(self.current_filetype)]
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
			self.local_versions = 0
			self.num_versions = 0
			print("no node_main_folder exist on drive")

		if self.local_versions:
			self.num_versions = len(self.local_versions)
			self.collectversion()
			self.versionpanel = self.win.createNodeWidgets()

	def collectversion(self):
		for i in range(0, self.num_versions):
			versionfolder = self.local_versions[i]
			path = versionfolder.path.replace('\\', '/')
			name = versionfolder.name
			exec(f"self.v{i + 1} = VersionFolder(self, '{i + 1}', '{path}', '{name}', '{self.filetype}')")
			# print(f"versionfolder{i+1} is ====", f"self.version_folder_{i+1}")
			exec(f"self.dict_v{i + 1} = self.v{i + 1}.make_dict()")


class VersionFolder:
	def __init__(self, index, node, path, name, filetype):
		# self.version_name = name
		self.node = node
		self.version_index = index
		self.version_size = fsize(path)
		self.mark_dirty = 0
		self.version_inc = 1
		selff0gxù4s•Ùd÷®ßñÃ\D£l+ÔK-	Ày…_xvipe = [".bgeo.sc", ".vdb"][int(filetype_index)]
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
		# print("==========sequence is dirty============")
		else:
			self.version_files = len(frames_list)
			self.endfr = max(frames_list)
			self.startfr = min(frames_list)
			if self.version_files > 0:
				fct = Fraction((float(float_frames_list[1]) - float(float_frames_list[0])) / 1)
				self.version_inc = fct.numerator
				self.version_substep = fct.denominator

	# print(self.version_inc)
	# print(self.version_substep)

	def podcast_detail(self):
		if not self.mark_dirty:
			print(f"{self.node} ==== {self.startfr} to {self.endfr} "
				  f"with Inc of {self.version_inc} and Subframe of {self.version_substep}"
				  f" total {self.version_files} cache files")
		else:
			print(f"v{self.node} is dirty")

	def make_dict(self):
		self.version_report = {}
		if not self.mark_dirty:
			self.version_report["node"] = self.node
			self.version_report["version"] = self.version_index
			self.version_report["start"] = self.startfr
			self.version_report["max"] = self.endfr
			self.version_report["inc"] = self.version_inc
			self.version_report["substep"] = self.version_substep
			self.version_report["totalfiles"] = self.version_files
		else:
			print(f"{self.node} is dirty")

		return self.version_report


pane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
pane_node = pane.pwd()

fileCacheNode = []
prismCacheNode = []
all_sop_nodes = hou.node("/obj/").allSubChildren()
for i in all_sop_nodes:
	if "filecacheprism" in i.type().name():
		print("found filecacheprism node: ", i.path())
		prismCacheNode.append(i)
	if i.type().name() == "filecache::2.0":
		print("found hou filecache node: ", i.path())
		fileCacheNode.append(i)

main_win = CacheCleanWindow()
for n in prismCacheNode:
	test = SingleCacheNode(n, main_win)
	for v in range(1, test.num_versions):
		exec(f"test.v{v}.podcast_detail()")
	# print(test.v3.podcast_detail)
	pass
