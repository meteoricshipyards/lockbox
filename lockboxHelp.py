import tkinter as tk

global help_text

help_text = \
['Help for LockBox',
 [[ 'About','LockBox is a program for keeping track of your passwords.\
 Each password has a name, a description, a user ID, and the password, of course.\
 The information is stored in a file, with the password encrypted. \n\
 \nName - anything you want to call the password, for example \n \
     "Discover Card", "Facebook", "Home Router" \n \
 \nDescription - Further information on the password, for example, \n\
     the URL of the site, phone number for help line, etc.\
 \nUser ID - Your signon at the site.  Could be an email address, or an actual user name.\
 \nPassword - the actual password.\
 \n\nYou can export the password file to save it, or move it to another device.  If you do that, you can \
 merge password files.  See further help sections for more information on these actions.'
 ],
 ['The Key','The Key is the password used to ecrypt the passwords.  It is not stored in the file. It can be as long as you like with any characters you want to include.  It is case sensitive.  Leading and trailing spaces are removed, but internal spaces are not (so the spacing in the \
 initial set up of the key is what you use forever).\n\
  If you forget, it cannot be recovered.  \n\
  \nIf you care, the key is used as a key in an RC4 encryption algorithm.  '
 ],
 ['Menus (Actions)',
  [['Export','Saves the file to a location of your chosing.  The file can be backed up or moved to a new device '+\
   'to be merged with another copy of the program.'],
   ['Merge','Merges an exported file.  The names are used to determine if the entry exists already, and if it does, the newer (most recently changed)  data is used.  (IE, you update Super Villain Credit Card on system A, export the file, and merge it with the LockBox file on system B, if A\'s data is newer than that saved on system B, system B\'s data is thrown away, and only A\'s data is saved.)'],
   ['Save','Although your LockBox data is saved when you exit the program, you can manually save it at any time.'],
   ["View Password","That's what this is all about, isn't it?"],
   ['Edit','Edit the selected entry.  Remember, the "Name" is used as a key.  If you change the name, you can end up with two entries to the same site if you merge with other Lockboxes on different systems.'],
   ['Delete','Remove an entry.  There is no undelete (but you can Export and save the data, and merge it back later.)'],
   ['Change Password', 'Change the password used to encrypt the data file.  For security, you will be asked the (current) password.']
  ]
 ],
 ['Buttons',
  [['Add','Adds a new password record.  Pops up a box where you enter the name, description, user name, and password.\n'+\
     'This box is presented the first time you run the program for entering the first password record.'],
   ['Edit','Lets you edit a password record.'],
   ['View password',"Pops up a box with the record's password in clear text."],
   ['PW -> Clipboard',"Copies the password to the clipboard so you can just paste it where you want to use it."],
   ['Done','Save any changes, and exit the program.']
  ]   
 ],
 ['Error messages',
   '"Bad file - incorrect format" - The data file is expected to be a certain format.  The file did not have the correct number of data blocks.  It could be because the file is from an older version (none exist at the time of this writing, however), or the file is not a saved or exported file from the Lockbox program.\
   \n\n"Bad file, unreadable" - The Python programming language uses a standard format for saving binary (ie. computer readable) data.  The file given did not have the correct format.  It was not created by the Lockbox program.\
   \n\n"Cannot open file" - For some reason, the program could not open the file.  It could be an authority probrom.  This error does not refer to the contents of the file, only that the file itself could not be opened.\
   \n\n"The Following entry(ies) had problems decrypting the passwords(s)" - For some reason, the decryption of password for a site failed.  At this time, all I can do is report the incident.\
   '
  ], 
  ['A bit of History','When I started working on computers in the late 70\'s, we were told to "Never, ever, ever write your password down!" \n\nOf course, it was easy back then.  You only ever had 1 or two passwords, for work or school.\n\nThings are a little different today, and to say I may have 50 passwords is a good guess (although I know some are for websites that have gone away, so probably don\'t count).  So a new method of keeping track of passwords has been developed, the password manager.  \n\nMy password manager probably doesn\'t have all the bells and whistles others have.  But it has no malware, no ads, and if you are paranoid, you can look over the code yourself and see that it is clean.\n\nUse it in good health, and remember, it is free, and should not be sold.'
  ]
 ]
]

errorMessages = { 'LckB0001' : "Bad file {} - incorrect format",
                  'LckB0002' : "Bad file {}, unreadable",
                  'LckB0003' : "Cannot open file {}",
                  'LckB0004' : "The following entry(ies) had problems decrypting the password(s) {}" }


