import os
import configuration

DIR = configuration.COLORIZE_MODEL_DIR
PROTOTXT = os.path.join(DIR,'colorization_deploy_v2.prototxt.txt')
POINTS = os.path.join(DIR,'pts_in_hull.npy')
MODEL = os.path.join(DIR,'colorization_release_v2.caffemodel')

def colorizePhoto(input, output):

    cmdExec = "python " + configuration.COLORIZE_PATH_TO_SCRIPT + " -i " + input + " -o " + output
    os.system(cmdExec)
    
    return output
