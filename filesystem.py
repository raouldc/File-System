'''
Created on 27/08/2013

This is where you do your work.
Not only do you need to fill in the methods but you can also add any other classes,
methods or functions to this file to make your system pass all of the tests.

@author: rdcu001
'''
from math import ceil

from drive import Drive

class A2File(object):
    '''
    One of these gets returned from Volume open.
    '''

    def __init__(self, params):
        '''
        Initializes an A2File object.
        Not called from the test file but you should call this from the
        Volume.open method.
        You can use as many parameters as you need.
        '''
        self.fsize = 0
        self.content = b''
        self.filename = params

    def size(self):
        '''
        Returns the size of the file in bytes.
        '''
        return self.fsize

    def write(self, location, data):
        '''
        Writes data to a file at a specific byte location.
        If location is greater than the size of the file the file is extended
        to the location with spaces.
        '''
        count = 0
        for i in range(location+len(data)):
            if i > len(self.content) and i<location:
                self.content+=b' '
            elif i>len(self.content) and i>=location:
                if count<len(data):
                    self.content+=data[count]
                    count+=1
            elif i<len(self.content) and i>=location:
                self.content[i] = data[count]
                count+=1

    def read(self, location, amount):
        '''
        Reads from a file at a specific byte location.
        An exception is thrown if any of the range from
        location to (location + amount - 1) is outside the range of the file.
        Areas within the range of the file return spaces if they have not been written to.
        '''
        if (location+amount-1)>len(self.content):
            raise IOError()
        return self.content[location:]

class Volume(object):
    '''
    A volume is the disk as it appears to the file system.
    The disk structure is to be entirely stored in ASCII so that it
    can be inspected easily. It must contain:
        Volume data blocks: the number of contiguous blocks with the volume data - as a string, ends with "\n"
        Name: at least one character plus "\n" for end of name)
        Size: as a string terminated with "\n"
        Free block bitmap: drive.num_blocks() + 1 bytes ("x" indicates used, "-" indicates free, ends with "\n")
        First block of root directory (called root_index) : as a string terminated with "\n" - always the last
            block on the drive.
    '''

    @staticmethod
    def format(drive, name):
        '''
        Creates a new volume in a disk.
        Puts the initial metadata on the disk.
        The name must be at least one byte long and not include "\n".
        Raises an IOError if after the allocation of the volume information
        there are not enough blocks to allocate the root directory and at least
        one block for a file.
        Returns the volume.
        '''
        if name is None or name == b'' or name == '':#check length of name
            raise ValueError("Invalid Name")
        if b'\n' in name:
            raise ValueError("Name cannot contain \"\n\"")
        if len(name) >drive.BLK_SIZE*(drive.num_blocks()-2):
            raise ValueError("")
        volBlockCount=1

        vol = Volume()

        nameArr =[]
        if len(name)>62:
            volBlockCount = ceil(len(name)/62)
            a=0
            b=62
            for i in range(volBlockCount):
                nameArr.append(name[a:b])
                a=b
                b+=64
        else:
            nameArr.append(name)

        vol.setName(nameArr)
        vol.setSize(drive.num_blocks())
        vol.setDrive(drive)
        #assuming that there is 1 block at the end for the root directory
        #and the volume info is in one block
        bmpArray=[]
        for i in range(volBlockCount):
            bmpArray.append(1)
        for i in range(drive.num_blocks()-1-volBlockCount):
            bmpArray.append(0)
        bmpArray.append(1)
        vol.setBitmapArray(bmpArray)
        vol.set_data_blocks(volBlockCount)
        return vol

    def name(self):
        '''
        Returns the volumes name.
        '''
        name =b''
        for i,v in enumerate(self.fname):
            name += v
        return name

    def setName(self,name):
        self.fname=name

    def setSize(self,size):
        self.fsize= size

    def setDrive(self,drive):
        self.driveObj=drive

    def set_data_blocks(self,datablocks):
        self.data_blocks=datablocks


    def volume_data_blocks(self):
        '''
        Returns the number of blocks at the beginning of the drive which are used to hold
        the volume information.
        '''
        return self.data_blocks

    def size(self):
        '''
        Returns the number of blocks in the underlying drive.
        '''
        return self.fsize

    def setBitmapArray(self,b):
        self.fbmpArray = b

    def bitmap(self):
        '''
        Returns the volume block bitmap.
        '''
        bitmap =b''

        for i, v in enumerate(self.fbmpArray):
            if v == 1:
                bitmap += b'x'
            else:
                bitmap += b'-'


        return bitmap

    def root_index(self):
        '''
        Returns the block number of the first block of the root directory.
        Always the last block on the drive.
        '''
        return self.fsize-1

    @staticmethod
    def mount(drive_name):
        '''
        Reconnects a drive as a volume.
        Any data on the drive is preserved.
        Returns the volume.
        '''
        drive = Drive.reconnect(drive_name)
        vol = Volume()

        block = drive.read_block(0).split(b'\n')
        volinfosize= int(bytes.decode(block[0]))
        nameArr = []
        nameArr.append(block[1])
        if volinfosize!=1:
            for i in range (1,volinfosize-1):
                nameArr.append(drive.read_block(0).split(b'\n')[0])
            block = drive.read_block(volinfosize-1).split(b'\n')
        vol.setName(nameArr)
        vol.setSize(int(bytes.decode(block[2])))
        vol.setDrive(drive)
        vol.set_data_blocks(int(bytes.decode(block[0])))
        
        bmpArr =[]
        
        bmp = bytes.decode(block[3])

        for i,v in enumerate(bmp):
            if v == 'x':
                bmpArr.append(1)
            else:
                bmpArr.append(0)
        vol.setBitmapArray(bmpArr)
        return vol

    def unmount(self):
        '''
        Unmounts the volume and disconnects the drive.
        '''


        for i, v in enumerate(self.fbmpArray):
            if v == 1:
                if i == 0:
                    self.writevolinfo()
                elif i == self.root_index():
                    self.writeroot(self.root_index())
                else:
                    #write file
                    pass
        self.driveObj.disconnect()
        self.driveObj = None

    def writevolinfo(self):
        #write number of blocks occupied by the volume information
        block =b""+bytearray(str(self.volume_data_blocks()),'utf-8')+b'\n'
        #write the rest of the volume information
        block = block + self.fname[0]
        if len(self.fname)!=1:
            self.driveObj.write_block(0,block)
            for i in range(1,len(self.fname)):
                block = b''
                block = block + self.fname[i]
                if i !=len(self.fname)-1:
                    self.driveObj.write_block(i,block)
        block+=b'\n'+bytearray(str(self.fsize),'utf-8')+b'\n'
        block+=self.bitmap()+b'\n'
        block+=bytearray(str(self.root_index()),'utf-8')+b'\n'
        while len(block)<64:
            block+=b' '
        self.driveObj.write_block(len(self.fname)-1,block)

    def writeroot(self,ind):
        block = b''
        for i in range(16):
            block = block + b'  0\n'
        self.driveObj.write_block(ind,block)

    def open(self, filename):
        '''
        Opens a file for read and write operations.
        If the file does not exist it is created.
        Returns an A2File object.
        '''
        if b'\n' in filename:
            raise ValueError()
        return A2File(filename)
