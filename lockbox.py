# password holder
#
#

import os
from os.path import exists,join

from datetime import date 
import hashlib
import tkinter
import sys
import PySimpleGUI as sg
import random
import pickle
import pyperclip
import lockboxHelp

#
# Globals
#
testphrase = "XYZZYPLUGHPLOVER"
LBfile = "" # lock box full file name
LBdata = [] # list of PWObj objects
PW = ""     # Password for your lockbox
HINT = ""   # Password hint

About = "LockBox - a password organizer \n\n\
(C)2022 Tom Arachtingi    Ver 0.9.0330L\n\
Including RC4 code https://github.com/manojpandey/rc4"

class PWObj :
    pwDisplay = "{:<16} {:<32} {:<16} {:0>4d}/{:0>2d}/{:0>2d}"

    def __init__(self, key, theTitle='notGui', n='name', d='description', u='username',
                 p='password') :
        if theTitle != 'notGui' :
            #print('loc 1 ', theTitle)
            objAdd =  [   [sg.Text("Name (for this password)"),sg.InputText(key="newName",focus=True)],
                          [sg.Text("Description or site")       ,sg.InputText(key="newDesc")],
                          [sg.Text("User Name for site ")       ,sg.InputText(key="newUID")],
                          [sg.Text("Password for this site")    ,sg.InputText(key="newPW",password_char="*")],
                          [sg.Submit(), sg.Cancel()]]
            event, values = sg.Window(  theTitle,
                                        objAdd, modal=True, keep_on_top=True ).read(close=True)
            #print('event', event)
            #print('values', values)
            self.desc = values["newDesc" ]
            self.name = values["newName"].strip()
            self.un   = values["newUID"]
            p         = values["newPW"]
            self.pw   = encrypt(key,p).strip()
            self.changedate =  date.today()
            self.history = ["{} Created".format(date.isoformat(self.changedate))]
        else :
            #print('loc 2', theTitle)
            self.desc =  d 
            self.name = n.strip()
            self.un = u
            self.pw = encrypt(key,p).strip()
            self.changedate =  date.today()
            self.history = ["{} Created".format(date.isoformat(self.changedate))]

    def edit(self,key,theTitle="Edit item") :
        objAdd =  [ [sg.Text("Name (for this password)"),sg.InputText(key="editName",default_text=self.name,focus=True)],
                    [sg.Text("Description or site")       ,sg.InputText(key="editDesc",default_text=self.desc)],
                    [sg.Text("User Name for site ")       ,sg.InputText(key="editUID",default_text=self.un)],
                    [sg.Text("Password for this site")    ,sg.InputText(key="editPW",default_text='<no change>',password_char="*")],
                    [sg.Submit(), sg.Cancel()]]
        event, values = sg.Window(  theTitle,
                                    objAdd,modal=True,  keep_on_top=True,resizable=True ).read(close=True)
        #print('event', event)
        #print('values', values)
        n = values["editName"].strip()
        d = values["editDesc"]
        u = values["editUID"]
        p = values["editPW"].strip()
        if p == '<no change>' : 
            pk = self.pw
        else:    
            pk = encrypt(key,p)
        today = date.today()
        todayf = date.isoformat(today)
        if self.name != n :
            self.changedate = today
            self.history.append("{} Edited Name of {}, {} -> {}".format(todayf,self.name,
                                self.name,n))
            self.name = n
        if self.desc != d :
            self.changedate = today
            self.history.append("{} Edited Desc of {}, {} -> {}".format(todayf,self.name,
                                 self.desc, d))                                
            self.desc = d
        if self.un != u :
            self.changedate = today
            self.history.append("{} Edited UID of {}, {} -> {}".format(todayf,self.name,
                                self.un,u))
            self.un = u
        if self.pw != pk :
            self.changedate = today
            self.history.append("{} Edited PW of {}, {} -> {}".format(todayf,self.name,
                                self.pw,pk))
            self.pw = pk
    
        
    def __str__(self) :
        v = PWObj.pwDisplay.format(self.name, self.desc, self.un, 
                                   self.changedate.year,self.changedate.month, self.changedate.day)
        #return self.name+' "'+self.desc+'" ['+self.pw+'] ('+ self.changedate.year + '/' + self.changedate.month + '/' + self.changedate.day + ')'
        return v

    def the_pw(self, key) :
        return " {} == {}".format(decrypt(key,self.pw), str(self.pw) )

    def get_pw(self, key) :
        return "{}".format(decrypt(key,self.pw))


    def showPW(self, key) :
        v = decrypt(key,self.pw)
        sg.popup('Password for {}'.format(self.name), v)


