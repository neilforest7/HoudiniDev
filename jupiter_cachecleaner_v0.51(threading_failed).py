import os
import threading
import queue

from fractions import Fraction
from time import sleep

from hutil.Qt import QtCore, QtGui, QtWidgets
# from QtCore import QProcess, QObject, SIGNAL, QProcess

import hou

from widgets import jupiter_cacheclean_main_ui as main_ui
from widgets import jupiter_cacheclean_nodewidget_ui as nodewidget_ui
from widgets import jupiter_cacheclean_versionwidget_ui as versionwidget_ui

_green = "background-color: rgb(5, 98, 75);"
_grey = "background-color: rgb(40, 44, 52);"
_red = "background-color: rgb(98, 48, 84);"


# TODO: Adding delete folder function to top of the menu
# TODO: Checkbox controls delete or not
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


def readQssFile(filePath):
	with open(filePath, 'r') as fileObj:
		styleSheet = fileObj.read()
	return styleSheet


def showinnetworkeditor(path):
	pane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
	_p_path = hou.node(path).parent().path()
	pane.cd(_p_path)
	hou.node(path).setSelected(False, True)
	hou.node(path).setDisplayFlag(True)
	pass


class CacheCleanWindow(QtWidgets.QWidget):
	def __init__(self):
		super(CacheCleanWindow, self).__init__()
		# Initial UI A:\AppBase\Houdini\localLib\scripts\python\widgets\test_hou_ui.ui
		self.window = QtWidgets.QMainWindow()
		self.ui = main_ui.Ui_MainWindow()
		self.ui.setupUi(self.window)
		self.window.show()
		styleSheet = readQssFile(f'{os.path.dirname(__file__)}/widgets/ManjaroMix.qss')
		self.window.setStyleSheet(styleSheet)

	def createNodeWidgets(self, node_detail):
		self.n_widget = QtWidgets.QGroupBox()
		self.nui = nodewidget_ui.Ui_Widget()
		self.nui.setupUi(self.n_widget)
		self.ui.verticalLayout_6.addWidget(self.n_widget)

		self.nui.label_currentpath.setText(node_detail["path"])
		self.nui.label_loaded_or_not.setText(node_detail["loaded"])
		self.nui.label_nodetype.setText(node_detail["nodetype"])
		self.nui.label_timedep_or_not.setText(node_detail["timedependent"])
		self.nui.label_filemethod.setText(node_detail["filemethod"])
		self.nui.label_currentversion.setText(node_detail["currentversion"])
		self.nui.label_cachename.setText(node_detail["cachename"])
		self.nui.label_startfr.setText(node_detail["startfr"])
		self.nui.label_endfr.setText(node_detail["endfr"])
		self.nui.label_inc.setText(node_detail["inc"])
		self.nui.label_substep.setText(node_detail["substep"])
		self.nui.btn_show_in_network.clicked.connect(lambda: showinnetworkeditor(node_detail["path"]))
		return self.nui

	def createVersionWidget(self, version_detail):
		self.v_widget = QtWidgets.QGroupBox()
		self.vui = versionwidget_ui.Ui_Form()
		self.vui.setupUi(self.v_widget)
		self.nui.verticalLayout_3.addWidget(self.v_widget)
		print(version_detail["version"] + "'s version widget is created")

		self.vui.singleFramed = version_detail["mark_singleframe"]
		self.vui.label_versionnum.setText(version_detail["version"])
		if self.vui.singleFramed:
			self.vui.frame_6.hide()
			self.vui.frame_8.hide()
			self.vui.frame_9.hide()
			self.vui.label_endfrnum.hide()
			self.vui.label_10.setText("(SingleFrame)")
		self.vui.label_sizestr.setText(version_detail["version_size"])
		self.vui.label_formatstr.setText(version_detail['filetype'])
		self.vui.label_startfrnum.setText(str(version_detail["start"]))
		self.vui.label_endfrnum.setText(str(version_detail["end"]))
		self.vui.label_incnum.setText(str(version_detail["inc"]))
		self.vui.label_substepnum.setText(str(version_detail["substep"]))
		self.vui.checkBox.setChecked(version_detail["clean"])
		self.vui.cb = version_detail["clean"]
		self.vui.tag = version_detail["tag"]
		_version_path = version_detail["version_path"]
		print(_version_path + " is the version path")
		self.vui.btn_open.clicked.connect(lambda: os.startfile(_version_path))
		self.vui.checkBox.stateChanged.connect(lambda x: self.enable_clean() if x else self.disable_clean())
		return self.vui

	def enable_clean(self):
		self.vui.cb = 1
		print(self.vui.checkBox)
		print("clean_button is on for", self.vui.label_versionnum.text())

	def disable_clean(self):
		self.vui.cb = 0
		print("clean_button is off for", self.vui.label_versionnum.text())


