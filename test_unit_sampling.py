
import sys, os, glob
import logging
import numpy as np 

from grid import sampler
from grid import star
from grid import plot_sampler

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def main():

  print ' - Load the mode list from a file'
  mode_file = 'stars/KIC_10526294.freq'
  modes     = star.load_modes_from_file(filename=mode_file, delimiter=',')

  print ' - Attach the modes to a star object'
  TheStar   = star.star()
  TheStar.setter('name', 'KIC_10526294')
  TheStar.setter('modes', modes)

  print ' - Get an instance of the "sampling" class.'
  TheSample = sampler.sampling()
  TheSample.setter('dbname', 'grid')
  TheSample.setter('sampling_func', sampler.constrained_pick_models_and_rotation_ids)
  TheSample.setter('max_sample_size', 5000)
  TheSample.setter('range_log_Teff', [4.0, 4.15])
  TheSample.setter('range_log_g', [3.0, 4.0])
  TheSample.setter('range_eta', [0, 0])

  TheSample.setter('star', TheStar)

  # seismic constraints
  TheSample.setter('modes_id_types', [2])   # for l=1, m=0: dipole zonal modes  

  # search plan for matching frequencies
  TheSample.setter('search_strictly_for_dP', True)

  # For non-rotating models, exclude eta column (which is just 0.0) to avoid singular X matrix
  TheSample.setter('exclude_eta_column', True)

  # Now, build the learning sets
  TheSample.build_learning_set()

  # Get the sample
  learning_x  = TheSample.get('learning_x')
  print '   Size of the retrieved sample is: "{0}"'.format(TheSample.sample_size)
  print '   Names of the sampled columns: ', learning_x.dtype.names

  # Get the corresponding frequencies
  learning_y = TheSample.get('learning_y')
  print '   Shape of the synthetic frequencies is: ', learning_y.shape 
  print '   '

  # Plot the histogram of the learning Y sample
  plot_sampler.hist_learning_y(TheSample, 'plots/KIC-10526294-hist-Y.png')

  # Set percentages for training, cross-validation and test sets
  TheSample.setter('training_percentage', 0.80)
  TheSample.setter('cross_valid_percentage', 0.15)
  TheSample.setter('test_percentage', 0.05)

  # Now, create the three sets from the learning set
  TheSample.split_learning_sets()

  # Print sizes of each learning sets
  print '   The Training set: X:{0}, Y:{1}'.format(TheSample.training_x.shape, TheSample.training_y.shape)
  print '   The Cross-Validation set: X:{0}, Y:{1}'.format(TheSample.cross_valid_x.shape, TheSample.cross_valid_y.shape)
  print '   The Test set: X:{0}, Y:{1}'.format(TheSample.test_x.shape, TheSample.test_y.shape)
  print 

  return TheSample

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if __name__ == '__main__':
  status = main()
  sys.exit(status)
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
