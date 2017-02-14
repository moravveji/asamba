
import sys, os, glob
import logging
import numpy as np 

from grid import var_def, var_lib, db_def, db_lib

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
logger = logging.getLogger(__name__)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# R O U T I N E S   T O   I N T E R A C T   W I T H   T H E   D A T A B A S E
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def prepare_insert_models():
  """
  "Prepare" a command that allows inserting any row into the models table. This is to facilitate
  much faster interaction with the database.
  """     
  # model_attrs = var_lib.get_model_attrs()
  # n_tot       = len(model_attrs)  # see the grid.sql file and the attribute types for models table
  # base_attrs  = var_lib.get_model_basic_attrs()
  # n_base      = len(base_attrs)
  other_attrs = var_lib.get_model_other_attrs()
  n_other     = len(other_attrs)

  # The 4 track attributes are retrieved by the id_track, so we must skip them. The other three 
  # attributes (i.e. id_trac, Xc and model_number) are inserted first, and so are the whole other attributes

  # creating a concatenated string for all variable types in order
  str_types   = 'int,real,int,' + ','.join(['real']*n_other)
  avail_attrs = ['id_track', 'Xc', 'model_number'] + var_lib.get_model_other_attrs() 
  n_attrs     = len(avail_attrs)
  str_attrs   = ','.join(avail_attrs)
  # str_qmarks  = ','.join(['?']*n_attrs)
  str_qmarks  = ','.join([ '${0}'.format(i+1) for i in range(n_attrs) ])

  cmnd = 'prepare prepare_insert_models ({0}) as \
          insert into models ({1}) values ({2})'.format(
          str_types, str_attrs, str_qmarks)
  
  return cmnd

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def get_execute_insert_model_command(tup_vals):
  """
  """
  n_tup = len(tup_vals)
  cmnd  = 'execute prepare_insert_models ({0})'.format(','.join(['%s'] * n_tup))

  return cmnd

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def insert_row_into_models(dbobj, model):
  """
  Insert one row into the models table of the database, by transfering the data contained in the model
  object (2nd argument). This function only performs the SQL insert operation, and does not commit. This
  helps a fast and efficient insertion. The user must do the commit() himself, else, the changes will 
  not be applied.

  @param dbojb: an instance of the db_def.grid_db class.
  @type dbobj: object
  @param model: an instance of the var_def.model class, which already contains the information of the row
  @type model: object
  @return: None
  @rtype: NoneType
  """
  attrs  = ['id_tracks', 'Xc', 'model_number'] + var_lib.get_model_other_attrs()

  M_ini  = model.M_ini
  fov    = model.fov
  Z      = model.Z
  logD   = model.logD
  id_track = db_lib.get_track_id(dbname_or_dbobj=dbobj, M_ini=M_ini, fov=fov, Z=Z, logD=logD)
  # print id_track

  vals   = [id_track]
  for i, attr in enumerate(attrs[1:]): 
    val  = getattr(model, attr)
    vals.append(val)

  tup    = tuple(vals)
  cmnd   = get_execute_insert_model_command(tup)
  dbobj.execute_one(cmnd, tup, commit=False)

  logger.info('insert_row_into_models: Adding: id_track={0}, Xc={1}'.format(id_track, model.Xc))

  return None

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def prepare_insert_tracks(include_id=False):
  """
  Execute the SQL "Prepare" statement in order to prepare for inserting rows into the tracks
  table

  @param include_id: (default False) Set True to include the attribute "id" as a part of the 
         prepare statement, or False to exclude it. Note that if "id" is included, during the 
         insertion operation, it should be also included accordingly.
  @type include_id: boolean      
  @return: the prepare_insert_tracks command to be executed independently
  @rtype: string
  """
  if include_id:
    cmnd   = 'prepare prepare_insert_tracks (integer, real, real, real, real) as \
              insert into tracks (id, M_ini, fov, Z, logD) values \
              ($1, $2, $3, $4, $5)'
  else:
    cmnd   = 'prepare prepare_insert_tracks (real, real, real, real) as \
              insert into tracks (M_ini, fov, Z, logD) values \
              ($1, $2, $3, $4)'

  return cmnd

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def insert_row_into_tracks(dbname_or_dbobj, id, M_ini, fov, Z, logD):
  """
  Inset one row into the "tracks" table of the database

  @param dbname_or_dbobj: The name of the database, or an instance of the database connection
  @type dbname_or_dbobj: string or object
  @param id: track id (declared serial in the SQL schema). If None, then its value is assigned by 
         SQL internally. If set to an integer, the passed value is enforced.
  @type id: int or None
  @param M_ini: initial mass of the track (in solar mass)
  @type M_ini: float
  @param fov: exponential overshoot free parameter
  @type fov: float
  @param Z: metallicity (with the standard solar metallicity 0.014)
  @type Z: float
  @param logD: the logarithm of the extra diffusive mixing
  @type logD: float
  @return: None
  """
  if isinstance(id, type(None)):
    cmnd = 'insert into tracks (M_ini, fov, Z, logD) values (%s, %s, %s, %s)'
    tup  = (M_ini, fov, Z, logD)
  elif isinstance(id, int):
    cmnd = 'insert into tracks (id, M_ini, fov, Z, logD) values (%s, %s, %s, %s, %s)'
    tup  = (id, M_ini, fov, Z, logD)
  else:
    logger.error('insert_row_into_tracks: Input argument id has unexpected type')
    sys.exit(1)

  if isinstance(dbname_or_dbobj, str):
    with db_def.grid_db(dbname=dbname_or_dbobj) as the_db:
      the_db.execute_one(cmnd, tup)
  elif isinstance(dbname_or_dbobj, db_def.grid_db):
    dbname_or_dbobj.execute_one(cmnd, tup)
  else:
    logger.error('insert_row_into_tracks: Input argument dbname_or_dbobj has a wrong type!')
    sys.exit(1)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# R O U T I N E S   T O   W O R K   W I T H   A N   I N P U T   A S C I I   F I L E
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def insert_models_from_models_parameter_file(dbname, ascii_in):
  """
  This function starts from an ASCII input file (which is most probably prepared by calling 
  write.write_model_parameters_to_ascii), and insert each line as a row into the "models" table of 
  the database. For example, one can use this function like the following:

  >>>from grid import insert_lib
  >>>param_file = '/home/user/my-projects/grid-models-parameters.txt'
  >>>insert_lib.insert_models_from_models_parameter_file(dbname='grid', ascii_in=param_file)

  @param dbname: the name of the database which contains the "models" table. Normally, it is called
         "grid"
  @type dbname: string
  @param ascii_in: The full path to the ASCII file containing the models parameters, and the additional
         columns. Only the unique M_ini, fov, Z and logD attributes are extracted from the rows, and 
         inserted into distinct rows into the "tracks" table.
  @type ascii_in: string
  """
  if not os.path.exists(ascii_in):
    logger.error('insert_models_from_models_parameter_file: "{0}" does not exist'.format(ascii_in))
    sys.exit(1)
  else:     # get the file handle
    n_rows = sum((1 for i in open(ascii_in, 'rb'))) - 1
    handle = open(ascii_in, 'r')

  try:
    assert db_def.exists(dbname=dbname) == True
    logger.info('insert_models_from_models_parameter_file: database "{0}" exists.'.format(dbname))
  except:
    logger.error('insert_models_from_models_parameter_file: failed to instantiate database "{0}".'.format(dbname))
    sys.exit(1)

  with db_def.grid_db(dbname=dbname) as the_db:
    try:
      assert the_db.has_table('models')
    except AssertionError:
      logger.error('insert_models_from_models_parameter_file: \
                    Table "{0}" not found in the database "{1}"'.format('models', dbname))
      sys.exit(1)

  # open the file, and get the file handle
  handle   = open(ascii_in, 'r')
  tups     = []

  # walk over the input file, and insert each row one after the other
  i        = -1
  with db_def.grid_db(dbname=dbname) as the_db:

    # prepare the database to receive a lot of insertions
    cmnd   = prepare_insert_models()
    the_db.execute_one(cmnd, None)

    # iterate over each line and insert it into the database
    while  True:
      i      += 1
      if i <= 0:      # skip the header
        hdr  = handle.readline()
        continue

      line   = handle.readline()
      if not line: break     # exit by the End-of-File (EOF)
      # row    = line.rstrip('\r\n').split()

      with model_line_to_model_object(line) as model:
        insert_row_into_models(the_db, model)
        print model.Xc

      # progress bar on the stdout
      sys.stdout.write('\r')
      sys.stdout.write('progress = {0:.2f} % '.format(100. * float(i)/n_rows))
      sys.stdout.flush()

  handle.close()
  logger.info('insert_models_from_models_parameter_file: "{0}" rows inserted into models table'.format(i-1))

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def insert_tracks_from_models_parameter_file(dbname, ascii_in):
  """
  Insert distinct track rows into the *tracks* table in the grid database. The four track attributes
  are taken from 
  This routine is protected agains *Injection Attacks*. Example of use is:

  >>>from grid import insert_lib
  >>>param_file = '/home/user/my-projects/grid-models-parameters.txt'
  >>>insert_lib.insert_tracks_from_models_parameter_file(dbname='grid', ascii_in=param_file)

  @param dbname: the name of the database which contains the "tracks" table. Normally, it is called
         "grid"
  @type dbname: string
  @param ascii_in: The full path to the ASCII file containing the models parameters, and the additional
         columns. Only the unique M_ini, fov, Z and logD attributes are extracted from the rows, and 
         inserted into distinct rows into the "tracks" table.
  @type ascii_in: string
  """
  if not os.path.exists(ascii_in):
    logger.error('insert_tracks_from_models_parameter_file: "{0}" does not exist'.format(ascii_in))
    sys.exit(1)

  try:
    assert db_def.exists(dbname=dbname) == True
    logger.info('insert_tracks_from_models_parameter_file: database "{0}" exists.'.format(dbname))
  except:
    logger.error('insert_tracks_from_models_parameter_file: failed to instantiate database "{0}".'.format(dbname))
    sys.exit(1)

  with db_def.grid_db(dbname=dbname) as the_db:
    try:
      assert the_db.has_table('tracks')
    except AssertionError:
      logger.error('insert_tracks_from_models_parameter_file: \
                    Table "{0}" not found in the database "{1}"'.format('tracks', dbname))
      sys.exit(1)

  # open the file, and get the file handle
  handle   = open(ascii_in, 'r')
  # iterate over each row in the file, and construct the insertion command
  # unique   = set()
  tups     = []

  i        = -1
  while True:
    i      += 1
    if i <= 0:     # skip the header
      hdr  = handle.readline()
      continue    

    line   = handle.readline()
    if not line: break      # exit by the End-of-File (EOF)
    row    = line.rstrip('\r\n').split()

    M_ini  = float(row[0])
    fov    = float(row[1])
    Z      = float(row[2])
    logD   = float(row[3])
    tup    = (M_ini, fov, Z, logD)

    # progress bar on the stdout
    sys.stdout.write('\r')
    sys.stdout.write('progress = {0:.2f} % '.format(100. * i/3.845e6))
    sys.stdout.flush()

    # make sure the insert row is unique. the following statement is too inefficient, but is OK
    # because the tracks table is gonna be filled up only once. On the plus side, the following 
    # statement keeps the same ordering of the ascii file intact, so, tracks are enumerated as 
    # they appear in the file. The alternative/efficient way (list --> set --> list) would be super
    # efficient, but does not guarantee the order (set rule)
    # if tup not in tups: tups.append(tup)
    tups.append(tup)

  handle.close()
  print

  # pick only unique sets of the track parameters
  unique   = set(tups)
  tups     = sorted(list(unique))

  n_values = len(tups)
  with db_def.grid_db(dbname=dbname) as the_db:
    
    # prepare an insertion statement into the tracks table
    cmnd   = prepare_insert_tracks(include_id=False)
    the_db.execute_one(cmnd, None)

    # execute many and commit
    logger.info('insert_tracks_from_models_parameter_file: "{0}" tracks recognized'.format(n_values))
    cmnd   = 'execute prepare_insert_tracks ({0})'.format( ','.join( ['%s'] * 4 ))
    the_db.execute_many(cmnd=cmnd, values=tups)
    # the_db.execute_one(cmnd, tups[0])
    logger.info('insert_tracks_from_models_parameter_file: Insertion completed.')

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# A U X I L A R Y    F U N C T I O N S
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def gen_tracks_insert_commands(list_tracks):
  """
  Receive a list of "track" objects, and return a list of SQL insert commands to put the data into the
  "grid.tracks" table.
  @param list_tracks: list of "var_def.track" instances
  @type list_tracks: list
  @return: list of SQL commands, one item to insert one MESA history/track info into the database.
  @rtype: list of strings
  """
  n_tracks = len(list_tracks)
  if n_tracks == 0:
    logger.error('gen_tracks_insert_commands: Input list is empty')
    sys.exit(1)

  list_cmnds = []
  for i, track in enumerate(list_tracks):
    M_ini = track.M_ini
    fov   = track.fov
    Z     = track.Z
    logD  = track.logD
    cmnd  = """insert into tracks (M_ini, fov, Z, logD) \
               values ({0}, {1}, {2}, {3})""".format(M_ini, fov, Z, logD)
    list_cmnds.append(cmnd)

  return list_cmnds

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def model_line_to_model_object(line):
  """
  Convert one row of the ascii parameter file, into an instance of the var_def.model class, and store
  the line values into those of the corresponding attribute. The returned object is useful to insert
  into the SQL database

  @param line: one line of the parameter file, which contains numbers only
  @type line: string
  @return: an instance of the var_def.model class, with the attributes all set from the input line.
  @rtype: object
  """
  if not isinstance(line, str):
    logger.error('model_line_to_model_object: The input is not a string')
    sys.exit(1)
  line        = line.rstrip('\r\n').split()

  # instantiate a model object
  model       = var_def.model()

  # get the model attribute names
  avail_attrs = var_lib.get_model_attrs()

  for i, attr in enumerate(avail_attrs):
    conv      = float
    if attr   == 'model_number': conv = int 
    val       = conv(line[i])
    setattr(model, attr, val)

  return model

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%







