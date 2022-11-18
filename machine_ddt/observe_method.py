import numpy as np
import dl_script


def static_compare(origin_image: np.ndarray, compare_image: np.ndarray):
    similarity = np.sum(origin_image == compare_image) / origin_image.size
    return similarity


def onnx_recognize(cut_image, onnx_model_fp, character_dict_fp, input_image_shape, algorithm="CTC"):
    session = dl_script.load_onnx(onnx_model_fp)
    preprocess_func = dl_script.build_preprocess(algorithm=algorithm)
    postprocess_func = dl_script.build_postprocess(character_dict_fp, algorithm=algorithm)

    norm_image = preprocess_func(cut_image, input_image_shape)
    input_name = session.get_inputs()[0].name
    output = session.run([], {input_name: norm_image})
    res = postprocess_func(output)[0][0]
    return res
