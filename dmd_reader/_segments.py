"""
Various file segment structures
"""
from enum import Enum
from zlib import crc32
from struct import unpack
from ._types import Version

class SegmentType(Enum):
    """
    A name for the segment
    """
    UNKNOWN = -1
    FILE_HEADER = 0
    FILE_FOOTER = 1

class FileSegment:
    """
    Base class for all file segments
    """
    def __init__(self, segment_type = SegmentType.UNKNOWN, offset = 0, size = 0):
        self.segment_type = segment_type
        self.segment_offset = offset
        self.segment_size = size
        self.crc = getattr(self, 'crc', 0)

class FileInfoSegment(FileSegment):
    """
    Base class for file info segments
    """
    FILE_INFO_SIZE = 4 + 2 + 2 + 2 + 1 + 64
    def __init__(self, f, segment_type = SegmentType.UNKNOWN, block_offset = 0, block_size = 0):
        super().__init__(segment_type, block_offset, block_size)
        data = f.read(FileInfoSegment.FILE_INFO_SIZE)
        self.file_identifier = data[0:4].decode('ascii')
        self.version = Version(*unpack("<HH", data[4:8]))
        self.header_size, self.calc_crc_in_ctrl_blocks = unpack("<H?", data[8:11])
        library_version_sz = data[11:]
        nullterm = library_version_sz.find(b'\x00')
        if nullterm != -1:
            self.library_version = library_version_sz[:nullterm].decode('ascii')
        else:
            self.library_version = library_version_sz.decode('ascii')
        self.crc = crc32(data, self.crc)

class FileHeader(FileInfoSegment):
    """
    Global file header
    """
    BLOCK_SIZE = 4096
    def __init__(self, f):
        f.seek(0, 1)
        super().__init__(f, SegmentType.FILE_HEADER, 0, FileHeader.BLOCK_SIZE)
        crc_in_file = int.from_bytes(f.read(4), "little")
        if crc_in_file != self.crc:
            raise RuntimeError("Invalid header CRC")

class FileFooter(FileInfoSegment):
    """
    Global file footer
    """
    BLOCK_SIZE = 4096
    def __init__(self, f):
        f.seek(-FileFooter.BLOCK_SIZE, 2) # Footer is at the end of the file
        file_offset = f.tell()
        data = f.read(8)
        self.crc = crc32(data)
        self.footer_tag = data.decode('ascii')

        super().__init__(f, SegmentType.FILE_FOOTER, file_offset, FileFooter.BLOCK_SIZE)

        data = f.read(2)
        self.crc = crc32(data, self.crc)
        ctrl_seg_cnt = int.from_bytes(data, "little")
        self.ctrl_segments = []
        for _ in range(ctrl_seg_cnt):
            data = f.read(4 + 8)
            self.crc = crc32(data, self.crc)
            offset_and_size = unpack("<IQ", data[0:12])
            self.ctrl_segments.append(offset_and_size)

        crc_in_file = int.from_bytes(f.read(4), "little")
        if crc_in_file != self.crc:
            raise RuntimeError("Invalid footer CRC")
