"""
Initially from https://gist.github.com/uroshekic/11078820
"""
from tkinter import *
import re

class AutocompleteDialog(Toplevel):
  @staticmethod
  def get_string(autocompleteList, master=None, title="Autocomplete", matchesFunction=None):
    if not master:
      master = Tk()
    diag = AutocompleteDialog(master, autocompleteList, title=title, matchesFunction=matchesFunction)
    return diag.result

  def __init__(self, parent, autocompleteList, matchesFunction=None, title=None):
    Toplevel.__init__(self, parent)
    self.transient(parent)

    self.autocompleteList = autocompleteList
    self.matchesFunction = matchesFunction
    if title:
      self.title(title)
    self.parent = parent
    self.result = None

    body = Frame(self)
    self.initial_focus = self.body(body)
    body.pack()


    width = body.winfo_width()
    height = 22#self.ent.winfo_height()
    x = (self.winfo_screenwidth() // 2) - (width // 2)
    y = (self.winfo_screenheight() // 2) - (height // 2)
    self.geometry('{}x{}+{}+{}'.format(width, height, x,y))

    self.grab_set()
    if not self.initial_focus:
      self.initial_focus = self

    self.protocol("WM_DELETE_WINDOW", self.cancel)

    self.initial_focus.focus_set()

    self.wait_window(self)

  def body(self, master):
    self.ent = AutocompleteEntry(self.autocompleteList, self, matchesFunction=self.matchesFunction)
    self.ent.pack()
    return self.ent

  def ok(self, event=None):
    self.withdraw()
    self.update_idletasks()
    self.apply()
    self.cancel()

  def cancel(self, event=None):
    self.parent.focus_set()
    self.destroy()

  def apply(self):
    self.result = self.ent.get()

class AutocompleteEntry(Entry):
    def __init__(self, autocompleteList, *args, **kwargs):
        self.listboxUp = False

        # Listbox length
        if 'listboxLength' in kwargs:
            self.listboxLength = kwargs['listboxLength']
            del kwargs['listboxLength']
        else:
            self.listboxLength = 8

        # Custom matches function
        if 'matchesFunction' in kwargs:
            self.matchesFunction = kwargs['matchesFunction']
            del kwargs['matchesFunction']
        else:
            def matches(fieldValue, acListEntry):
                pattern = re.compile('.*' + re.escape(fieldValue) + '.*', re.IGNORECASE)
                return re.match(pattern, acListEntry)

            self.matchesFunction = matches


        Entry.__init__(self, *args, **kwargs)
        self.focus()

        self.autocompleteList = autocompleteList

        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = StringVar()

        self.var.trace('w', self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Up>", self.moveUp)
        self.bind("<Down>", self.moveDown)
        self.bind("<Return>", self.selection)
        self.bind("<Escape>", self.master.cancel)
        self.bind("<Tab>", self.tabPress)
        self.bind("<Shift-Tab>", self.shiftTabPress)


    def changed(self, name, index, mode):
        if self.var.get() == '':
            if self.listboxUp:
                self.listbox.destroy()
                self.listboxUp = False
        else:
            words = self.comparison()
            if words:
                if not self.listboxUp:
                    self.listbox = Listbox(self.winfo_toplevel(),width=self["width"], height=self.listboxLength)
                    self.listbox.bind("<Button-1>", self.selection)
                    self.listbox.bind("<Right>", self.selection)
                    self.listbox.place(in_=self,relx=0, rely=1, bordermode="ignore")
                    self.listbox.update_idletasks()
                    height = self.listbox.winfo_y() + self.listbox.winfo_height()
                    self.winfo_toplevel().geometry("{}x{}".format(self.winfo_width(), height))
                    self.listboxUp = True

                self.listbox.delete(0, END)
                for w in words:
                    self.listbox.insert(END,w)
            else:
                if self.listboxUp:
                    self.listbox.destroy()
                    self.listboxUp = False

    def selection(self, event):
        if self.listboxUp:
            self.var.set(self.listbox.get(ACTIVE))
            self.listbox.destroy()
            self.listboxUp = False
            self.icursor(END)
        self.master.ok()

    def tabPress(self, event):
        self.moveDown(event)
        return 'break' # Interrupts default behavior (shifting focus)

    def shiftTabPress(self, event):
        self.moveUp(event)
        return 'break' # Interrupts default behavior (shifting focus)

    def moveUp(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = len(self.words)
            else:
                index = self.listbox.curselection()[0]

            if index != '0':
                self.listbox.selection_clear(first=index)
                index = str(int(index) - 1)

                self.listbox.see(index) # Scroll!
                self.listbox.selection_set(first=index)
                self.listbox.activate(index)

    def moveDown(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = '-1'
            else:
                index = self.listbox.curselection()[0]

            if index != END:
                self.listbox.selection_clear(first=index)
                index = str(int(index) + 1)

                self.listbox.see(index) # Scroll!
                self.listbox.selection_set(first=index)
                self.listbox.activate(index)

    def comparison(self):
        matches = []
        for w in self.autocompleteList:
          match = self.matchesFunction(self.var.get(), w)
          if match:
            matches.append(match)
        matches.sort(key=lambda m: m.span()[1] - m.span()[0])
        words = [w.string for w in matches]
        self.words = words
        return words
