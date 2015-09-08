from tkinter import *
import tkinter.simpledialog as simpledialog
from PIL import Image, ImageTk
import re
import os
import shutil
import sys, getopt
from autocomplete import AutocompleteDialog

# The order that keys are bound.
bindKeys = [
  "a",
  ";",
  "s",
  "l",
  "d",
  "k",
  "f",
  "j",
  "g",
  "h",
  "q",
  "w",
  "e",
  "r",
  "t",
  "u",
  "i",
  "o",
  "v",
  "c",
  "n",
  "m",
  "b",
  "x",
  ",",
  "z",
  "p",
  "y"
]

destinationDir = "D:/Images/Wallpapers"
destinationDir = os.path.normpath(destinationDir)

sourceDir = "D:/Torrent/BitTorrent Sync/Huge Anime Wallpaper Collection/Pictures/Wallpaper Cycle"
sourceDir = os.path.normpath(sourceDir)

processedDir = sourceDir + os.sep + "Processed"

locationFilePath = sourceDir + os.sep + "location.txt"

def main(argv):
  try:
    opts, args = getopt.getopt(argv, "d:s:p:l:vkh",
      ["dest=","source=","processed=", "locFile=", "verbose", "keepSkipped", "help"])
  except getopt.GetoptError as err:
    print(err)
    sys.exit(2)
  global destinationDir, sourceDir, processedDir, locationFilePath
  global destDirs, sourceFiles
  global index, current
  global debug, keepSkipped

  debug = False
  keepSkipped = False

  for opt, arg in opts:
    if opt in ("-h", "--help"):
      print(helpMessage)
      sys.exit(1)
    if opt in ("-d", "--dest"):
      destinationDir = arg
    if opt in ("-s", "--source"):
      sourceDir = arg
    if opt in ("-p", "--processed"):
      processedDir = arg
    if opt in ("-l", "--locFile"):
      locFile = arg
    if opt in ("-v", "--verbose"):
      debug = True
    if opt in ("-k", "--keepSkipped"):
      keepSkipped = True

  if not os.path.isdir(processedDir):
    os.makedirs(processedDir)

  if not os.path.isdir(sourceDir):
    print("Passed source directory does not exist")
    sys.exit(2)

  if not os.path.isdir(processedDir):
    os.mkdir(processedDir);

  destDirs = os.listdir(destinationDir)
  sourceFiles = os.listdir(sourceDir)
  index = -1

  if os.path.isfile(locationFilePath):
    with open(locationFilePath, "r") as f:
      current = f.readline()
      if current in sourceFiles:
        index = sourceFiles.index(current) - 1
        print("Found file in index " + str(index))
      else:
        print("No index found")


  nextImage()
  root.mainloop()

# Process a file.
# If dir is set move it to that directory (relative path).
# If it isn't set move it to the processed images dir.
def processFile(newName, dir=False):
  if not dir:
    if not keepSkipped:
      fromPath = sourceDir + os.sep + sourceFiles[index]
      toPath = processedDir + os.sep + sourceFiles[index]
    else:
      return
  else:
    fromPath = sourceDir + os.sep + sourceFiles[index]
    toPath = destinationDir + os.sep + dir + os.sep + newName
  if debug:
    print("From: " + fromPath)
    print("To: " + toPath)
  os.rename(fromPath, toPath)

def fuzzySearch(query, strings):
  matches = []
  query = ".*?".join(query)
  for string in strings:
    match = re.search(query, string)
    if match:
      matches.append(match)
  matches.sort(key=lambda m: m.span()[1] - m.span()[0])
  return matches



def closeProgram():
  with open(locationFilePath, "w") as f:
    f.write(sourceFiles[index])
  root.destroy()

def passWidget(func):
  return lambda event: func(event.widget)

root = Tk()
# Make sure that when you close the program we save where we were
root.protocol("WM_DELETE_WINDOW", closeProgram)

imgBut = Button(root)

# Goes to the next image
def skipProcessing(widget=None):
  processFile(sourceFiles[index])
  if widget:
    widget.destroy()
  nextImage()