class VersionWidget:
	def __init__(self, node, path, name, filetype):
		# self.version_name = name
		self.node = node
		self.filetype = filetype
		self.version_path = os.path.realpath(path)
		self.version = os.path.basename(path)
		self.version_size = fsize(path)
		self.tag = ""
		self.mark_clean = 0
		self.mark_dirty = 0
		self.mark_singleframe = 0
		self.version_inc = 1
		self.version_substep = 1
		cache_files = os.scandir(path)

		print(f"===================={name}======================")
		has_substep = 0
		no_substep = 0
		frames_list = []
		float_frames_list = []
		lst = len(os.listdir(path))
		if lst == 1:
			# single frame like: Cache_box_high3_v3.bgeo.sc
			self.mark_singleframe = 1
			no_substep = 1
		elif not lst:
			# only folder exist but no cache files
			self.mark_dirty = 1
		else:
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
		elif self.mark_dirty:
			pass
		elif self.mark_singleframe:
			self.version_files = 1
			self.endfr = 0
			self.startfr = 0
			self.version_inc = 1
			self.version_substep = 1
		else:
			self.version_files = len(frames_list)
			self.endfr = int(max(frames_list))
			self.startfr = int(min(frames_list))
			if self.version_files > 0:
				fct = Fraction((float(float_frames_list[1]) - float(float_frames_list[0])) / 1)
				self.version_inc = fct.numerator
				self.version_substep = fct.denominator

	def make_version_dict(self):
		self.version_report = {}
		if not self.mark_dirty:
			self.version_report["version"] = self.version
			self.version_report["version_size"] = self.version_size
			self.version_report["version_path"] = self.version_path
			self.version_report["filetype"] = self.filetype
			self.version_report["start"] = self.startfr
			self.version_report["end"] = self.endfr
			self.version_report["inc"] = self.version_inc
			self.version_report["substep"] = self.version_substep
			self.version_report["totalfiles"] = self.version_files
			self.version_report["mark_singleframe"] = self.mark_singleframe
			self.version_report["clean"] = self.mark_clean
			self.version_report["tag"] = self.tag
			self.podcast_detail()
			return self.version_report
		else:
			print(f"{self.node} is dirty")
			return None

	def podcast_detail(self):
		if not self.mark_dirty:
			# print(f"{self.node} ==== {self.startfr} to {self.endfr} "
			# 	  f"with Inc of {self.version_inc} and Subframe of {self.version_substep}"
			# 	  f" total {self.version_files} cache files")
			pass
		else:
			print(f"v{self.node} is dirty")


class NodeWidget:
	def __init__(self, node):
		# Prepare data for nodeWidget
		self.current_nodepath = node.path()
		self.current_nodetype = node.type().name()
		_loaded = node.parm("loadfromdisk").eval()
		self.current_loaded = ["Unload", "Loaded"][int(_loaded)]
		_filetype = node.parm("filetype").eval()
		self.current_filetype = [".bgeo.sc", ".vdb"][int(_filetype)]
		_timedependent = node.parm("timedependent").eval()
		self.current_timedependent = ["SingleFramed", "TimeDependent"][int(_timedependent)]
		_filemethod = node.parm("filemethod").eval()
		self.current_filemethod = ["Constructed", "Explicit"][int(_filemethod)]
		_version = node.parm("version").evalAsInt()
		self.current_version = "v" + str(_version)
		self.current_cachename = node.parm("basename").eval()
		self.current_framerange = node.parmTuple("f").eval()  # float3 use __getitem__(index)
		self.current_substeps = node.parm("substeps").evalAsInt()
		# All above is preparation

		self.local_versions = []  # list of scandir entries
		self.current_cachefolder = node.parm("cachedir").eval().replace("\\", "/")
		try:
			self.local_main_folder = os.path.dirname(self.current_cachefolder)
			self.local_main_folder_size = fsize(self.local_main_folder)
			for entry in os.scandir(self.local_main_folder):
				if not entry.name.startswith('.') and entry.is_dir():
					self.local_versions.append(entry)
		except FileNotFoundError:
			self.local_versions = 0
			self.num_versions = 0
			print("no node_main_folder exist on drive")

	def make_node_dict(self):
		self.node_report = {}
		self.node_report["path"] = self.current_nodepath
		self.node_report["loaded"] = self.current_loaded
		self.node_report["nodetype"] = self.current_nodetype
		self.node_report["timedependent"] = self.current_timedependent
		self.node_report["filemethod"] = self.current_filemethod
		self.node_report["currentversion"] = self.current_version
		self.node_report["cachename"] = self.current_cachename
		self.node_report["startfr"] = str(int(self.current_framerange[0]))
		self.node_report["endfr"] = str(int(self.current_framerange[1]))
		self.node_report["inc"] = str(int(self.current_framerange[2]))
		self.node_report["substep"] = str(self.current_substeps)
		return self.node_report


