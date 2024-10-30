"""Module that allows inference with own data on previously trained models."""

from types import SimpleNamespace
import pandas as pd
import torch
from .Electricity_model import ELECTRICITY
from .NILM_Dataset import NILMDataset
from .parsers import PChaingerParser

# set precision
torch.set_default_tensor_type(torch.DoubleTensor)


def inference(config: dict) -> pd.DataFrame:
    """NILM inference with your own data

        Args:
            config: Configuration for inference. Must be of format:
                config = {
                    # Aggregated data
                    "data_file": here("path/to/data.csv"),

                    # Saved model from previous training
                    "model_file": here("path/to/best_acc_model.pth"),

                    # Inference device
                    "device": "cpu",  # or "gpu"

                    # Re-sample data if necessary
                    "sampling": "6s",

                    # Keep aggregated data below this threshold
                    "cutoff": [2000],

                    # Normalization
                    "normalize": "mean"  # or "minmax"
                }

        Returns:
            A pandas dataframe containing the inferred data.
    """
    # network configuration
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

    ds_parser = PChaingerParser(
        sampling=config["sampling"],
        normalize="mean",
        cutoff=config["cutoff"],
        drop_last=True,
        location=config["data_file"],
        val_size=1,
        separator=",",
        window_size=480,
        window_stride=240,
    )

    # create model
    model = ELECTRICITY(args)

    # load model with previously trained data
    model.load_state_dict(torch.load(config["model_file"], map_location=torch.device(config["device"])))

    # bring our own dataset in a format that the dataloader can understand
    inference_data = NILMDataset(
        x=ds_parser.x, y=[0] * len(ds_parser.x), status=[0] * len(ds_parser.x), window_size=480, stride=480
    )

    inference_dataloader = torch.utils.data.DataLoader(
        dataset=inference_data,
        batch_size=480,
    )

    # put the model in evaluation mode
    model.eval()

    # evaluate in batches
    batches = []
    for batch in inference_dataloader:
        batches.append(model(batch[0].to("cpu")))

    # assemble output data from batches
    data = []
    for batch in batches:
        for chunk in batch[0]:
            data += list(chunk[0].tolist())

    # "undo" normalizations
    if ds_parser.normalize == "mean":
        print(ds_parser.x_std)
        print(ds_parser.x_mean)
        rescaled_data = [data_point * ds_parser.x_std + ds_parser.x_mean for data_point in data]
    elif ds_parser.normalize == "minmax":
        rescaled_data = [data_point * (ds_parser.x_max - ds_parser.x_min) + ds_parser.x_min for data_point in data]
    else:
        rescaled_data = data

    return pd.DataFrame(rescaled_data, index=ds_parser.index, columns=["inference"])
