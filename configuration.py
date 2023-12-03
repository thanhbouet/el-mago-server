import os 
DIR_PATH = os.path.dirname(os.path.realpath(__file__))

ENHANCE_FACE_RES_DIR = DIR_PATH + "\\enhance_image\\res"
ENHANCE_FACE_RESTORED_DIR =  ENHANCE_FACE_RES_DIR + "\\restored_imgs"

REMOVE_BG_RES_DIR = DIR_PATH +"\\res_remove"
REMOVE_BG_RESULT_DIR = REMOVE_BG_RES_DIR + "\\result"
REMOVE_BG_INPUT_DIR = REMOVE_BG_RES_DIR + "\\update"

COLORIZE_RES_DIR = DIR_PATH + "\\colorize"
COLORIZE_RESULT_DIR = COLORIZE_RES_DIR + "\\result"

ENHANCE_VIDEO_RES_DIR = DIR_PATH + "\\video_enhance" 
ENHANCE_VIDEO_RESTORED_DIR = ENHANCE_VIDEO_RES_DIR + "\\output" 
ENHANCE_VIDEO_INPUT_DIR = ENHANCE_VIDEO_RES_DIR + "\\input"

INFERENCE_TO_GFPGAN = "D:\\hoctap\\Python\\GFPGAN\\inference_gfpgan.py"
