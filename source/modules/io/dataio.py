import glob
import os
import sys
import torch.utils.data as data
from .dataloader import adobenpi
from .dataloader import realdata
from .utils import *


class dataio(data.Dataset):
    def __init__(self, mode, args, conf, outdir):

        if mode == 'Train':
            data_root = [args.training_dir]
            extension = conf.train_suffix
            self.numberOfImageBuffer = conf.train_maxNumberOfImages
            self.datatype = conf.train_datatype
            self.prefix = conf.train_prefix
            self.outdir = outdir

        elif mode == 'Test':
            data_root = [args.test_dir]
            extension = conf.test_suffix
            self.numberOfImageBuffer = conf.test_maxNumberOfImages
            self.datatype = conf.test_datatype
            self.prefix = conf.test_prefix
            self.outdir = outdir
        else:
            print("mode must be from [Train, Test]", file=sys.stderr)
            sys.exit(1)

        self.data_name = []
        self.set_id = []
        self.valid = []
        self.sample_id = []
        self.dataCount = 0
        self.dataLength = -1
        self.mode = mode
        self.loader_imgsize = None

        self.objlist = []
        for i in range(len(data_root)):
            print('Initialize %s' % (data_root[i]))
            objlist = []
            [objlist.append(p) for p in glob.glob(
                data_root[i] + '/*%s' % extension, recursive=True) if os.path.isdir(p)]
            objlist = sorted(objlist)
            self.objlist = self.objlist + objlist
        print(f"Number of {mode} set is {len(self.objlist)}")

        if self.datatype == 'AdobeNPI':
            self.data = adobenpi.dataloader(self.numberOfImageBuffer)
        elif self.datatype == 'RealData':
            self.data = realdata.dataloader(
                self.numberOfImageBuffer, self.outdir)
        else:
            raise Exception(' "datatype" != in "Cycles, Adobe, DiLiGenT"')

    def __getitem__(self, index_):

        objid = index_
        if self.datatype == 'AdobeNPI':
            self.data.load(self.objlist, objid, prefix=self.prefix)
        elif self.datatype == 'RealData':
            self.data.load(self.objlist, objid, prefix=self.prefix,
                           loader_imgsize=self.loader_imgsize[0])

        else:
            raise Exception(' "datatype" != in "Cycles, Adobe, DiLiGenT"')

        img = self.data.I.transpose(2, 0, 1, 3)  # c, h, w, N
        nml = self.data.N.transpose(2, 0, 1)  # 3, h, w
        mask = self.data.mask.transpose(2, 0, 1)  # 1, h, w
        return img, nml, mask

    def __len__(self):
        return len(self.objlist)
