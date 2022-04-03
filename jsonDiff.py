#!/usr/bin/env python3

import os
import sys
import json
import argparse
import collections

cli = False
try:
  import tkinter as tk
  import tkinter.ttk as ttk
  from tkinter import filedialog as fd

  TK_VERSION = tk.TkVersion
  if TK_VERSION < 8.6:
    from PIL import ImageTk, Image
  PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
  RSC_PATH = os.path.join(PROJECT_PATH, 'resource')
  USER_PATH = os.path.expanduser("~")
except ImportError:
    cli = True


class Comparison:
  def __init__(self, index=0):
    self.tabIndex = index
    self.jsonPath = {'1': None, '2': None}
    self.jsonData = {'1': None, '2': None}
    self.jsonView = {'1': None, '2': None}
    self.mismatch = collections.OrderedDict()
    self.mismatchIndex = None
    self.search = {'1': [], '2': []}
    self.searchIndex = {'1': -1, '2': -1}
      
  def compare(self):
    self.mismatch = collections.OrderedDict()
    self.jsonDiff(self.jsonData['1'], self.jsonData['2'], f='1')
    self.jsonDiff(self.jsonData['2'], self.jsonData['1'], f='2')
    self.Index = list(self.mismatch)
    self.maxIndex = len(self.Index) - 1 if self.Index else 0
    
  def getMismatch(self):
    if not self.maxIndex:
      msg = 'The fiels are the same'
    elif self.mismatchIndex is None:
      msg = 'Found {} mismatches'.format(self.maxIndex+1)
    else:
      mismatch = self.Index[self.mismatchIndex]
      msg = self.mismatch[mismatch]['error']
    return msg 

  def firstMismatch(self):
    self.mismatchIndex = 0
    mismatch = self.Index[self.mismatchIndex]
    return self.mismatch[mismatch]
    
  def lastMismatch(self):
    self.mismatchIndex =  self.maxIndex
    mismatch = self.Index[self.mismatchIndex]
    return self.mismatch[mismatch]
    
  def nextMismatch(self):
    if self.mismatchIndex is None:
      self.mismatchIndex = 0
    elif self.mismatchIndex < self.maxIndex:
      self.mismatchIndex += 1
    mismatch = self.Index[self.mismatchIndex]
    return self.mismatch[mismatch]
    
  def prevMismatch(self):
    if self.mismatchIndex is None:
      self.mismatchIndex = self.maxIndex
    elif self.mismatchIndex > 0:
      self.mismatchIndex -= 1
    mismatch = self.Index[self.mismatchIndex]
    return self.mismatch[mismatch]
    
  def jsonDiff(self, obj1, obj2, path='$', f=''):
    if obj1 == obj2:                                            # the same
      return                                                    # no need to continue
    oType1 = type(obj1)                                         # get object1 type
    oType2 = type(obj2)                                         # get object1 type
    if oType1 != oType2:                                        # different type
      if not path in self.mismatch:                             # mismatch already seen?
        # nope: save the mismatch
        error = ' Mismatch: {} different types'.format(path) 
        self.mismatch[path] = {'error':error, 'node': []}
      return                                                    # no need to continue
    if oType1 in (dict,):                                       # start comparing object contents
      for prop in obj1:                                         # 1 key/property at a time
        propPath = '{}.{}'.format(path, prop)                   # create 'path' name
        propType = type(obj1[prop])                             # determine the type
        if prop in obj2:                                        # check if it is available in object2
          if obj1[prop] != obj2[prop]:                          # check if it is not the same
            if propType in (dict, list):                        # yes, go deeper if needed for additional object or list
              self.jsonDiff(obj1[prop], obj2[prop], path=propPath, f=f)
            else:                                               # for 'normal' properties print mismatch message
              if propPath not in self.mismatch:                 # check if mismatch already seen
                # nope: save the mismatch
                error = ' Mismatch: {} - {} != {}'.format(propPath, obj1[prop], obj2[prop])
                self.mismatch[propPath] = {'error':error, 'node': []}
        else:                                                   # property missing
          error = ' Missing property:  file{} {}: {}'.format(f, propPath, prop)
          self.mismatch[propPath] = {'error':error, 'node': []}
    elif oType1 in (list,):                                     # start comparing list contents
      for idx, prop in enumerate(obj1):                         # 1 element at a time
        propPath = '{}[{}]'.format(path, idx)                   # indicate list index
        propType = type(prop)                                   # get element type
        try:
          if obj2[idx] != prop:                                 # check if not the same
            if propType in (dict, list):                        # yes, go deeper if needed for additional object or list
              self.jsonDiff(prop, obj2[idx], path=propPath, f=f)
            else:                                               # for 'normal' properties print mismatch message
              if propPath not in self.mismatch:                 # check if mismatch already seen
                # nope, save and print message
                error = ' Mismatch: {} - {} != {}'.format(propPath, prop, obj2[idx])
                self.mismatch[propPath] = {'error':error, 'node': []}
        except IndexError:
          error = ' Missing list element: file{} {} - {}'.format(f,propPath, prop)
          self.mismatch[propPath] = {'error':error, 'node': []}
    else:                                                          # for 'normal' properties print mismatch message
      if path not in mismatch:
        error = ' Mismatch: {} - {} != {}'.format(path, obj1, obj2)
        self.mismatch[path] = {'error':error, 'node': []}
    return
  