def getFName(dir):
  fName = simpledialog.askstring("File Name", "What should it be named?")
  if fName:
    fName += os.path.splitext(sourceFiles[index])[1]
  else:
    fName = sourceFiles[index]
  processFile(fName, dir)
  nextImage()

def chooseDir(event=None):
  def matches(query, entry):
    pattern = re.compile(".*?".join(re.escape(query)), re.IGNORECASE)
    return re.search(pattern, entry)
  newDir = AutocompleteDialog.get_string(destDirs, master=root, title="What is the name of the directory?", matchesFunction=matches)
  if newDir:
    getFName(newDir)
  else:
    skipProcessing()

def processImage(event=None):
  global top
  top = Toplevel()
  top.title("Choose what to do with this")
  optionButtons = []
  # Add buttons and keybinds for each option
  # Cancel
  top.bind("<Escape>", passWidget(skipProcessing))
  optionButtons.append(Button(top, text="Skip (Esc)", command=skipProcessing))
  # New Folder
  top.bind("<Return>", createNewDir)
  optionButtons.append(Button(top, text="New (Enter)", command=createNewDir))
  # Image Folders
  for dirInd, dir in enumerate(destDirs):
    if dirInd < len(bindKeys):
      bindChar = bindKeys[dirInd]
      top.bind(bindChar, lambda event: getFName(dir))
    else:
      bindChar = "NONE"
    optionButtons.append(Button(top, text=dir + " (" + bindChar + ")", command=lambda: getFName(dir)))


  for button in optionButtons:
    button.pack()
  top.focus_set()
  # Center the window
  top.update_idletasks()
  width = top.winfo_width()
  height = top.winfo_height()
  x = (top.winfo_screenwidth() // 2) - (width // 2)
  y = (top.winfo_screenheight() // 2) - (height // 2)
  top.geometry('{}x{}+{}+{}'.format(width, height, x,y))



def nextImage():
  global index
  global imgBut
  global root
  global sourceFiles
  index += 1
  # If we went through the entire directory, say that we're done
  if index >= len(sourceFiles):
    top = Toplevel()
    doneBut = Button(top, text="Done", command=closeProgram)
    top.protocol("WM_DELETE_WINDOW", closeProgram)

  # If it is a directory, don't even try to open it as an image, just skip it
  if os.path.isdir(sourceFiles[index]):
    if debug:
      print("Skipping directory " + sourceFiles[index])
    nextImage()

  # Try opening the file. If it isn't an image, move onto the next file
  try:
    imgObj = Image.open(sourceDir + os.sep + sourceFiles[index])
  except IOError as err:
    print(err)
    nextImage()
  except OSError as err:
    print(err)
    nextImage()

  img = ImageTk.PhotoImage(imgObj)
  imgBut.destroy()
  imgBut = Button(root, image=img, command=processImage)
  imgBut.image = img
  root.bind("<Escape>", lambda event: closeProgram())
  root.bind("<space>", chooseDir)
  root.bind("<Return>", chooseDir)
  root.bind("n", lambda event: skipProcessing())
  imgBut.pack()
  root.focus_set()

# Make a new folder to put an image into
def createNewDir(event=None):
  newDir = simpledialog.askstring("New Directory", "What should it be named?")
  if newDir not in destDirs:
    destDirs.append(newDir)
  getFName(newDir)

helpMessage = """
A tool to make sorting images into subfolders easier. 
Goes through a directory, showing you each image and letting you easily move it to different folders and rename it.

Arguments:
  d, dest: The folder where all the subfolders are stored
  s, source: The folder where the images to be sorted are stored
  p, processed: Where to put skipped images. Does nothing if -k is passed
  l, locFile: Where to find/put the file that keeps track of which images have been processed
  k, keepSkipped: Flag to not move skipped images to the "Processed" folder
  v, verbose: Turns on some debug messages
  h, help: Prints a help message. You know this though, since you're reading it.


"""
if __name__ == "__main__":
  main(sys.argv[1:])
