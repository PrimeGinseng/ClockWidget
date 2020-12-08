'''
	clockwidget.py
	Author: Mango Solomento
	do not duplicate or reproduce unless ur super fly k?
'''

#import wx
import time, os, urllib2, re
from sys import exit
from urlparse import urlparse
try:
	import wx
except ImportError:
	raise ImportError, "The wxPython module is required to run this program."

# moving window without border code jacked straight from here: https://bytes.com/topic/python/answers/699951-move-windows-without-title-bar-wxpython#post3801341

TRAY_ICON = "icon.png"
TRAY_TOOLTIP = "Holding on anger is like drinking poison and expecting the other person to die."
WEATHERURL = "https://weather.gc.ca/rss/city/qc-147_e.xml"

global temperature
temperature = "-0.0" # if the weather ever displays -0.0, then the weather is not being pulled at launch
global temprun
temprun = 0
global _clickenable


def create(parent):
    return Frame1(parent)

[wxID_FRAME1] = [wx.NewId() for _init_ctrls in range(1)]
	
def get_temp():
	o = urlparse(WEATHERURL)
	if o.scheme in ["http", "https"]:
		request = urllib2.Request(WEATHERURL)
		try:
			response = urllib2.urlopen(request)
		except urllib2.urlopen(request) as e:
			print "Error accessing web page: " + WEATHERURL + ": " + str(e.code)
		line = response.readline()
		while line:
			if "Temperature:" not in line:
				line = response.readline()
			else:
				break
		sign = 1
		if "-" in line:
			sign = -1
		line = float(re.search(r'\d+.\d', line).group()) * sign
		print line
		response.close()
		return line
	else:
		print "gotta use a real url, fruitnuts"

class Frame1(wx.Frame): 
	def _init_ctrls(self, prnt):
		wx.Frame.__init__(self, id=wxID_FRAME1, name='', parent=prnt, pos=wx.Point(22, 22), size=wx.Size(90, 15), style=(wx.NO_BORDER | wx.FRAME_NO_TASKBAR), title='Frame1')
		self.Bind(wx.EVT_MOTION, self.OnFrame1Motion)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnFrame1LeftDown)
	
	def __init__(self, parent):
		self._init_ctrls(parent)
		self.lastMousePos = wx.Point(0, 0)
		self.SetBackgroundColour('black')
		self.ToggleWindowStyle(wx.STAY_ON_TOP)
		
		global _clickenable
		if os.path.isfile('cfg'):
			with open('cfg') as f:
				thex = int(f.readline())
				they = int(f.next())
				_clickenable = int(f.next())
				print str(_clickenable)
			print "Window location: " + str(thex) + ", " + str(they)
			self.SetPosition((thex,they))

		self.SetTitle("Happy Egg Clock Widget")
		self.InitUI()
	
	def OnFrame1Motion(self, event):
		global _clickenable
		if event.LeftIsDown() and _clickenable > 0:
			windowX = self.lastMousePos[0]
			windowY = self.lastMousePos[1]
			screenX = wx.GetMousePosition()[0]
			screenY = wx.GetMousePosition()[1]
			self.Move(wx.Point(screenX - windowX, screenY - windowY))
		event.Skip()
	
	def OnFrame1LeftDown(self, event):
		self.lastMousePos = event.GetPosition()
		event.Skip()
	
	def closeWindow(self, e):
		self.Destroy() # prevent memory leak
	
	def InitUI(self):
		self.text = wx.StaticText(self, label="Syncing...", style=wx.ALIGN_RIGHT)
		self.text.SetForegroundColour('cyan')
		font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
		self.text.SetFont(font)
		self.compareTime = time.strftime('%H:%M:%S') # set time at execution for sync
		global temperature
		temperature = get_temp()
		self.SyncTime()

	def SyncTime(self):
		curtime = time.strftime('%H:%M')
		if curtime == self.compareTime:
			wx.CallLater(1, self.SyncTime)
		else:
			self.AutoUpdateTime()
		
	def AutoUpdateTime(self):
		hour = int(time.strftime('%H'))
		ampm = "" # fallback
		if hour % 12 < 1:
			if hour // 12 > 1:
				ampm = "am"
			else:
				ampm = "pm"
			hour = 12
		else:
			if hour // 12 > 0:
				ampm = "pm"
			else:
				ampm = "am"
			hour %= 12
		curtime = time.strftime(':%M:%S')
		#thetime = str(hour)+curtime+ampm
		thetime = str(hour)+curtime
		
		global temperature
		global temprun
		if curtime == ":10:00":
			if temprun < 1:
				print "Updating temperature..."
				temperature = get_temp()
				temprun = 1
		elif temprun > 0:
			temprun = 0
		self.text.SetLabel(str(temperature) + "C " + thetime)
		self.ToggleWindowStyle(wx.STAY_ON_TOP)
		wx.CallLater(500, self.AutoUpdateTime)
		

		
class TrayIcon(wx.TaskBarIcon):
	def __init__(self):
		super(TrayIcon, self).__init__()
		self.set_icon(TRAY_ICON)
	# figure out why this has to be done this way cause wtf why not just construct it
	def set_icon(self, path):
		icon = wx.IconFromBitmap(wx.Bitmap(path))
		self.SetIcon(icon, TRAY_TOOLTIP)
	
	def create_menu_item(self, menu, label, func):
		item = wx.MenuItem(menu, -1, label)
		menu.Bind(wx.EVT_MENU, func, id=item.GetId())
		menu.AppendItem(item)
		return item

	def create_menu_check_item(self, menu, label, func):
		item = menu.Append(wx.ID_ABOUT, label, kind=wx.ITEM_CHECK)
		menu.Bind(wx.EVT_MENU, func, id=item.GetId())
		return item
	
	def CreatePopupMenu(self):
		menu = wx.Menu()
		self.tester = self.create_menu_check_item(menu, "Click enabled", self.options_menu)
		self.ontop = self.create_menu_item(menu, "Always on top", self.ontopfunc)
		menu.AppendSeparator()
		self.create_menu_item(menu, "Frig off", self.frig_off)
		self.tester.Check(_clickenable)
		return menu
		
	def frig_off(self, event):
		global _clickenable
		curx, cury = frame.GetPosition()
		f = open('cfg', 'w')
		f.write(str(curx))
		f.write("\n")
		f.write(str(cury))
		f.write("\n")
		f.write(str(_clickenable))
		f.close()
		wx.CallAfter(exit()) # currently giving traceback error, figure this out
	
	def ontopfunc(self, event):
		frame.Raise()
		frame.ToggleWindowStyle(wx.STAY_ON_TOP)
	
	def options_menu(self, event):
		global _clickenable
		print str(_clickenable)
		if _clickenable:
			_clickenable = 0
		else:
			_clickenable = 1
		
if __name__ == "__main__":
	app = wx.App()
	frame = create(None)
	frame.Show()
	TrayIcon()
	app.MainLoop()

'''
	create multiple tray icons for different states
'''