class CustomNotebook(ttk.Notebook):
  """ A ttk Notebook with close buttons on each tab
      from https://stackoverflow.com/questions/39458337/is-there-a-way-to-add-close-buttons-to-tabs-in-tkinter-ttk-notebook
  """

  __initialized = False

  def __init__(self, *args, **kwargs):
    if not self.__initialized:
      self.__initialize_custom_style()
      self.__inititialized = True

    kwargs["style"] = "CustomNotebook"
    ttk.Notebook.__init__(self, *args, **kwargs)

    self._active = None

    self.bind("<ButtonPress-1>", self.on_close_press, True)
    self.bind("<ButtonRelease-1>", self.on_close_release)

  def on_close_press(self, event):
    """Called when the button is pressed over the close button"""

    element = self.identify(event.x, event.y)

    if "close" in element:
      self.state(['pressed'])
      self._active = self.index("@%d,%d" % (event.x, event.y))
      return "break"

  def on_close_release(self, event):
    """Called when the button is released"""
    if not self.instate(['pressed']):
      return

    element =  self.identify(event.x, event.y)
    if "close" not in element:
      # user moved the mouse off of the close button
      return

    index = self.index("@%d,%d" % (event.x, event.y))
    print('Closing tab: {}'.format(index))
    if index==0:                                            # Never close the newDiff tab
      self.hide(index)
    elif self._active == index:
      self.forget(index)
    # Need to indicate the index of the closed tab, so comparision data 
    # can be removed. Overwrite x value to do this
    self.event_generate("<<NotebookTabClosed>>", x=index) 
    self.state(["!pressed"])
    self._active = None

  def __initialize_custom_style(self):
    style = ttk.Style()
    self.images = (
      tk.PhotoImage("img_close", data='''
          R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
          d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
          5kEJADs=
          '''),
      tk.PhotoImage("img_closeactive", data='''
          R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
          d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
          5kEJADs=
          '''),
      # tk.PhotoImage("img_closeactive", data='''
          # R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
          # AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
          # '''),
      tk.PhotoImage("img_closepressed", data='''
          R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
          d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
          5kEJADs=
      ''')
    )

    style.element_create("close", "image", "img_close",
                        ("active", "pressed", "!disabled", "img_closepressed"),
                        ("active", "!disabled", "img_closeactive"), border=8, sticky='')
    style.layout("CustomNotebook", [("CustomNotebook.client", {"sticky": "nswe"})])
    style.layout("CustomNotebook.Tab", [
            ("CustomNotebook.tab", {
               "sticky": "nswe",
               "children": [
                 ("CustomNotebook.padding", {
                   "side": "top",
                   "sticky": "nswe",
                   "children": [
                     ("CustomNotebook.focus", {
                       "side": "top",
                       "sticky": "nswe",
                       "children": [
                         ("CustomNotebook.label", {"side": "left", "sticky": ''}),
                         ("CustomNotebook.close", {"side": "left", "sticky": ''}),
                       ]
                     })
                   ]
                 })
               ]
             })
           ])


