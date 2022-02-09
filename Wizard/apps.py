from django.apps import AppConfig
import os
import tensorflow as tf
from . import config as ModelConfig
from . import model as CNNModel
import csv
import requests
# https://drive.google.com/file/d/1gz4ab_3Kiq3NA6jW8lzNIczj8P46msBp/view?usp=sharing
MODEL_FILE_ID = "1gz4ab_3Kiq3NA6jW8lzNIczj8P46msBp"
MODULE_DIR = os.path.dirname(__file__) 
destination = os.path.join(MODULE_DIR, 'mask_rcnn_taco_0021.h5')

class WizardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Wizard'
    def __init__(self, app_name, app_module):
        super(WizardConfig, self).__init__(app_name, app_module)
        self.graph = None
        self.config = None
        self.model = None
        self.class_map = {}

    def ready(self):
        if self.graph is None:
            if not os.path.exists(destination):
                print("[TACO LOG] start to download the model ...")
                download_file_from_google_drive(MODEL_FILE_ID, destination)
                print("[TACO LOG] Download completes ...")
            else:
                print("[TACO LOG] Download completed before ...")
            print("[TACO LOG] start to load the model ...")
            print(os.listdir(MODULE_DIR))
            TRAINED_MODEL_PATH = os.path.join(MODULE_DIR, 'mask_rcnn_taco_0021.h5')
            DEFAULT_LOGS_DIR = os.path.join(MODULE_DIR, './logs')
            CLASS_MAP_PATH = os.path.join(MODULE_DIR, 'map_10.csv')

            class TacoTestConfig(ModelConfig.Config):
                NAME = "taco"
                GPU_COUNT = 1
                IMAGES_PER_GPU = 1
                DETECTION_MIN_CONFIDENCE = 10
                NUM_CLASSES = 11
                USE_OBJECT_ZOOM = False
            self.config = TacoTestConfig()

            self.model = CNNModel.MaskRCNN(mode="inference", config=self.config, model_dir=DEFAULT_LOGS_DIR)
            self.model.load_weights(TRAINED_MODEL_PATH, TRAINED_MODEL_PATH, by_name=True)
            self.graph = tf.get_default_graph()

            with open(CLASS_MAP_PATH) as csvfile:
                reader = csv.reader(csvfile)
                self.class_map = {row[0]: row[1] for row in reader}
                # map_to_one_class = {c: 'Litter' for c in class_map}

            print("[TACO LOG] loading done ...")


def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

            