class HelpDialog(tk.Toplevel):
    """ 
    Help - put up a help screen.  Help is hierarchical.  Each level is a 2 tuple (of list).
           The first element is a string that is the section title, the second is either  
           a string, the help contents for this section, or a list of help topics (string, contents pairs)
           Further details as they are worked out.
    """
    def __init__(self,helpObj) :
        """ create window, title it.  Put up contents """
        tk.Toplevel.__init__(self, None)
        if self.checkInput(helpObj,0) == False :
            print('Bad help object, see previous output')
            return             
        self.stack = []
        self.title( "Help" )
        self.stack.append(helpObj)
        button = tk.Button(self,text = 'Done', command = self.done) 
        button.grid(row = 0, column = 0)
        
        self.displayContents()
  
    def checkInput(self,helpObj,lvl) :
        ret = True # assume it's good
        lev = lvl
        if len(helpObj) != 2 :
            """
            print(' '*lev, 'Help object length is != 2, type = ', str(type(helpObj)), ' len: ',len(helpObj) )
            
            if type(helpObj) == list :
                print(' '*lev,'types in help obj:')
                for i in helpObj:
                    if type(i) == str :
                        print(' '*lev,'Text:',  i )
                    else:
                        print(' '*lev,str(type(i)))
            """
            return False
        if type(helpObj[0]) != str :
            #print(' '*lev,'Title field not string: ', str(type(helpObj[0])) )
            ret = False
        #else:    
            #print(' '*lev,helpObj[0])
        
        lev = lev + 2
        if type(helpObj[1]) == str :
            #print(' '*lev ,'Contents is a string' )
            return ret
        else: 
            if type(helpObj[1]) != list :
                #print(' '*lev,'Contents is not a string or list')
                return False
            else:
                for i in helpObj[1] :
                    ret = ret and self.checkInput(i, lev )                
                return ret    
       


  
    def done(self) :
        #print('done :',repr(self.stack))
        _ = self.stack.pop()
        #print('done::',repr(self.stack))
        if len(self.stack) == 0 :
            # exiting top level, exit help
            self.destroy()
        else:
            try :
                self.text.config(state=tk.NORMAL)
                self.text.delete('1.0', tk.END)
                #print("Done -- clear ?")
            except Exception as e :
                #print("Done -- problem clearing text.  Error: ", repr(e))
                pass 
            try :    
                self.lb.delete(0,tk.END)
                #print("Done -- clear list ")
            except Exception as e :
                print("Help Done -- problem clearing list ", repr(e))
                
            self.displayContents()

    def displayContents(self) :
        cont = self.stack[-1] # top of stack (last element)
        if type(cont) == str :  # that mysterious string got on the stack
            #print("bad value on stack")
            _ = self.stack.pop()
            cont = self.stack[-1]
        #print("in displayContents",str(cont))
        self.title(cont[0])
        
        try :
             if type(cont[1]) == str : 
                 ok = True
        except IndexError as e :
             messagebox.showerror(title="index error", message=str(e)+'\n \n'+str(cont))
             #print("----------------")
             #print("Error " + str(e))
             #print("Cont = " + str(cont))
             #print("Stack = " + str(self.stack))
             #print("----------------")

        if type(cont[1]) == str : # simple case, just display it
            self.text = tk.Text(self, height=20, width = 80, wrap=tk.WORD )
            self.text.insert(tk.END, cont[1])
            self.text.config(state=tk.DISABLED) # make the help text read only.
            self.text.grid(row = 1, column = 0)
            # slider?             
        else: 
            
            nextLevel = []
            for el in cont[1] : # for each element in the next level down 
                nextLevel.append(el[0])
            self.lb = tk.Listbox(self, selectmode = tk.SINGLE, height = 0 )    
            for i in nextLevel :
                 self.lb.insert(tk.END,i)            
            self.lb.grid(row = 1, column = 0)
            self.lb.columnconfigure(0, weight=1)
            self.lb.rowconfigure(1,weight=1)
            self.lb.bind('<<ListboxSelect>>', self.levelSelect)
            
    def levelSelect(self,event) :       
        selectIndex = self.lb.curselection()[0]
        # c = self.stack[-1][1][selectIndex]
        c = self.stack[-1][1][selectIndex]
        self.stack.append(c)
        self.displayContents()
    