class jsonDiffApp:
  json_conv = { None: 'null',
                True: 'true',
                False: 'false'
              }
  comparison = [None]                     # Open comparison records, None for newDiff tab
                                          # Intention is to sync this to the tabs indexes
                                          
  newDiffTab = 0                          # 
  jsonPath = {'1': None, '2': None}
  
  def __init__(self, args, master=None, path=USER_PATH):
    self.mainwindow = tk.Tk() if master is None else tk.Toplevel(master)
    self.userPath = path
    self. buildUI()
    # newDiff tab is shown at start
    self.newComparison()
    if args.jsonFile1 is not None:
      self.loadJson(args.jsonFile1, '1')
    if args.jsonFile2 is not None:
      self.loadJson(args.jsonFile2, '2')
    self.enableCompare()
      
  def buildUI(self):
    def loadImage(path):
      if TK_VERSION < 8.6:
        return ImageTk.PhotoImage(Image.open(path))
      else:
        return tk.PhotoImage(file=path)
        
    # variable to interact with UI
    self.searchStr = tk.StringVar(value='')
    self.mismatchMsg = tk.StringVar(value='')
    self.jsonPath['1'] = tk.StringVar(value='')
    self.jsonPath['2'] = tk.StringVar(value='')
    
    # images
    self.refreshImg_24 = loadImage(os.path.join(RSC_PATH,'24x24/redo.png'))
    self.openImg_24 = loadImage(os.path.join(RSC_PATH,'24x24/file-import.png'))
    self.searchImg_24 = loadImage(os.path.join(RSC_PATH,'24x24/search.png'))
    self.nextImg_24 = loadImage(os.path.join(RSC_PATH,'24x24/angle_right.png'))
    self.prevImg_24 = loadImage(os.path.join(RSC_PATH,'24x24/angle_left.png'))
    self.openImg = loadImage(os.path.join(RSC_PATH,'48x48/folder-open.png'))
    #self.closeImg = loadImageos.path.join(RSC_PATH,'48x48/close.png'))
    self.exitImg = loadImage(os.path.join(RSC_PATH,'48x48/close.png'))
    self.firstImg = loadImage(os.path.join(RSC_PATH,'48x48/angle-double-up.png'))
    self.lastImg = loadImage(os.path.join(RSC_PATH,'48x48/angle-double-down.png'))
    self.nextImg = loadImage(os.path.join(RSC_PATH,'48x48/angle-down.png'))
    self.prevImg = loadImage(os.path.join(RSC_PATH,'48x48/angle-up.png'))

    # build ui
    self.main = ttk.Frame(self.mainwindow)
    # Customize TreeView colors
    style = ttk.Style()
    style.map('Treeview', background=[('selected', 'grey90')])
    style.map('Treeview', foreground=[('selected', 'black')])
    # Icon bar
    self.iconBar_UI()                                       
    # search bar
    #self.searchBar_UI()               # INTEGRATED WITH ICONBAR                      
    # noteBook
    self.notebook = CustomNotebook(self.main)               
    self.notebook.pack(expand=1, fill='both', side='top')
    # add tab to open new Diff
    self.notebook.add(self.newDiffFrame(), sticky='ns', text='New...')               # Add new diff frame to notebook
    self.notebook.bind('<<NotebookTabChanged>>', self.onTabChange)      # Capture when the tab changes, needed to update currentComparison
    self.notebook.bind('<<NotebookTabClosed>>', self.onTabClose)        # Capture when the tab closes, needed to remove old data from comparison
    
    self.main.pack(expand=1, fill='both', side='top')
    self.mainwindow.title('jsonDiff')
    self.mainwindow.iconphoto(False, loadImage(os.path.join(RSC_PATH,'jsonDiff.png')))
    self.mainwindow.configure(width='600', height='400')
    self.mainwindow.minsize(600, 400)

  def newDiffFrame(self):
    frame = ttk.Frame(self.notebook)
    # first row and last row with higher weight resulting in vertical centering
    empty1 = ttk.Label(frame)
    empty1.configure(text=' ')
    empty1.grid(column='0', row='0',columnspan='3')
    empty1.rowconfigure('0', weight='1')
    # row 1: jsonFile 1
    label1 = ttk.Label(frame)
    label1.configure(text='JSON File 1')
    label1.grid(column='0', row='1', padx='5', pady='2')
    entry1 = ttk.Entry(frame)
    entry1.configure(textvariable=self.jsonPath['1'])
    entry1.grid(column='1', row='1', padx='5', pady='2')
    selectJson1 = ttk.Button(frame)
    selectJson1.configure(text='...', width='3', 
                          command=lambda: self.selectFile('new_1'))
    selectJson1.grid(column='2', row='1', pady='2')
    #row 2: jsonFile 2
    label2 = ttk.Label(frame)
    label2.configure(text='JSON File 2')
    label2.grid(column='0', row='2', padx='5', pady='2')
    entry2 = ttk.Entry(frame)
    entry2.configure(textvariable=self.jsonPath['2'])
    entry2.grid(column='1', row='2', padx='5', pady='2')
    selectJson2 = ttk.Button(frame)
    selectJson2.configure(text='...', width='3', 
                          command=lambda: self.selectFile('new_2'))
    selectJson2.grid(column='2', row='2', pady='2')
    #row 3: start Comparison
    self.diffBtn = ttk.Button(frame)
    self.diffBtn.configure(state='disabled', text='Compare', command=self.jsonDiff)
    self.diffBtn.grid(column='0', row='3', columnspan='3', sticky='e')
    # first row and last row with higher weight resulting in vertical centering
    empty2 = ttk.Label(frame)
    empty2.configure(text=' ')
    empty2.grid(column='0', row='4',columnspan='3')
    empty2.rowconfigure('4', weight='1')
    frame.pack(side='top')      
    return frame  

  def diffFrame(self):
    mainFrame = ttk.Frame(self.notebook)
    panedWindow = ttk.Panedwindow(mainFrame, orient='horizontal')
    
    # JSON file 1
    # container for title bar and json treeView
    pane1 = ttk.Frame(panedWindow)                              
    # title bar
    titleBar1 = ttk.Frame(pane1)
    newBtn1 = ttk.Button(titleBar1)                            # open new file
    newBtn1.configure(image=self.openImg_24, style='Toolbutton')
    newBtn1.pack(side='left')
    newBtn1.configure(command=lambda: self.selectFile('open_1'))
    refreshBtn1 = ttk.Button(titleBar1)                        # reload existing file
    refreshBtn1.configure(image=self.refreshImg_24, style='Toolbutton')
    refreshBtn1.pack(side='left')
    refreshBtn1.configure(command=lambda: self.reloadFile('1'))
    jsonFile1 = ttk.Label(titleBar1)                           # json file name
    jsonFile1.configure(text=self.currentComparison.jsonPath['1'])
    jsonFile1.pack(padx='5', side='left')
    titleBar1.configure(height='20', width='200')
    titleBar1.pack(fill='x', side='top')
    # json treeView
    self.currentComparison.jsonView['1'] = ttk.Treeview(pane1,style="selection.Treeview")                   #
    self.currentComparison.jsonView['1'].pack(expand=1, fill='both', side='top')
    self.currentComparison.jsonView['1'].configure(show='tree')
    pane1.configure(height='200', width='200')
    pane1.pack(expand=1, fill='both',side='top')
    panedWindow.add(pane1, weight='1')
    
    # JSON file 2
    # container for title bar and json treeView
    pane2 = ttk.Frame(panedWindow)                              
    # title bar
    titleBar2 = ttk.Frame(pane2)
    newBtn2 = ttk.Button(titleBar2)                            # open new file
    newBtn2.configure(image=self.openImg_24, style='Toolbutton')
    newBtn2.pack(side='left')
    newBtn2.configure(command=lambda: self.selectFile('open_2'))
    refreshBtn2 = ttk.Button(titleBar2)                        # reload existing file
    refreshBtn2.configure(image=self.refreshImg_24, style='Toolbutton')
    refreshBtn2.pack(side='left')
    refreshBtn2.configure(command=lambda: self.reloadFile('2'))
    jsonFile2 = ttk.Label(titleBar2)                           # json file name
    jsonFile2.configure(text=self.currentComparison.jsonPath['2'])
    jsonFile2.pack(padx='5', side='left')
    titleBar2.configure(height='20', width='200')
    titleBar2.pack(fill='x', side='top')
    # json treeView
    self.currentComparison.jsonView['2'] = ttk.Treeview(pane2)
    self.currentComparison.jsonView['2'].pack(expand=1, fill='both', side='top')
    self.currentComparison.jsonView['2'].configure(show='tree')
    pane2.configure(height='200', width='200')
    pane2.pack(expand=1, fill='both',side='top')
    panedWindow.add(pane2, weight='1')
    panedWindow.pack(expand=1, fill='both', side='top')
    # mismatch message
    statusBar = ttk.Frame(mainFrame)
    msg = ttk.Entry(statusBar)
    msg.configure(state='readonly', textvariable=self.mismatchMsg, validate='none')
    msg['state'] = 'normal'
    msg.pack(expand=1, fill='x', side='top')
    statusBar.configure(height='50', width='200')
    statusBar.pack(fill='x', side='top')
    mainFrame.configure(height='400', width='600')
    mainFrame.pack(expand=1, fill='both', side='top')
    return mainFrame
      
  def iconBar_UI(self):
    iconBar = ttk.Frame(self.main)
    newBtn = ttk.Button(iconBar)
    newBtn.configure(image=self.openImg, style='Toolbutton')
    newBtn.pack(pady='1', side='left')
    newBtn.configure(command=self.newDiff)
    # closeBtn = ttk.Button(iconBar)
    # closeBtn.configure(image=self.closeImg, style='Toolbutton')
    # closeBtn.pack(side='left')
    # closeBtn.configure(command=self.closeComparison)
    # refreshAll = ttk.Button(iconBar)
    # refreshAll.configure(image=self.refreshImg, style='Toolbutton')
    # refreshAll.pack(side='left')
    # refreshAll.configure(command=lambda: self.reload(None))
    exitBtn = ttk.Button(iconBar)
    exitBtn.configure(image=self.exitImg, style='Toolbutton')
    exitBtn.pack(side='left')
    exitBtn.configure(command=self.exitApp)
    separator = ttk.Separator(iconBar)
    separator.configure(orient='horizontal')
    separator.pack(fill='y', padx='7', pady='1', side='left')
    self.searchNextBtn = ttk.Button(iconBar)
    self.searchNextBtn.configure(image=self.nextImg_24, style='Toolbutton',
                                 state='disabled', command=self.searchNext)
    self.searchNextBtn.pack(padx='1', pady='1', side='right')
    self.searchPrevBtn = ttk.Button(iconBar)
    self.searchPrevBtn.configure(image=self.prevImg_24, style='Toolbutton',
                                 state='disabled', command=self.searchPrev)
    self.searchPrevBtn.pack(padx='1', pady='1', side='right')
    searchBtn = ttk.Button(iconBar)
    searchBtn.configure(image=self.searchImg_24, style='Toolbutton')
    searchBtn.pack(padx='1', pady='1', side='right')
    searchBtn.configure(command=self.searchProperty)
    searchEntry = ttk.Entry(iconBar)
    searchEntry.configure(textvariable=self.searchStr, validate='none')
    searchEntry.pack(pady='2', side='right')
    searchEntry.bind('<Return>', self.searchProperty)
    separator = ttk.Separator(iconBar)
    separator.configure(orient='horizontal')
    separator.pack(fill='y', padx='15', pady='1', side='right')
    lastBtn = ttk.Button(iconBar)
    lastBtn.configure(image=self.lastImg, style='Toolbutton')
    lastBtn.pack(side='left')
    lastBtn.configure(command=lambda: self.showMismatch('last'))
    nextBtn = ttk.Button(iconBar)
    nextBtn.configure(image=self.nextImg, style='Toolbutton')
    nextBtn.pack(side='left')
    nextBtn.configure(command=lambda: self.showMismatch('next'))
    prevBtn = ttk.Button(iconBar)
    prevBtn.configure(image=self.prevImg, style='Toolbutton')
    prevBtn.pack(side='left')
    prevBtn.configure(command=lambda: self.showMismatch('prev'))
    firstBtn = ttk.Button(iconBar)
    firstBtn.configure(image=self.firstImg, style='Toolbutton')
    firstBtn.pack(side='left')
    firstBtn.configure(command=lambda: self.showMismatch('first'))
    iconBar.configure(height='20', relief='flat', width='200')
    iconBar.pack(expand='false', fill='x', side='top')

  def searchBar_UI(self):
    searchBar = ttk.Frame(self.main)
    searchBtn = ttk.Button(searchBar)
    searchBtn.configure(image=self.searchImg_24, style='Toolbutton')
    searchBtn.pack(padx='1', pady='1', side='right')
    searchBtn.configure(command=self.searchProperty)
    searchEntry = ttk.Entry(searchBar)
    searchEntry.configure(show='•', textvariable=self.searchStr, validate='none')
    searchEntry.pack(pady='2', side='right')
    label = ttk.Label(searchBar)
    label.configure(text='Search text')
    label.pack(padx='2', side='right')
    searchBar.configure(height='20', relief='sunken')
    searchBar.pack(fill='x', side='top')
      
  def newComparison(self):
    index = len(self.comparison)
    self.comparison.append(Comparison(index))                   # Add new comparison
    self.currentComparison = self.comparison[-1]                # save it as the current comparison
    print("New Tab 0:{} - {}".format(self.currentComparison.tabIndex, 
                                     self.currentComparison.jsonPath))

  def onTabChange(self, event):                                 # Selected new tab
    index = self.notebook.index('current')                      # Get current tab index
    if index==self.newDiffTab:                                  # Do nothing when on newDiff Frame
      return
    self.currentComparison = self.comparison[index]             # set correct currentComparison for the tab
    self.mismatchMsg.set(self.currentComparison.getMismatch())
    print('Changed Tab {}:{} - {}'.format(index, self.comparison.index(self.currentComparison),
                                          self.currentComparison.jsonPath))
      
  def onTabClose(self, event):                                  # Closed tab
    """ tabs and compairson needs to be kept in sync
    """
    index = event.x
    if index ==0:
      popped = self.comparison.pop()                            # Remove comparison data
    else:
      popped = self.comparison.pop(index)                       # Remove comparison data

    print('Closed Tab {}:{} - {}'.format(index, popped.tabIndex, popped.jsonPath))
    self.currentComparison = None                               # 
    if len(self.comparison) == 1:                               # Closed all comparison tabs
      self.notebook.select(self.newDiffTab)                     # show newDiff Frame

  def newDiff(self):                                            # Show newDiff Frame
    self.newComparison()                                        # create new Comparison
    self.jsonPath['1'].set('')                                  # clear old file names
    self.jsonPath['2'].set('')                                  
    self.notebook.select(self.newDiffTab)                       # show newDiff tab
    self.diffBtn.configure(state='disabled')
    
  def reloadFile(self, jsonId):
    print('Reload File: {}'.format(jsonId))
    try:
      fn = self.currentComparison.jsonPath[jsonId]
      self.currentComparison.jsonData[jsonId] = json.load(open(fn)) # Load json data
      self.currentComparison.compare()
      self.updateView(self.notebook.index('current'))
    except json.decoder.JSONDecodeError as e:
      tk.messagebox.showwarning(title='Invalid JSON', message=e)
      return
    pass

  def exitApp(self):
    sys.exit(0)

  def showMismatch(self, action):
    msg = {'first': self.currentComparison.firstMismatch,
           'last': self.currentComparison.lastMismatch,
           'next': self.currentComparison.nextMismatch,
           'prev': self.currentComparison.prevMismatch}
           
    mismatch = msg[action]()
    node = mismatch['node']
    # Select path in jsonView1 and jsonView2
    for node in mismatch['node']:
      node[0].see(node[2])
      node[0].selection_set(node[2])
    self.mismatchMsg.set(mismatch['error'])
    
  def searchProperty(self, event=None):
    if not self.searchStr:
      return
    self.currentComparison.search = {'1':[], '2':[]}
    self.search(self.currentComparison.jsonView['1'],'1')
    self.search(self.currentComparison.jsonView['2'],'2')
    # (dis-)enable search next & prev buttons
    enabled = len(self.currentComparison.search['1']) > 1 or \
              len(self.currentComparison.search['2']) > 1
    self.searchNextBtn.configure(state='normal' if enabled else 'disabled')
    self.searchPrevBtn.configure(state='normal' if enabled else 'disabled')
    self.currentComparison.searchIndex = {'1':-1, '2':-1}
    self.searchNext()
    
  def search(self, tree, f):
    def get_all_children(tree, item=""):
      children = tree.get_children(item)
      for child in children:
        children += get_all_children(tree, child)
      return children

    for item_id in get_all_children(tree):
      tree.item(item_id, open=False)                              # Collapse tree view
      item_text = str(tree.item(item_id, 'text'))                 # get item text
      if self.searchStr.get().lower() in item_text.lower():       # matches search term?
        self.currentComparison.search[f].append((tree,item_id))   # Yes add the searchList

  def searchNext(self):
    for jsonId in self.currentComparison.search:
      l = len(self.currentComparison.search[jsonId])              # get search result length
      idx = (self.currentComparison.searchIndex[jsonId] + 1) % l  # wrap arounf searchIndex
      self.currentComparison.searchIndex[jsonId] = idx            # save latest searchIndex
      tree, item_id = self.currentComparison.search[jsonId][idx]  # show search result
      tree.see(item_id)
      tree.selection_set(item_id)
      
  def searchPrev(self):
    for jsonId in self.currentComparison.search:
      l = len(self.currentComparison.search[jsonId])              # get search result length
      idx = (self.currentComparison.searchIndex[jsonId] - 1) % l  # wrap arounf searchIndex
      self.currentComparison.searchIndex[jsonId] = idx            # save latest searchIndex
      tree, item_id = self.currentComparison.search[jsonId][idx]  # show search result
      tree.see(item_id)
      tree.selection_set(item_id)
      
  def selectFile(self, data):
    action, jsonId = data.split('_')                              # get action new/open
    fn = fd.askopenfilename(initialdir = self.userPath,           # show file dialog
                            title = "Select file",
                            filetypes = (("json files","*.json"),
                                         ("all files","*.*")))
    if fn is None:                                                # No file selected or Cancel pressed
      return                                                      # Do nothing
    self.userPath = os.path.dirname(fn)                           # save last used path
    print('Select File: {}'.format(fn))
    self.loadJson(fn, jsonId)                                     # Load json data

    if action == 'new':                                           # if new comparison
      self.enableCompare()                                        # Enable compare button when both files loaded
    else:                                                         # Update existing comparison
      self.currentComparison.compare()                            # Compare newly loaded file with old file
      self.updateView(self.notebook.index('current'))             # Show update comparison

  def loadJson(self, fn, jsonId):
    try:
      self.currentComparison.jsonData[jsonId] = json.load(open(fn)) # Load json data
      self.currentComparison.jsonPath[jsonId] = fn                # Save file name
      self.jsonPath[jsonId].set(fn)                               # Update TreeView title
    except json.decoder.JSONDecodeError as e:
      tk.messagebox.showwarning(title='Invalid JSON', message=e)
    return

  def enableCompare(self):
    """ Enable compare button if both files are loaded
    """
    if self.currentComparison.jsonData['1'] and \
       self.currentComparison.jsonData['2']:
      self.diffBtn.configure(state='normal')

  def jsonDiff(self):
    self.notebook.insert('end', self.diffFrame())
    tabIndex = self.notebook.index('end') - 1
    print('Current tab  {}:{}'.format(tabIndex, self.currentComparison.tabIndex))
    self.currentComparison.compare()
    self.updateView(tabIndex);
    self.notebook.hide(self.newDiffTab)
    self.notebook.select(tabIndex)

  def updateView(self, tabIndex):
    
    title = '{} - {}'.format(os.path.basename(self.currentComparison.jsonPath['1']),
                             os.path.basename(self.currentComparison.jsonPath['2']))
    self.notebook.tab(tabIndex, text=title)
    #Clear the treeview list items
    for item in self.currentComparison.jsonView['1'].get_children():
      self.currentComparison.jsonView['1'].delete(item)
    self.insertNodes(self.currentComparison.jsonView['1'], 
                     self.currentComparison.jsonData['1'], 
                     '1')
     #Clear the treeview list items
    for item in self.currentComparison.jsonView['2'].get_children():
      self.currentComparison.jsonView['2'].delete(item)
    self.insertNodes(self.currentComparison.jsonView['2'], 
                     self.currentComparison.jsonData['2'],
                     '2')
    msg = self.currentComparison.getMismatch()
    self.mismatchMsg.set(msg)

  def insertNodes(self, tree, data, f='1'):
    tree.tag_configure('mismatch', background='tan1')
    tree.tag_configure('missing', background='medium sea green')
    parent = ""
    if isinstance(data, list):
      for index, value in enumerate(data):
        path = '$[{}]'.format(index)
        self.insertNode(tree, parent, index, value, path, f)
    elif isinstance(data, dict):
      for (key, value) in data.items():
        path = '$.{}'.format(key)
        self.insertNode(tree, parent, key, value, path, f)
              
  def insertNode(self, tree, parent, key, value, path='$', f='1'):
    if path in self.currentComparison.mismatch:
      error = self.currentComparison.mismatch[path]['error'].split()[0]
      tags = ('missing' if error=='Missing' else 'mismatch')
      #print('Match: ',path, tags)
    else: 
      tags = ()
      
    if type(value) in (list, tuple):
      node = tree.insert(parent, 
                         'end', 
                         text='{} [{}]'.format(key, len(value)), 
                         tags=tags, 
                         open=False)
      for index, item in enumerate(value):    # list what is shown with [:MAX_N_SHOW_ITEM]
        self.insertNode(tree, node, index, item, '{}[{}]'.format(path,index), f)
    elif type(value) in (dict,):
      node = tree.insert(parent, 
                         'end', 
                         text='{} {{{}}}'.format(key, len(value)), 
                         tags=tags, 
                         open=False)
      for key, item in value.items():
        self.insertNode(tree, node, key, item, '{}.{}'.format(path, key), f)
    elif type(value) in (str,):
      node = tree.insert(parent, 
                         'end', 
                         text='{}: "{}"'.format(key, value), 
                         tags=tags, 
                         open=False)
    elif type(value) in (int,float):
      node = tree.insert(parent, 
                         'end', 
                         text='{}: {}'.format(key, value), 
                         tags=tags, 
                         open=False)
    else:
      node = tree.insert(parent, 
                         'end', 
                         text='{}: {}'.format(key, self.json_conv[value]),
                         tags=tags,
                         open=False)
    if tags:
      self.currentComparison.mismatch[path]['node'].append((tree, parent, node))
      print(f,node)

  def run(self):
      self.mainwindow.mainloop()


