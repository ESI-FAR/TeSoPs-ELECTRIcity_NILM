#!/usr/bin/env python3

import torch
torch.set_default_tensor_type(torch.DoubleTensor)

import argparse
from config import *
from UKDALE_Parser import *
from REDD_Parser import *
from Refit_Parser import *
from Electricity_model import *
from NILM_Dataloader import *
from Trainer import *
from time import time
from pathlib import Path
import pickle as pkl
import plotly.express as px


with open("./results_UK-DALE_TitanV_kettle/uk_dale/kettle/results.pkl", "rb") as f:
    res = pkl.load(f)

args = res["args"]

# override computing device
args.device = "cpu"
args.pretrain_num_epochs = 0
args.num_epochs = 0
args.validation_size = 1
args.hidden = 256

setup_seed(args.seed)

args.house_indices = [2]
args.validation_size = .1
ds_parser = UK_Dale_Parser(args)

model = ELECTRICITY(args)
trainer = Trainer(args,ds_parser,model)

# Why is this necessary?
model.pretrain = False

dataloader = NILMDataloader(args, ds_parser)
_, test_loader = dataloader.get_dataloaders()
mre, mae, acc, prec, recall, f1 = trainer.test(test_loader, map_location='cpu')

print('Mean Accuracy:', acc)
print('Mean F1-Score:', f1)
print('MAE:', mae)
print('MRE:', mre)
