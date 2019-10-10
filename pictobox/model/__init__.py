#
# This module contains utilities and functions pertaining to the
# machine learning portion of the program. It also contains the
# trained model, as 'model.h5'.
#

import numpy as np
import tensorflow as tf
import cv2
from PIL import Image

CLASS_NAMES = [
  'big_poe',
  'blue_fire',
  'blue_potion',
  'bomb',
  'bomb_bag',
  'bombchu',
  'boomerang',
  'bottled_fairy',
  'bug',
  'bunny_hood',
  'claim_check',
  'cojiro',
  'cucco',
  'deku_nut',
  'deku_stick',
  'dins_fire',
  'empty',
  'empty_bottle',
  'eyeball_frog',
  'eyedrops',
  'fairy_bow',
  'fairy_bow_and_fire_arrow',
  'fairy_bow_and_ice_arrow',
  'fairy_bow_and_light_arrow',
  'fairy_ocarina',
  'fairy_slingshot',
  'farores_wind',
  'fire_arrow',
  'fish',
  'gerudo_mask',
  'goron_mask',
  'green_potion',
  'hookshot',
  'ice_arrow',
  'keaton_mask',
  'lens_of_truth',
  'light_arrow',
  'longshot',
  'magic_beans',
  'mask_of_truth',
  'megaton_hammer',
  'milk',
  'milk_half',
  'nayrus_love',
  'ocarina_of_time',
  'odd_mushroom',
  'odd_potion',
  'poachers_saw',
  'poe',
  'prescription',
  'red_potion',
  'rutos_letter',
  'skull_mask',
  'sold_out',
  'spooky_mask',
  'weird_egg',
  'zeldas_letter',
  'zora_mask'
]

def normalizeImage(image):
  img = np.array(image.resize((49, 49), Image.ANTIALIAS))[:,:,:3]

  # Red and blue channels are reverse of keras format so we have to flip them
  red = img[:,:,2].copy()
  blue = img[:,:,0].copy()

  img[:,:,0] = red
  img[:,:,2] = blue

  img = np.reshape(img, (1, 49, 49, 3))
  
  return img/255.

def flipChannels(image):
  image = np.array(image)[:,:,:3]

  red = image[:,:,2].copy()
  blue = image[:,:,0].copy()

  image[:,:,0] = red
  image[:,:,2] = blue

  return Image.fromarray(image)