'''
Created on 27/08/2013

This is where you do your work.
Not only do you need to fill in the methods but you can also add any other classes, 
methods or functions to this file to make your system pass all of the tests.

@author: rdcu001
'''

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
        pass
    
    def size(self):
        '''
        Returns the size of the file in bytes.
        '''
        pass
    
    def write(self, location, data):
        '''
        Writes data to a file at a specific byte location.
        If location is greater than the size of the file the file is extended
        to the location with spaces. 
        '''
        pass
    
    def read(self, location, amount):
        '''
        Reads from a file at a specific byte location.
        An exception is thrown if any of the range from
        location to (location + amount - 1) is outside the range of the file.
        Areas within the range of the file return spaces if they have not been written to.
        '''
        pass

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
        vol.setName(name)
        vol.setSize(drive.num_blocks())
        vol.setDrive(drive)
        vol.set_data_blocks(volBlockCount)
        return vol
    
    def name(self):
        '''
        Returns the volumes name.
        '''
        return self.fname
    
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
    
    def bitmap(self):
        '''
        Returns the volume block bitmap.
        '''
        bitmap =b''
        for i in range(self.fsize):
            if len(self.driveObj.read_block(i).strip()) != 0:
                bitmap = bitmap+b'x'
            else:
                bitmap = bitmap+b'-'
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
        vol = Volume
        
        block = drive.read_block(0).split(b'\n')
        #gotta account for multiple blocks of info
        vol.setName(block[1])
        vol.setSize(int(block[2]))
        vol.setDrive(drive)
        vol.set_data_blocks(block[0])
        return vol
    
    def unmount(self):
        '''
        Unmounts the volume and disconnects the drive.
        '''
        driveObj.disconnect()
        driveObj = None
    
    def open(self, filename):
        '''
        Opens a file for read and write operations.
        If the file does not exist it is created.
        Returns an A2File object.
        '''
        pass