def main(args):
  comparison = Comparison()
  try:
    fn = args.jsonFile1
    print('Reading: {}'.format(fn))
    comparison.jsonData['1'] = json.load(open(fn))
  except FileNotFoundError:
    print('Can not find: {}'.format(sys.arg[v]))
    sys.exit(1)
  except json.decoder.JSONDecodeError as e:
    print('Invalid JSON: {}'.format(e))
    sys.exit(1)

  try:
    fn = args.jsonFile2
    print('Reading: {}'.format(fn))
    comparison.jsonData['2'] = json.load(open(fn))
  except FileNotFoundError:
    print('Can not find: {}'.format(sys.arg[v]))
    sys.exit(1)
  except json.decoder.JSONDecodeError as e:
    print('Invalid JSON: {}'.format(e))
    sys.exit(1)

  comparison.compare()
  for path in comparison.mismatch:
    print(comparison.mismatch[path]['error'])
  

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Show differences between 2 JSON files with GUI when available')
  parser.add_argument('jsonFile1', nargs='?', action='store', default=None, help='JSON input file 1')
  parser.add_argument('jsonFile2', nargs='?', action='store', default=None, help='JSON input file 2')
  parser.add_argument('--cli', action='store_true', help='force cli handling')  
  args = parser.parse_args()    
                  
  if cli or args.cli:
    if args.jsonFile1 is None or args.jsonFile2 is None:
      parser.print_usage()
      sys.exit(1)
    main(args)
  else:
    app = jsonDiffApp(args)
    app.run()

