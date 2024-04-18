"""Integration tests for the electricity package."""

from types import SimpleNamespace
import numpy as np
import pandas as pd
import torch
from pyprojroot import here
from electricity.Electricity_model import ELECTRICITY
from electricity.NILM_Dataset import NILMDataset
from electricity.parsers import PChainger_Parser

torch.set_default_tensor_type(torch.DoubleTensor)


def test_powerchainger_smoke():
    """notebooks/Test_Parser.ipynb as a 'smoke test'."""
    data_file = here("tests/test_data/main.csv")
    model_file = here("results_UK-DALE_TitanV_kettle/uk_dale/kettle/best_acc_model.pth")
    expected_file = here('tests/test_data/powerchainger_output.npy')
    device = "cpu"
    args = SimpleNamespace(
        drop_out=0.1,
        heads=2,
        hidden=256,
        n_layers=2,
        output_size=1,
        pretrain=False,
        window_size=480,
    )
    ds_parser = PChainger_Parser(
        sampling="6s",
        normalize="mean",
        cutoff=[3100],
        drop_last=True,
        location=data_file,
        val_size=1,
        separator=",",
        window_size=480,
        window_stride=240
    )

    model = ELECTRICITY(args)
    model.load_state_dict(torch.load(model_file, map_location=torch.device(device)))

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

    model.eval()

    batches = [model(batch[0].to("cpu")) for batch in inference_dataloader]
    data = []
    for batch in batches:
        for chunk in batch[0]:
            data += list(chunk[0].tolist())

    df = pd.DataFrame(data, index=ds_parser.index, columns=["inference"])

    expected = np.load(expected_file)
    assert np.allclose(expected, df.values)
