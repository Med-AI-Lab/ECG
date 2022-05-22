import ECG.api as api
from ECG.data_classes import Diagnosis
from ECG.tests.test_util import get_ecg_signal, get_ecg_array, open_image

def test_convert_image_to_signal():
    image_filename = './ECG/tests/test_data/ecg_image.jpg'
    array_filename = './ECG/tests/test_data/ecg_array.npy'

    signal = get_ecg_array(array_filename)
    image = open_image(image_filename)
    result = api.convert_image_to_signal(image)

    assert (signal == result).all(), 'Recognized signal does not match the original'


def test_check_ST():
    filename = './ECG/tests/test_data/MI.mat'
    sampling_rate = 500
    signal = get_ecg_signal(filename)
    ste = api.check_ST_elevation(signal, sampling_rate)
    ste_expected = 0.225
    assert ste == ste_expected, f"Failed to predict ST probability: expected {ste_expected}, got {ste}"


def test_evaluate_risk_markers():
    filename = './ECG/tests/test_data/MI.mat'
    sampling_rate = 500
    signal = get_ecg_signal(filename)

    risk_markers = api.evaluate_risk_markers(signal, sampling_rate)
    expected = 0.225
    assert risk_markers.Ste60_V3 == expected, f"Failed to predict STE60 V3: expected {expected}, got {risk_markers.Ste60_V3}"
    expected = 501
    assert risk_markers.QTc == expected, f"Failed to predict QTc: expected {expected}, got {risk_markers.QTc}"
    expected = 0.315
    assert risk_markers.RA_V4 == expected, f"Failed to predict RA V4: expected {expected}, got {risk_markers.RA_V4}"


def test_diagnose_with_STEMI():
    filename_stemi = './ECG/tests/test_data/MI.mat'
    filename_er = './ECG/tests/test_data/BER.mat'
    sampling_rate = 500
    signal_stemi = get_ecg_signal(filename_stemi)
    signal_er = get_ecg_signal(filename_er)

    stemi_positive = api.diagnose_with_STEMI(signal_stemi, sampling_rate)
    stemi_negative = api.diagnose_with_STEMI(signal_er, sampling_rate)

    # positive
    assert stemi_positive[0] == Diagnosis.MI, "Failed to recognize MI"
    expected_explanation = "Criterion value calculated as follows: (2.9 * [STE60 V3 in mm]) + (0.3 * [QTc in ms]) + (-1.7 * np.minimum([RA V4 in mm], 19)) = 151.47 exceeded the threshold 126.9, therefore the diagnosis is Myocardial Infarction"
    assert stemi_positive[1] == expected_explanation, f"Wrong explanation: \n\tExpected {expected_explanation} \n\tGot {stemi_positive[1]}"

    # negative
    assert stemi_negative[0] == Diagnosis.BER, "Failed to recognize BER"
    expected_explanation = "Criterion value calculated as follows: (2.9 * [STE60 V3 in mm]) + (0.3 * [QTc in ms]) + (-1.7 * np.minimum([RA V4 in mm], 19)) = 118.4062869471591 did not exceed the threshold 126.9, therefore the diagnosis is Benign Early Repolarization"
    assert stemi_negative[1] == expected_explanation, f"Wrong explanation: \n\tExpected {expected_explanation} \n\tGot {stemi_negative[1]}"
