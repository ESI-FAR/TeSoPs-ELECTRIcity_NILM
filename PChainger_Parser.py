import numpy as np
import pandas as pd
from pathlib import Path
from collections import defaultdict
from NILM_Dataset import *
from Pretrain_Dataset import *


class PChainger_Parser:

    def __init__(
            self,
            sampling,
            normalize,
            cutoff,
            threshold,
            location,
            min_on,
            min_off,
            val_size,
            window_size,
            window_stride,
            ):

        self.data_location = location
        self.sampling = sampling
        self.normalize = normalize
        self.cutoff = cutoff
        self.threshold = threshold
        self.min_on = min_on
        self.min_off = min_off
        self.val_size = val_size
        self.window_size = window_size
        self.window_stride = window_stride

        self.index, self.x = self.load_data(location)

        if self.normalize == 'mean':
            self.x_mean = np.mean(self.x)
            self.x_std = np.std(self.x)
            self.x = (self.x - self.x_mean) / self.x_std
        elif self.normalize == 'minmax':
            self.x_min = min(self.x)
            self.x_max = max(self.x)
            self.x = (self.x - self.x_min) / (self.x_max - self.x_min)

    def load_data(self, location):
        #house_data = pd.read_csv(location, sep=' ', header=None) #aggregate
        house_data = pd.read_csv(location, sep=',', header=None) #aggregate

        #read aggregate data and resample
        house_data.columns = ['time','aggregate']
        #house_data['time'] = pd.to_datetime(house_data['time'], unit = 's')
        house_data['time'] = pd.to_datetime(house_data['time'])
        house_data = house_data.set_index('time').resample(self.sampling).mean().fillna(method='ffill', limit=30)

        house_data = house_data.clip([0] * len(house_data.columns), self.cutoff, axis=1) # force values to be between 0 and cutoff
        house_data = house_data.fillna(0)
        return pd.to_datetime(house_data.index), house_data.reset_index(drop=True).values[:, 0]

    def get_train_datasets(self):
        val_end = int(self.val_size * len(self.x))

        val = NILMDataset(self.x[:val_end],
                          self.x[:val_end],  # nonsense, to satisfy NILMDataset
                          [1] * len(self.x),  # nonsense, to satisfy NILMDataset
                          self.window_size,
                          self.window_size    #non-overlapping windows
                          )

        train = NILMDataset(self.x[val_end:],
                            self.x[val_end:],  # nonsense, to satisfy NILMDataset
                            [1] * len(self.x),  # nonsense, to satisfy NILMDataset
                            self.window_size,
                            self.window_stride
                            )
        return train, val
