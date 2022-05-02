from PIL import Image
import numpy as np
from typing import Tuple
from ECG.criterion_based_approach.pipeline import detect_risk_markers, diagnose, get_ste
from ECG.data_classes import Diagnosis, RiskMarkers
from digitization.preprocessing import open_image, image_rotation, binarization
from digitization.digitization import grid_detection, signal_extraction

def convert_image_to_signal(image: Image.Image) -> np.ndarray:
    image = open_image(image)
    rotated_image = image_rotation(image)
    scale = grid_detection(rotated_image)
    binary_image = binarization(rotated_image)
    ecg_signal = signal_extraction(binary_image, scale)

    return ecg_signal 

def check_ST_elevation(signal: np.ndarray, sampling_rate: int) -> bool:
    return get_ste(signal, sampling_rate)


def evaluate_risk_markers(signal: np.ndarray, sampling_rate: int) -> RiskMarkers:
    return detect_risk_markers(signal, sampling_rate)


def diagnose_with_STEMI(signal: np.ndarray, sampling_rate: int) -> Tuple[Diagnosis, str]:
    risk_markers = evaluate_risk_markers(signal, sampling_rate)
    stemi_diagnosis, stemi_criterion = diagnose(risk_markers)

    diagnosis_enum = Diagnosis.MI if stemi_diagnosis else Diagnosis.BER
    explanation = 'Criterion value calculated as follows: ' + \
        '(1.196 * [STE60 V3 in mm]) + (0.059 * [QTc in ms]) - (0.326 * min([RA V4 in mm], 15)) = ' + str(stemi_criterion) + \
        (' exceeded ', ' did not exceed ')[stemi_diagnosis] + \
        'the threshold 28.13, therefore the diagnosis is ' + diagnosis_enum.value

    return (diagnosis_enum, explanation)


def diagnose_with_NN(s: np.ndarray) -> Tuple[Diagnosis, Image.Image]:
    raise NotImplementedError()
