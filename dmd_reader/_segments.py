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
    FILE_HEADER = 0 << 8
    CFG = 1 << 8
    FILE_FOOTER = 5 << 8

class FileSegment:
    """
    Base class for all file segments
    """
    def __init__(self, segment_type = SegmentType.UNKNOWN, offset = 0, size = 0):
        self.segment_type = segment_type
        self.segment_offset = offset
        self.segment_size = size
        self.data = None

class FileHeader(FileSegment):
    """
    Global file header
    """
    BLOCK_SIZE = 4096
    HEADER_SIZE = 4 + 2 + 2 + 2 + 1 + 64
    def __init__(self, data, segment_type=SegmentType.FILE_HEADER):
        super().__init__(segment_type, 0, FileHeader.BLOCK_SIZE)
        tag, ver_major, ver_minor, self.header_size, self.calc_crc_in_ctrl_blocks, lib_version = unpack("<4sHHH?64s", data)
        if tag != b'DMDF':
            raise RuntimeError("Invalid file header")
        self.version = Version(ver_major, ver_minor)
        nullterm = lib_version.find(b'\x00')
        if nullterm != -1:
            self.library_version = lib_version[:nullterm].decode('ascii')
        else:
            self.library_version = lib_version.decode('ascii')

class FileFooter(FileHeader):
    """
    Global file footer
    """
    def __init__(self, data):
        super().__init__(data, SegmentType.FILE_FOOTER)
        self.ctrl_segments = []

def read_file_header(f):
    data = f.read(FileHeader.HEADER_SIZE + 4)
    header = FileHeader(data[:FileHeader.HEADER_SIZE])
    crc_in_file = int.from_bytes(data[-4:], "little")
    if crc_in_file != crc32(data[:-4]):
        raise RuntimeError("Invalid header CRC")
    return header

def read_file_footer(f):
    f.seek(-FileHeader.BLOCK_SIZE, 2)
    file_offset = f.tell()
    data = f.read(8 + FileHeader.HEADER_SIZE + 2)
    tag = data[0:8]
    if tag != b'NOHD_END':
        raise RuntimeError("Invalid file header")
    offset = 8
    footer = FileFooter(data[offset:(offset+FileHeader.HEADER_SIZE)])
    footer.segment_offset = file_offset
    offset += FileHeader.HEADER_SIZE
    ctrl_seg_cnt = int.from_bytes(data[offset:offset+2], "little")
    crc = crc32(data)
    footer.ctrl_segments = []
    for _ in range(ctrl_seg_cnt):
        data = f.read(4 + 8)
        crc = crc32(data, crc)
        offset_and_size = unpack("<IQ", data)
        footer.ctrl_segments.append(offset_and_size)

    crc_in_file = int.from_bytes(f.read(4), "little")
    if crc_in_file != crc:
        raise RuntimeError("Invalid footer CRC")

    return footer

def read_file_segment(f):
    file_offset = f.tell()
    data = f.read(20)
    tag, data_size, block_size, seg_id, seg_type, crc_in_file = unpack("<4sIIHHI", data)
    if tag != b'DMDH':
        raise RuntimeError("Invalid segment tag")
    if crc_in_file != crc32(data[:-5]):
        raise RuntimeError("Invalid segment CRC")
    segment = FileSegment(type, file_offset, block_size)
    segment.id = seg_id
    if seg_type == SegmentType.CFG.value:
        segment.data = f.read(data_size).decode('utf-8')
        return segment
    return None