def error(errcode, abort=False, *args) :
    # currently, a simple error mechanism.  Might add logging or a dayfile function
    
    s = ""
    for a in args :
        s = s+str(a) + ' '
        
    print("error - {}  {}".format(errcode, s))

    # gui enhancement
    try :
        s = lockboxHelp.errorMessages[errcode].format(args)
    except KeyError as ke:
        print('error - ',str(lockboxHelp.errorMessages),' ke: ', str(ke))
        sb.popup_error('Unknown Error message. Code "{}"'.format(errcode), title='Errorr LckB0000')
        
    except :    
        s = lockboxHelp.errorMessages[errcode]
    sg.popup_error("unknown error in error code.",title='Error '+errcode)

    if abort :
        print("error - aborting")
        sys.exit()      





#    ####     ####    #   #
#    #   #   #    #   #   #
#    ####    #        ######
#    #   #   #    #       #
#    #    #   ####        #


#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: @manojpandey
# from https://github.com/manojpandey/rc4

# Python 3 implementation for RC4 algorithm
# Brief: https://en.wikipedia.org/wiki/RC4

# Will use codecs, as 'str' object in Python 3 doesn't have any attribute 'decode'
import codecs

MOD = 256


def KSA(key):
    ''' Key Scheduling Algorithm (from wikipedia):
        for i from 0 to 255
            S[i] := i
        endfor
        j := 0
        for i from 0 to 255
            j := (j + S[i] + key[i mod keylength]) mod 256
            swap values of S[i] and S[j]
        endfor
    '''
    key_length = len(key)
    # create the array "S"
    S = list(range(MOD))  # [0,1,2, ... , 255]
    j = 0
    for i in range(MOD):
        j = (j + S[i] + key[i % key_length]) % MOD
        S[i], S[j] = S[j], S[i]  # swap values

    return S


def PRGA(S):
    ''' Psudo Random Generation Algorithm (from wikipedia):
        i := 0
        j := 0
        while GeneratingOutput:
            i := (i + 1) mod 256
            j := (j + S[i]) mod 256
            swap values of S[i] and S[j]
            K := S[(S[i] + S[j]) mod 256]
            output K
        endwhile
    '''
    i = 0
    j = 0
    while True:
        i = (i + 1) % MOD
        j = (j + S[i]) % MOD

        S[i], S[j] = S[j], S[i]  # swap values
        K = S[(S[i] + S[j]) % MOD]
        yield K


def get_keystream(key):
    ''' Takes the encryption key to get the keystream using PRGA
        return object is a generator
    '''
    S = KSA(key)
    return PRGA(S)


def encrypt_logic(key, text):
    ''' :key -> encryption key used for encrypting, as hex string
        :text -> array of unicode values/ byte string to encrpyt/decrypt
    '''
    # For plaintext key, use this
    key = [ord(c) for c in key]
    # If key is in hex:
    # key = codecs.decode(key, 'hex_codec')
    # key = [c for c in key]
    keystream = get_keystream(key)

    res = []
    for c in text:
        val = ("%02X" % (c ^ next(keystream)))  # XOR and taking hex
        res.append(val)
    return ''.join(res)


def encrypt(key, plaintext):
    ''' :key -> encryption key used for encrypting, as hex string
        :plaintext -> plaintext string to encrpyt
    '''
    plaintext = [ord(c) for c in plaintext]
    return encrypt_logic(key, plaintext)


def decrypt(key, ciphertext):
    ''' :key -> encryption key used for encrypting, as hex string
        :ciphertext -> hex encoded ciphered text using RC4
    '''
    ciphertext = codecs.decode(ciphertext, 'hex_codec')
    res = encrypt_logic(key, ciphertext)
    return codecs.decode(res, 'hex_codec').decode('utf-8')

#
# Menu function
#
def helpAction() :
    
    lockboxHelp.HelpDialog(lockboxHelp.help_text)
    
def export() :
    global LBdata, LBfile, PW, testphrase
    filename = sg.popup_get_file("File to export data",title='Export', save_as=True)  
    savedata(filename)

def saveAction() :    
    global LBdata, LBfile, PW, testphrase
    savedata(LBfile)

def aboutAction() :
    global About
    sg.popup(About, title="About LockBox")

def changePWAction() :
    global LBdata, LBfile, PW, HINT, testphrase
    hint = None
    while True :
        print('changePWAction - hint ',hint)
        oldPW = getPW(hint=hint)
        
        if oldPW is None : return
        if PW == oldPW : break
        sg.popup_error('Wrong Password')
        hint = HINT
        
    newPW = sg.popup_get_text("Enter new password",title="New Master Password")
    newHint = sg.popup_get_text("Enter new Hint",title="New Hint for new Password")
    changePW(oldPW, newPW,LBdata)
    PW = newPW
    HINT = newHint
    savedata( LBfile)

