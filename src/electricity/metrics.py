import numpy as np
from sklearn.metrics import confusion_matrix


def acc_precision_recall_f1_score(status, status_pred):
    """Calculate a variety of machine learning performance scores"""
    assert status.shape == status_pred.shape

    if type(status) != np.ndarray:
        status = status.detach().cpu().numpy().squeeze()
    if type(status_pred) != np.ndarray:
        status_pred = status_pred.detach().cpu().numpy().squeeze()

    status = status.reshape(status.shape[0], -1)
    status_pred = status_pred.reshape(status_pred.shape[0], -1)
    accs, precisions, recalls, f1_scores = [], [], [], []

    for i in range(status.shape[0]):
        tn, fp, fn, tp = confusion_matrix(
            status[i, :], status_pred[i, :], labels=[0, 1]
        ).ravel()
        acc = (tn + tp) / (tn + fp + fn + tp)
        precision = tp / np.max((tp + fp, 1e-9))
        recall = tp / np.max((tp + fn, 1e-9))
        f1_score = 2 * (precision * recall) / np.max((precision + recall, 1e-9))

        accs.append(acc)
        precisions.append(precision)
        recalls.append(recall)
        f1_scores.append(f1_score)

    return np.array(accs), np.array(precisions), np.array(recalls), np.array(f1_scores)


def regression_errors(pred, label):
    """Calculate the mean absolute error and mean relative error"""
    assert pred.shape == label.shape

    if type(pred) != np.ndarray:
        pred = pred.detach().cpu().numpy().squeeze()
    if type(label) != np.ndarray:
        label = label.detach().cpu().numpy().squeeze()

    pred = pred.reshape(pred.shape[0], -1)
    label = label.reshape(label.shape[0], -1)
    epsilon = np.full(label.shape, 1e-9)
    mean_absolute_error_array, mean_relative_error_array = [], []

    for i in range(label.shape[0]):
        abs_diff = np.abs(label[i, :] - pred[i, :])
        mean_absolute_error = np.mean(abs_diff)
        mean_relative_error_num = np.nan_to_num(abs_diff)
        mean_relative_error_den = np.max(
            (label[i, :], pred[i, :], epsilon[i, :]), axis=0
        )
        mean_relative_error = np.mean(mean_relative_error_num / mean_relative_error_den)
        mean_absolute_error_array.append(mean_absolute_error)
        mean_relative_error_array.append(mean_relative_error)

    return np.array(mean_absolute_error_array), np.array(mean_relative_error_array)
