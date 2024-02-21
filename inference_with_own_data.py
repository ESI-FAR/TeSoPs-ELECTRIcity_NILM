import torch
import pandas as pd
import plotly.express as px
import plotly.io as pio

from types import SimpleNamespace

from PChainger_Parser import PChainger_Parser
from Electricity_model import ELECTRICITY
from NILM_Dataset import NILMDataset

torch.set_default_tensor_type(torch.DoubleTensor)


#data_file = "./data/test/geert/main.csv"
#model_file = "./results_UK-DALE_TitanV_kettle/uk_dale/kettle/best_acc_model.pth"

#device = "cpu"


def inference(config):

    args = SimpleNamespace(
        drop_out=0.1,
        heads=2,
        hidden=256,
        n_layers=2,
        output_size=1,
        pretrain=False,
        window_size=480,
    )

    # `drop_last = True` will drop the last part of the data that
    # does not fit in the window_size anymore!

    ds_parser = PChainger_Parser(
        sampling=config["sampling"],
        normalize="mean",
        cutoff=config["cutoff"],
        drop_last=True,
        location=config["data_file"],
        val_size=1,
        separator=",",
        window_size=480,
        window_stride=240
    )

    model = ELECTRICITY(args)
    model.load_state_dict(torch.load(config["model_file"], map_location=torch.device(config["device"])))

    inference_data = NILMDataset(
        x=ds_parser.x,
        y=[0] * len(ds_parser.x),
        status=[0] * len(ds_parser.x),
        window_size=480,
        stride=480
    )

    inference_dataloader = torch.utils.data.DataLoader(
        dataset=inference_data,
        batch_size=480,
    )

    out = model.eval()

    batches = []
    for batch in inference_dataloader:
        batches.append(model(batch[0].to("cpu")))

    data = []
    for batch in batches:
        for chunk in batch[0]:
            data += list(chunk[0].tolist())

    # "undo" normalizations
    if ds_parser.normalize == "mean":
        print(ds_parser.x_std)
        print(ds_parser.x_mean)
        rescaled_data = [data_point * ds_parser.x_std + ds_parser.x_mean \
                         for data_point in data]
    elif ds_parser.normalize == "minmax":
        rescaled_data = [data_point * (ds_parser.x_max - ds_parser.x_min) \
                + ds_parser.x_min for data_point in data]
    else:
        rescaled_data = data

    return pd.DataFrame(data, index=ds_parser.index,
                        columns=["inference"])
