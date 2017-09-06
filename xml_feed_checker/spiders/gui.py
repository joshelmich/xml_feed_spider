#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author Jos Helmich
# email: jos.helmich@finlandned.org
# 
import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui

# Sample info
#my_struct = [
#2017-09-05 21:11:32 [xml_feed_spider.log] ERROR: Status; HttpError on http://wrongsitename.com/ , DownloadTime: 0.004
#2017-09-05 21:11:32 [xml_feed_spider.log] INFO: Status; NoError on http://finlandned.org/administrator/index.php , DownloadTime: 0.375
#2017-09-05 21:11:33 [xml_feed_spider.log] ERROR: Status; RequiredPathNotFound on http://www.valaquanta.fi/wp-login.php , DownloadTime: 1.380
#]
my_struct = []
table = None

DOWNLOAD_TIMER_INTERVAL = 10000 # Be careful! This interval should not be lower than the time that it takes for run.sh to complete

my_keys = ["Date", "Time", "ignore", "Status", "ignore", "Specific", "ignore", "Web url", "ignore", "ignore", "Download Time"]
headers = ["Date", "Time",  "Status", "Specific", "Web url", "Download Time"]

class MyTable(QTableWidget):
	def __init__(self, thestruct, *args):
		QTableWidget.__init__(self, *args)
		self.data = my_struct
		self.keys = my_keys		
		self.headers = headers
		self.setmydata()
        
	def setmydata(self):
		self.setHorizontalHeaderLabels(self.headers)		
		n = 0		
		for n in range(0, len(self.data)):
			m = 0			
			j = 0
			for m in range(0, len(self.keys)):
				if self.keys[m] != 'ignore':
					item = self.data[n][m]
					# get rid of : after ERROR and INFO
					if item.find(":") == len(item) -1:
						temp = item.split(":");
						item = temp[0]					
					newitem = QTableWidgetItem(item)
					self.setItem(n, j, newitem)
					j += 1
				m += 1
			n += 1
		pass

	def refresh(self):
		self.data = my_struct
		for n in range(0, len(my_struct)):
			j = 0
			for m in range(0, len(self.keys)):
				if self.keys[m] != 'ignore':
					item = self.data[n][m]
					# get rid of : after ERROR and INFO
					if item.find(":") == len(item) -1:
						temp = item.split(":")
						item = temp[0]	
					self.item(n, j).setText(item)
						
					j += 1
		pass

# this class is needed to resize the columns properly
class ResizeDelegate(QStyledItemDelegate):

    def __init__(self, table, stretch_column, *args, **kwargs):
        super(ResizeDelegate, self).__init__(*args, **kwargs)        
        self.table = table
        self.stretch_column = stretch_column

    def sizeHint(self, option, index):
        size = super(ResizeDelegate, self).sizeHint(option, index)
        if index.column() == self.stretch_column:
            total_width = self.table.viewport().size().width()
            calc_width = size.width()
            for i in range(self.table.columnCount()):
                if i != index.column():
                    option_ = QtGui.QStyleOptionViewItem()
                    index_ = self.table.model().index(index.row(), i)
                    self.initStyleOption(option_, index_)
                    size_ = self.sizeHint(option_, index_)
                    calc_width += size_.width()
            if calc_width < total_width:
                size.setWidth(size.width() + total_width - calc_width)
        return size

# this class reads the information from file
class info(QObject):
	
	refresh = pyqtSignal()
	    
	def get_information(self):	
		del my_struct[:]	
		os.system("./run.sh")
		f = open('status.txt')
		f.seek(0)
		lines = f.readlines()
		for i in range(0, len(lines)):
			line = lines[i].split()
			if len(line) > 2:
				my_struct.append(line)
		f.close()
		self.refresh.emit()
		
	def get_refresh_interval(self):
		f = open('gui.cfg')
		if (f > 0):
			cfg_lines = f.readlines()
			print "cfg_lines", cfg_lines
			for i in range(0, len(cfg_lines)):
				line = cfg_lines[i].split()
				print "line", line
				if len(line) >= 3:
					if line[0] == "DOWNLOAD_TIMER_INTERVAL" and line[1] == "=":
						interval = line[2]
						return int(interval)
			f.close()
		return -1
			
def main():       
	app = QtGui.QApplication(sys.argv)
	# grabbing the first info
	my_info = info()
	ret = my_info.get_refresh_interval()
	if (ret != -1):
		DOWNLOAD_TIMER_INTERVAL = ret
	my_info.get_information()	
	# initializing the table
	table = MyTable(my_struct, len(my_struct), len(headers))
	delegate = ResizeDelegate(table, 0)
	table.setItemDelegate(delegate)
	table.resizeColumnsToContents()	
	# scheduling refresh
	my_info.refresh.connect(table.refresh) # when my_inf emits a signal table.refresh is executed
	timer = QTimer()
	timer.timeout.connect(my_info.get_information)
	timer.start(DOWNLOAD_TIMER_INTERVAL)
	# display table widget
	table.showMaximized()
	sys.exit(app.exec_())
    
if __name__ == '__main__':
	main()
    
