#!/usr/bin/env python3

import pickle as pkl
import torch
from pyprojroot import here
from electricity.config import setup_seed
from electricity.Electricity_model import ELECTRICITY
from electricity.NILM_Dataloader import NILMDataloader
from electricity.parsers import UKDaleParser
from electricity.Trainer import Trainer

torch.set_default_tensor_type(torch.DoubleTensor)
with open(here("results_UK-DALE_TitanV_kettle/uk_dale/kettle/results.pkl"), "rb") as f:
    res = pkl.load(f)

args = res["args"]
args.ukdale_location = here(args.ukdale_location)

# override computing device
args.device = "cpu"
args.pretrain_num_epochs = 0
args.num_epochs = 0
args.validation_size = 1
args.hidden = 256

setup_seed(args.seed)

args.house_indices = [2]
args.validation_size = 0.1
ds_parser = UKDaleParser(args)

model = ELECTRICITY(args)
trainer = Trainer(args, ds_parser, model)

# Why is this necessary?
model.pretrain = False

dataloader = NILMDataloader(args, ds_parser)
_, test_loader = dataloader.get_dataloaders()
mre, mae, acc, prec, recall, f1 = trainer.test(test_loader, map_location="cpu")

print("Mean Accuracy:", acc)
print("Mean F1-Score:", f1)
print("MAE:", mae)
print("MRE:", mre)