def find(name, data) :
    # find index into data of a pwObj that has name
    for i in range(1, len(data) ) :
        if data[i].name == name :
            return i
    return 0    
  
def mergeAction() :
    global LBdata, PW, HINT, testphrase

    filename = sg.popup_get_file("File to import data",title='Merge',
                                 save_as=False)
    if filename is None :
        return  # canceled when asking for file
    if not exists(filename) :
        return
    
    mergeData, mergeHint, mergepw = load(filename)
    if mergepw != PW :
        changePW(mergepw, PW,mergeData)
    for i in range(1, len(mergeData) ) : # merge each item from the other file
        j = find(mergeData[i].name, LBdata)
        if j == 0 : # new item
            mergeData[i].history = ["{} Merged".format(date.isoformat(date.today() ))]
            LBdata.append(mergeData[i]) 
        else :
            if mergeData[i].changedate < LBdata[j].changedate :
                mergeData[i].history = ["{} Merged".format(date.isoformat(date.today() ))]
                LBdata[j] = mergeData[i] 

def history():
    global LBdata
    hist = "\n"
    for o in LBdata :
        try :
            if type(o) == PWObj :
                print('--- ', o.name, ' ---')
                hist = hist + '\n--- {} ---\n'.format(o.name)
                for h in o.history :
                    print(h)
                    hist = hist + h + '\n'
                    
        except AttributeError as e :
               print( " history error: ",e, "::", o)
    layout = [[sg.Multiline(default_text=hist, enter_submits=False, s=(100,20),
                disabled=False, autoscroll=True, write_only=True)]]
    window2 = sg.Window("History", layout, modal=True)
    choice = None
    while True:
        event, values = window2.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        
    window2.close()    

#
# Pickle functions
#

def load(fn) :
    """ load tne file
        fn = full path
        Used to load both the program data and merged data
        returns data, hint, and pw that worked on file
        
        Unpickles the file
        make sure the file has 3 parts.
        check that the pw is correct.
        if not, loop while asking for new pw
    """    
        
    global LBdata, PW, testphrase

    # print('load - fn = ', fn)
    data = []
    thedata = None
    theHINT = None
    pw = PW
    try :
        with open(fn, 'rb') as loaf:
            data = []

            data = pickle.load(loaf)                            # unpickle data: [pwcheck, save_hint, LBdata ]
            print('load - unpickled file')
        if len(data) != 3 : # currently data is stored in 3 chunks 
            error("LckB0001",False,loadfile)
            return None, None, None            
        else :
            #extract the values
            pwcheck = data[0]
            encrypted_hint=data[1]
            saved_hint = decrypt(testphrase,encrypted_hint)
            theData = data[2]

            print('load - len', len(data), ' hint ', saved_hint,' > ',testphrase)

            #check if pw is correct
            try :                                # test pw by decrypting a known phrase
                tmp = decrypt(pw,pwcheck)        # with the pw.
            except UnicodeDecodeError as UDE :   # could get a UDE if the pw is wrong
                tmp = "no"                       # so make sure tmp won't match
                
            if  tmp == testphrase :              # test tmp against the known phrase
                return theData, saved_hint, pw   # if they match - well and good, and leave
            else:
                pw_processing = True
                while pw_processing :
                    title = 'Password for '+fn
                    pw = getPW(hint=saved_hint,title=title)  # ask for a new password, offer the hint
                    # same code as above
                    if pw is None :              # canceled out of request for pw
                        sys.quit()               # leave program
          
                    #print('getting pw again ',pw)
                    try :                        # test pw by decrypting a known phrase
                        tmp = decrypt(pw,pwcheck)          # with the pw.
                    except UnicodeDecodeError as UDE :     # could get a UDE if the pw is wrong
                        tmp = "no"               # so make sure tmp won't match
                    if tmp == testphrase :       # if pw given is correct
                        #print('load - password worked')
                        return theData, saved_hint, pw     # exit proc, returning contents of file
                    
    except pickle.UnpicklingError as pe :        # file opened but unreadable 
         #print("Error while trying to read the List : ",str(pe))
         error("LckB0002",False,loadfile)
         #popup_error(title='Bad file, unreadable')
         return None, None, None
    except OSError as ose:                       # file didn't open
        #print("Error opening file {} : {}".format(loadfile, str(ose)) )
        error("LckB0003", False, loadfile)
        #popup_error(title='Cannot open file')
        return None, None, None
    print("shouldn't be here")


