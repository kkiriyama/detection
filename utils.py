import numpy as np
import pandas as pd
import os
import glob
from PIL import Image
from tqdm import tqdm

for i in range(1, 8):
  files = os.listdir('./keras-yolo3_modified/train/location%d/images'%(i))
  for f in tqdm(files):
    img = Image.open(f)
    img_resize = img.resize((416, 416))
    img_resize.save(f)
