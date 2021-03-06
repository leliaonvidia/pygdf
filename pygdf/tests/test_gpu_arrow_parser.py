import logging

import numpy as np
from numba import cuda

from pygdf.gpuarrow import GpuArrowReader


def test_gpu_parse_arrow_data():
    # make gpu array
    TESTDATA = b"\x00\x01\x00\x00\x10\x00\x00\x00\x0c\x00\x0e\x00\x06\x00\x05\x00\x08\x00\x00\x00\x0c\x00\x00\x00\x00\x01\x01\x00\x10\x00\x00\x00\x00\x00\n\x00\x08\x00\x00\x00\x04\x00\x00\x00\n\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00l\x00\x00\x00\x04\x00\x00\x00\xb0\xff\xff\xff\x00\x00\x01\x038\x00\x00\x00\x1c\x00\x00\x00\x14\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x1c\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x9a\xff\xff\xff\x00\x00\x01\x00\x8c\xff\xff\xff \x00\x01\x00\x94\xff\xff\xff\x01\x00\x02\x00\x08\x00\x00\x00dest_lon\x00\x00\x00\x00\x14\x00\x18\x00\x08\x00\x06\x00\x07\x00\x0c\x00\x00\x00\x10\x00\x14\x00\x00\x00\x14\x00\x00\x00\x00\x00\x01\x03H\x00\x00\x00$\x00\x00\x00\x14\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00,\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x08\x00\x06\x00\x06\x00\x00\x00\x00\x00\x01\x00\xf8\xff\xff\xff \x00\x01\x00\x08\x00\x08\x00\x04\x00\x06\x00\x08\x00\x00\x00\x01\x00\x02\x00\x08\x00\x00\x00dest_lat\x00\x00\x00\x00\xd8\x00\x00\x00\x14\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x16\x00\x06\x00\x05\x00\x08\x00\x0c\x00\x0c\x00\x00\x00\x00\x03\x01\x00\x18\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x18\x00\x0c\x00\x04\x00\x08\x00\n\x00\x00\x00|\x00\x00\x00\x10\x00\x00\x00\x17\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x17\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x17\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x91\xa7\x06B\x91\xa7\x06B\x91\xa7\x06B\xc4\xcd\xdfA\x91\xa7\x06B\xc4\xcd\xdfA\xe7\xea\nB\x9c\xb3\x1cB\xe7\xea\nB\x9c\xb3\x1cB\xe7\xea\nB]n\xe3A\xe7\xea\nB\xd9$\'Brc\x03BL\x8a\xffArc\x03B\xd9$\'Brc\x03BL\x8a\xffArc\x03Bt@\x06B\x03o\x1fB\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00C\xa5\xcb\xc2C\xa5\xcb\xc2C\xa5\xcb\xc2\x06\x11\xa5\xc2C\xa5\xcb\xc2\x06\x11\xa5\xc2\xd0r\xb8\xc2\x1eV\x99\xc2\xd0r\xb8\xc2\x1eV\x99\xc2\xd0r\xb8\xc2\xce\xa1\xa2\xc2\xd0r\xb8\xc2>\x81\xaf\xc2\x1b\xb4\xc1\xc2ag\xcc\xc2\x1b\xb4\xc1\xc2>\x81\xaf\xc2\x1b\xb4\xc1\xc2ag\xcc\xc2\x1b\xb4\xc1\xc2\xd1\x81\xad\xc2\x81U\xd1\xc2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    cpu_data = np.ndarray(shape=len(TESTDATA), dtype=np.byte,
                          buffer=bytearray(TESTDATA))
    gpu_data = cuda.to_device(cpu_data)
    del cpu_data
    # test reader
    reader = GpuArrowReader(gpu_data)
    assert reader[0].name == 'dest_lat'
    assert reader[1].name == 'dest_lon'
    lat = reader[0].data.copy_to_host()
    lon = reader[1].data.copy_to_host()
    assert lat.size == 23
    assert lon.size == 23
    np.testing.assert_array_less(lat, 42)
    np.testing.assert_array_less(27, lat)
    np.testing.assert_array_less(lon, -76)
    np.testing.assert_array_less(-105, lon)

    dct = reader.to_dict()
    np.testing.assert_array_equal(lat, dct['dest_lat'].to_array())
    np.testing.assert_array_equal(lon, dct['dest_lon'].to_array())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('pygdf.gpuarrow').setLevel(logging.DEBUG)

    test_gpu_parse_arrow_data()