def savedata(fn) :
    """ write the data out to a file, given by the parameter fn 
        Create directory if needed
        pickle the file
        
    """
    global LBdata, PW, testphrase, HINT
    pwcheck = encrypt(PW,testphrase)
    save_hint = encrypt(testphrase, HINT)
    saveobj = [pwcheck, save_hint, LBdata ]
    #print('In Save >{}<'.format(fn))
    dirname_from_filename = os.path.dirname(fn)   # see if a path was provided as part of filename
    if dirname_from_filename:
        path = dirname_from_filename
        filename = os.path.basename(fn)
    else :                                        # no path
        path = os.getcwd()                        # use the current working directory.  May not work but have to try something
        
    #print('  path {}  filename {}'.format(path,filename))
    if not exists(path) : #no directory
        #print('no directory')
        os.makedirs(path,exist_ok=True)
        #print('created directory')

    try :                                        # pickle the file
        with open(fn, 'wb') as savf:
            #print('About to pickle')
            pickle.dump(saveobj, savf)
            
    except pickle.PicklingError as pe :          # can't write file
        print("Error while trying to write out the password list : ",str(pe))
        error("LckB0002",False,fn)
    except FileNotFoundError as fnfe :           # this is early code, not sure if it is still needed
        print("Filee not found error ", fnfe)
        us=sg.UserSetings(file='lockbox')
        f,p,n = us._compute_filename(filename=fn)
        if not exits(p) : #no directory
            print('no directory')
            os.makedirs(p,exit_ok=True)
            print('created directory')
            savedir(fn)    
    except OSError as ose :                      # another section of early code.  OS error opening file
        print("Error opening file "+ fn +" :", str(ose))    
        error("LckB0003",False,fn)


# next few functions stolen from PySimpleGUI
def running_linux():
    """
    Determines the OS is Linux by using sys.platform
    Returns True if Linux
    :return: True if sys.platform indicates running Linux
    :rtype:  (bool)
    """
    return sys.platform.startswith('linux')


def running_mac():
    """
    Determines the OS is Mac by using sys.platform
    Returns True if Mac
    :return: True if sys.platform indicates running Mac
    :rtype:  (bool)
    """
    return sys.platform.startswith('darwin')      # don't have a Mac to test any of the Mac code


def running_windows():
    """
    Determines the OS is Windows by using sys.platform
    Returns True if Windows
    :return: True if sys.platform indicates running Windows
    :rtype:  (bool)
    """
    return sys.platform.startswith('win')



    
def getPW(hint=None,title=None) : 
    # hint will be None if this is the first time running.
    # ask for the password
    obscure = '*'
    if title is None :
        thetitle = 'Enter PW'
    else :
        thetitle = title

    if hint is None :
        obscure = ""
        text = 'Enter the Key for securing your passwords'
    else :
        print('getpw hint = ',hint)
        text = 'Hint: '+hint

    thePW = sg.popup_get_text(text, title=thetitle, password_char=obscure)
    if thePW is None :
        return None
    return thePW.strip()


    
def getHint() : 
    # ask for the hint
    thehint = sg.popup_get_text('Enter a Hint for the password.  There is no recovery if you can\'t remember the maser password',
                      title='Enter Hint',size=(100,1))
    return thehint


def changePW(oldPW,newPW,data) :
    """ changePW - change the password in a list of PWObj
        oldPW - the current pw used by the data
        newPW - the new pw that the password part of the data will be changed to
        data  - the list of PWObj to be changed
    """
    l = []
    for i in range(1, len(data) ) :
        try :
            opw = decrypt(oldPW,data[i].pw)
            data[i].pw = encrypt(newPW, opw )
        except UnicodeDecodeError as ude :
            l.append( data[1].name )
                
    if len(l) > 0 :  # un-decryptable passwords encountered
        error('LckB0004',False,l)

def getfilename() :
    # returns file name and whether the file exists
    #print('getfile name ')
    DEFAULT_USER_SETTINGS_WIN_PATH = r'~\AppData\Local\LockBox'
    DEFAULT_USER_SETTINGS_LINUX_PATH = r'~/.config/LockBox'
    DEFAULT_USER_SETTINGS_MAC_PATH = r'~/Library/Application Support/LockBox'

    if running_windows():
        path = os.path.expanduser(DEFAULT_USER_SETTINGS_WIN_PATH)
    elif running_linux():
        path = os.path.expanduser(DEFAULT_USER_SETTINGS_LINUX_PATH)
    elif running_mac():
        path = os.path.expanduser(DEFAULT_USER_SETTINGS_MAC_PATH)
    
    fullFileName = join(path,"lockbox.dta") # lock box file
    #print('getfilename - about to build file')
    e = exists(fullFileName)
    return fullFileName,e