class MainFunction:
	def __init__(self, nodelist, main_window):
		self.win = main_window
		threadID = 1
		threads = []
		for node in nodelist:
			self.node = node
			self.n = NodeWidget(self.node)

			if self.n.local_versions:
				self.node_dict = self.n.make_node_dict()
				self.num_versions = len(self.n.local_versions)
				self.nui = self.win.createNodeWidgets(self.node_dict)

			self.all_vui_nested_dict = {}
			self.all_version_nested_dict = {}

			if self.n.local_versions:
				for i in range(0, self.num_versions):
					version_folder = self.n.local_versions[i]
					filetype = self.n.current_filetype
					tName = self.n.current_nodepath + "_v" + str(i)
					thread = myThread(threadID, tName, i, version_folder, filetype)
					thread.start()
					threads.append(thread)
					threadID += 1
		for t in threads:
			t.join()
		# self.compare_node_to_version()
		# self.loopvui()

	def thread_version(self, index, versionfolder, filetype):
		print("Acquiring queue lock")
		queueLock.acquire()
		path = versionfolder.path.replace('\\', '/')
		name = versionfolder.name
		v = VersionWidget(self, path, name, filetype)
		if not v.mark_dirty:
			print("Comparing version to node")
			self.compare_version_to_node(v)
			version_dict = v.make_version_dict()
			self.all_vui_nested_dict[f"v{index + 1}"] = v
			print(self.all_vui_nested_dict[f"v{index + 1}"])
			self.all_version_nested_dict[f"v{index + 1}"] = version_dict
			print(self.all_version_nested_dict[f"v{index + 1}"])
			vui = self.win.createVersionWidget(version_dict)
			print(vui)
			queueLock.release()
			return vui
		else:
			queueLock.release()
			return None
		# self.colorize_vui()

	def compare_version_to_node(self, v):
		if self.n.current_timedependent == "SingleFramed":
			if v.mark_singleframe and (v.version == self.n.current_version):
				# node require singleframe and version is singleframe and version matched
				v.tag = "currentversion"
			elif v.mark_singleframe:
				# versions don't matched
				v.tag = "notcurrentversion"
			else:
				# node require singleframe and version is sequence
				v.tag = "notsingleframe"
		else:
			if v.version != self.n.current_version:
				# both sequence but versions don't match
				v.tag = "notcurrentversion"
			elif (v.version == self.n.current_version and
				  v.startfr == int(self.n.current_framerange[0]) and
				  v.endfr + 1 == int(self.n.current_framerange[1]) and
				  v.version_inc == int(self.n.current_framerange[2]) and
				  v.version_substep == int(self.n.current_substeps) and
				  v.version_inc > 1):
				# special occasion when increments endframe = endframe_set_on_node - 1
				v.tag = "currentversion"
			elif (v.startfr != int(self.n.current_framerange[0]) or
				  v.endfr != int(self.n.current_framerange[1]) or
				  v.version_inc != int(self.n.current_framerange[2]) or
				  v.version_substep != int(self.n.current_substeps)):
				# versions matched but sequences don't match
				v.tag = "framesdontmatch"
			else:
				# all match which is desired version
				v.tag = "currentversion"

	def compare_node_to_version(self):
		if self.n.current_timedependent == "SingleFramed":
			self.nui.frame_12.setStyleSheet(_red)
		if self.n.current_loaded == "Unload":
			self.nui.frame_11.setStyleSheet(_red)
		clean_list = []
		tag_list = []
		size_list = []
		for version, version_dict in self.all_version_nested_dict.items():
			clean_list.append(int(version_dict["clean"]))
			size_list.append(str(version_dict["version_size"]))
			tag_list.append(str(version_dict["tag"]))
		if "framesdontmatch" in tag_list:
			self.nui.label_cleaned_or_not.setText("Clean with Care")
			self.nui.label_cleaned_or_not.setStyleSheet(_red)
		elif "currentversion" not in tag_list:
			self.nui.label_cleaned_or_not.setText("Clean All")
			self.nui.label_cleaned_or_not.setStyleSheet(_red)
		else:
			self.nui.label_cleaned_or_not.setText("Clean Others")
			self.nui.label_cleaned_or_not.setStyleSheet(_green)

	def loopvui(self):
		tag_state_list = []
		for _version, _vui in self.all_vui_nested_dict.items():
			tag_state_list.append(_vui.tag)
		print(tag_state_list)

	def colorize_vui(self):
		if self.v.tag == "framesdontmatch":
			self.vui.widget.setStyleSheet(_red)
			self.vui.checkBox.setChecked(1)
			self.vui.checkBox.setText("Frames Dont Match")

		if self.v.tag == "notsingleframe":
			self.vui.widget.setStyleSheet(_grey)
			self.vui.checkBox.setChecked(1)
			self.vui.checkBox.setText("Not SingleFrame")

		if self.v.tag == "notcurrentversion":
			self.vui.widget.setStyleSheet(_grey)
			self.vui.checkBox.setChecked(1)

		if self.v.tag == "currentversion":
			self.vui.widget.setStyleSheet(_green)
			self.vui.checkBox.setChecked(0)
			self.vui.checkBox.setText("Current Version")
			self.v.tag = "currentversion"
		pass


