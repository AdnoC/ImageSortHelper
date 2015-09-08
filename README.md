A tool to make it easier to sort a bunch of images in a folder into subfolders.
This was a quick and dirty project to try out tkinter.

It goes through all the images in a specified folder. You then choose what folder to move them to and what to call them. If you don't want to sort an image, it puts it into a Processed folder without changing the name. It keeps track of which images you went through so you can stop midway and continue later.
You can prevent it from moving skipped folders by passing the -k argument.

You can use either mouse or keyboard controls (although you would obviously need the keyboard to name images or new folders).
Clicking the image brings the menu for mouse controls.
When looking at an image pressing...
- Escape: Closes the program.
- Space: Open the directory choosing dialog.
- Enter: Open the directory choosing dialog.
- n: Skip this image.
The directory choosing dialog with the keyboard opens a dialog with fuzzy autocomplete of all existing directories in the destination folder.
Pressing escape in dialogs closes them and either skips the image (if choosing directory) or doesn't change the name (if naming the file).
There are keyboard shortcuts when choosing a directory with the mouse.
