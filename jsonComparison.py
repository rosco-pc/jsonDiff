class Comparison:
  def __init__(self, index=0):
    self.tabIndex = index                             # Save tab index (not used at the moment)
    self.jsonPath = {'1': None, '2': None}            # Initialize json file path
    self.jsonData = {'1': None, '2': None}            # Initialize json data
    self.jsonView = {'1': None, '2': None}            # Initialize TreeView
    self.mismatch = {}                                # Initialize mismatch dict
    self.mismatchIndex = None                         # Initialize index into mismatch dict
    self.maxIndex = 0                                 # Initialize max index of mismatch dict
    self.search = {'1': [], '2': []}                  # Initialize search dict
    self.searchIndex = {'1': -1, '2': -1}             # Initialize serach dict index
      
  def compare(self):
    """ Compare 2 json data structures
    
        Both way comparison
    """
    self.mismatch = collections.OrderedDict()
    self.jsonDiff(self.jsonData['1'], self.jsonData['2'], f='1')
    self.jsonDiff(self.jsonData['2'], self.jsonData['1'], f='2')
    self.Index = list(self.mismatch)
    self.maxIndex = len(self.Index) - 1 if self.Index else 0
    
  def getMismatch(self):
    if not self.maxIndex:
      msg = 'The files are the same'
    elif self.mismatchIndex is None:
      msg = 'Found {} mismatches'.format(self.maxIndex+1)
    else:
      mismatch = self.Index[self.mismatchIndex]
      msg = self.mismatch[mismatch]['error']
    return msg 

  def firstMismatch(self):
    self.mismatchIndex = 0
    if not self.maxIndex:
      return
    mismatch = self.Index[self.mismatchIndex]
    return self.mismatch[mismatch]

    
  def lastMismatch(self):
    self.mismatchIndex =  self.maxIndex
    if not self.maxIndex:
      return
    mismatch = self.Index[self.mismatchIndex]
    return self.mismatch[mismatch]
    
  def nextMismatch(self):
    if not self.maxIndex:
      return
    if self.mismatchIndex is None:
      self.mismatchIndex = 0
    elif self.mismatchIndex < self.maxIndex:
      self.mismatchIndex += 1
    mismatch = self.Index[self.mismatchIndex]
    return self.mismatch[mismatch]
    
  def prevMismatch(self):
    if not self.maxIndex:
      return
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
  
if __name__=='__main__':
  print('to be imported')  
