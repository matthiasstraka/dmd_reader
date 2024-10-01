"""
Main DMD reader entry point
"""
from ._segments import read_file_header, read_file_footer, read_file_segment

class DmdReader:
    """
    Opens the DMD file <filename> for reading
    """
    def __init__(self, filename):
        # pylint: disable=consider-using-with
        self._file = open(filename, 'rb')
        self._header = read_file_header(self._file)
        self._file.seek(self._header.BLOCK_SIZE)
        self._cfg = read_file_segment(self._file)
        self._footer = read_file_footer(self._file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """
        Close the DMD file
        """
        self._file.close()
        del self._file

    @property
    def dmd_version(self) -> str:
        """
        Return the DMD file version
        """
        return self._header.version

    @property
    def dmd_library(self) -> str:
        """
        Return the identifier of the DMD library used to write the DMD file
        """
        return self._header.library_version
