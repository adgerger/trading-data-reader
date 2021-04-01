from io import BytesIO as Buffer
from io import (TextIOWrapper, BytesIO)
from zipfile import ZipFile


def get_buffer_from_zip(zipfile, fname):
    return TextIOWrapper(BytesIO(zipfile.read(fname)))

def get_zipfile(res):
    buffered = Buffer(res.content)
    return ZipFile(buffered)

def camel2title(base):
    return [re.sub("([a-z])([A-Z])", "\g<1> \g<2>", i).title() for i in base]