def init() :
    global LBdata, LBfile, PW, testphrase, HINT
    LBfile, ee = getfilename()

    PW = getPW()
    #print('Init - got PW')
    if PW is None :                               # hit cancel on the PW screen
        sys.quit()
    
    if ee :
        #print('Lockbox file exists : {}'.format(LBfile))
        LBdata, HINT, PW = load(LBfile)
        
    else :
        #print('lockbox doesnt exist')
        header = PWObj.pwDisplay.format("Name","Description or Site","User Name",0,0,0) #generating header line
        header = header[:67] + "Set Date"
        LBdata = [header]                         #start with an empty list initially
        # print('Lockbox file didn\'t exists : {} size {}'.format(LBfile , len(LBdata)))
        HINT = None
        while HINT is None :
           HINT = getHint()
    #print('init - done')
    if LBfile is None :
        # something went wrong reading the file
        os.quit()

def main():
    global LBdata, LBfile, PW, testphrase
    init()
    if LBdata is None : # cancelled in pw processing
        sys.quit()
    menu_def = [['File', ['Export','Merge','Save','Exit']],
                ['Edit', ['Edit','Delete','Change Password']],
                ['Help', ['Help','About','History']]]

    theListBox = sg.Listbox(values=LBdata,select_mode="LISTBOX_SELECT_MODE_SINGLE", horizontal_scroll=True, key='list',
                            expand_x = True, expand_y = True, font='Courier' )
                            
    mainlayout = [[ sg.Menu(menu_def, tearoff=False)],
                  [ theListBox ],
                  [sg.B('Add'), sg.B('Edit'), sg.B('View Password'), sg.B('PW -> Clipboard', key='_CB_'), sg.B('Done')]]
    window = sg.Window('Lockbox!', mainlayout, size=(800, 600),resizable=True) 

    
    print('before main loop')
    if len(LBdata) == 1 :
        p = PWObj(PW,"Enter information for the first password")
        LBdata.append(p)
        ## test
        print(p)
    # event loop
    while True:
        
        #   get event
        event, values = window.read()
        #print('Event ',event)

        #   process event

        if event == 'Add' :
            # do add
            p = PWObj(PW,"Enter information for password site")
            LBdata.append(p)
            theListBox.Update(values=LBdata)

        elif event == 'Edit' or event == 'Update' :
            # do edit
            n = theListBox.get_indexes()[0]
            if n != 0 :
                g = theListBox.get()
                v = theListBox.get_list_values()
                o = values['list'][0]
            #print( '-values ', o, str(o) )
            #print('get   ',g[0] , str(g[0]) )
            #print('get_list', v, str(g) )
            print('indexes ', n, LBdata[n])
            LBdata[n].edit(PW,"Edit item {}".format(LBdata[n].name))
            theListBox.Update(values=LBdata)
        elif event == 'Delete' :
            n = theListBox.get_indexes()[0]
            del LBdata[n]
            theListBox.Update(values=LBdata)
        elif event == 'Test' :
            # test routine
            r=random.randint(0,5000)
            for i in range(5) :
               r = r + 1
               s=str(r)
               LBdata.append(PWObj(PW,u='un'+s,p='pw'+s, n='name'+s, d='desc'+s+'.com' ) )
            theListBox.Update(values=LBdata)
        elif event == 'Change Password' :
            changePWAction()
        elif event == 'Export' :
            export()
     
        elif event == 'Merge' :
            mergeAction()
            theListBox.Update(values=LBdata)

        elif event == 'Help' :
            helpAction()
        elif event == 'About' :
            aboutAction()
        elif event == 'History' :
            history()
        elif event == 'View Password' :
            try : 
                n = theListBox.get_indexes()[0]
                if n != 0 :
                    LBdata[n].showPW(PW)
            except : pass        
        elif event == '_CB_' :  # copy pw to clipboard
            n = theListBox.get_indexes()[0]
            pyperclip.copy(LBdata[n].get_pw(PW))
        elif event == sg.WIN_CLOSED or event == 'Done' or event == 'Exit':
            # save and exit
            saveAction()
            #print('exit')
            break
        
         
        # Update the "output" text element to be the value of "input" element
        
        # In older code you'll find it written using FindElement or Element
        # window.FindElement('-OUTPUT-').Update(values['-IN-'])
        # A shortened version of this update can be written without the ".Update"
        # window['-OUTPUT-'](values['-IN-'])     

    window.close()

   
    # until end event (quit or x)
    # write out list


if __name__ == '__main__':
    main()