class myThread(threading.Thread):
	def __init__(self, threadID, name, i, version_folder, filetype):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.versionfolder = version_folder
		self.filetype = filetype
		self.i = int(i)

	def run(self):
		print("开启线程：" + self.name)
		test.thread_version(self.i, self.versionfolder, self.filetype)
		print("完成构建线程：" + self.name)


pane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
pane_node = pane.pwd()

fileCacheNode = []
prismCacheNode = []
all_sop_nodes = hou.node("/obj/geo2").allSubChildren()
for i in all_sop_nodes:
	if "filecacheprism" in i.type().name():
		print("found filecacheprism node: ", i.path())
		prismCacheNode.append(i)
	if i.type().name() == "filecache::2.0":
		print("found hou filecache node: ", i.path())
		prismCacheNode.append(i)

queueLock = threading.Lock()

main_win = CacheCleanWindow()
test = MainFunction(prismCacheNode, main_win)
# for n in prismCacheNode:
# 	test = SingleCacheNode(n, main_win)
# 	pass


# class SingleCacheNode:
# 	def __init__(self, node, _mainwindow):
# 		self.win = _mainwindow
# 		self.node = node
#
# 		self.n = NodeWidget(self.node)
# 		if self.n.local_versions:
# 			self.node_dict = {}
# 			self.num_versions = len(self.n.local_versions)
# 			# CORE #########################################################
# 			self.node_dict = self.n.make_node_dict()
# 			self.nui = self.win.createNodeWidgets(self.node_dict)
#
# 		self.all_vui_nested_dict = {}
# 		self.all_version_nested_dict = {}
# 		if self.n.local_versions:
# 			for i in range(0, self.num_versions):
# 				self.version_dict = {}
# 				_temp_version_dict = {}
# 				_temp_vui_dict = {}
# 				versionfolder = self.n.local_versions[i]
# 				path = versionfolder.path.replace('\\', '/')
# 				name = versionfolder.name
# 				# CORE #########################################################
# 				self.v = VersionWidget(self, path, name, self.n.current_filetype)
# 				if not self.v.mark_dirty:
# 					# jump over dirty caches
# 					self.compare_version_to_node()
# 					self.version_dict = self.v.make_version_dict()
# 					_temp_vui_dict[f"v{i + 1}"] = self.v
# 					_temp_version_dict[f"v{i + 1}"] = self.version_dict
# 					self.all_vui_nested_dict.update(_temp_vui_dict)
# 					self.all_version_nested_dict.update(_temp_version_dict)
# 					self.vui = self.win.createVersionWidget(self.version_dict)
# 					self.colorize_vui()
#
# 		self.compare_node_to_version()
# 		self.loopvui()
#
# 	def compare_version_to_node(self):
# 		if self.n.current_timedependent == "SingleFramed":
# 			if self.v.mark_singleframe and (self.v.version == self.n.current_version):
# 				# node require singleframe and version is singleframe and version matched
# 				self.v.tag = "currentversion"
# 			elif self.v.mark_singleframe:
# 				# versions don't matched
# 				self.v.tag = "notcurrentversion"
# 			else:
# 				# node require singleframe and version is sequence
# 				self.v.tag = "notsingleframe"
# 		else:
# 			if self.v.version != self.n.current_version:
# 				# both sequence but versions don't match
# 				self.v.tag = "notcurrentversion"
# 			elif (self.v.version == self.n.current_version and
# 				  self.v.startfr == int(self.n.current_framerange[0]) and
# 				  self.v.endfr + 1 == int(self.n.current_framerange[1]) and
# 				  self.v.version_inc == int(self.n.current_framerange[2]) and
# 				  self.v.version_substep == int(self.n.current_substeps) and
# 				  self.v.version_inc > 1):
# 				# special occasion when increments endframe = endframe_set_on_node - 1
# 				self.v.tag = "currentversion"
# 			elif (self.v.startfr != int(self.n.current_framerange[0]) or
# 				  self.v.endfr != int(self.n.current_framerange[1]) or
# 				  self.v.version_inc != int(self.n.current_framerange[2]) or
# 				  self.v.version_substep != int(self.n.current_substeps)):
# 				# versions matched but sequences don't match
# 				self.v.tag = "framesdontmatch"
# 			else:
# 				# all match which is desired version
# 				self.v.tag = "currentversion"
#
# 	def compare_node_to_version(self):
# 		if self.n.current_timedependent == "SingleFramed":
# 			self.nui.frame_12.setStyleSheet(_red)
# 		if self.n.current_loaded == "Unload":
# 			self.nui.frame_11.setStyleSheet(_red)
# 		clean_list = []
# 		tag_list = []
# 		size_list = []
# 		for version, version_dict in self.all_version_nested_dict.items():
# 			clean_list.append(int(version_dict["clean"]))
# 			size_list.append(str(version_dict["version_size"]))
# 			tag_list.append(str(version_dict["tag"]))
# 		if "framesdontmatch" in tag_list:
# 			self.nui.label_cleaned_or_not.setText("Clean with Care")
# 			self.nui.label_cleaned_or_not.setStyleSheet(_red)
# 		elif "currentversion" not in tag_list:
# 			self.nui.label_cleaned_or_not.setText("Clean All")
# 			self.nui.label_cleaned_or_not.setStyleSheet(_red)
# 		else:
# 			self.nui.label_cleaned_or_not.setText("Clean Others")
# 			self.nui.label_cleaned_or_not.setStyleSheet(_green)
#
# 	def loopvui(self):
# 		tag_state_list = []
# 		for _version, _vui in self.all_vui_nested_dict.items():
# 			tag_state_list.append(_vui.tag)
# 		print(tag_state_list)
#
# 	def colorize_vui(self):
# 		if self.v.tag == "framesdontmatch":
# 			self.vui.widget.setStyleSheet(_red)
# 			self.vui.checkBox.setChecked(1)
# 			self.vui.checkBox.setText("Frames Dont Match")
#
# 		if self.v.tag == "notsingleframe":
# 			self.vui.widget.setStyleSheet(_grey)
# 			self.vui.checkBox.setChecked(1)
# 			self.vui.checkBox.setText("Not SingleFrame")
#
# 		if self.v.tag == "notcurrentversion":
# 			self.vui.widget.setStyleSheet(_grey)
# 			self.vui.checkBox.setChecked(1)
#
# 		if self.v.tag == "currentversion":
# 			self.vui.widget.setStyleSheet(_green)
# 			self.vui.checkBox.setChecked(0)
# 			self.vui.checkBox.setText("Current Version")
# 			self.v.tag = "currentversion"
# 		pass
