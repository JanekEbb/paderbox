"""

>>> from pathlib import Path
>>> p = Path('/') / 'net' # /storage/python_unittest_data
>>> p
>>> p = p / 'storage'
>>> p
>>> str(p)

"""

import os
from pathlib import Path


testing = Path(os.getenv(
    'NT_TESTING_DIR',
    '/net/storage/python_unittest_data'
))
timit = Path(os.getenv(
    'NT_TIMIT_DIR',
    '/net/db/timit'
))
tidigits = Path(os.getenv(
    'NT_TIDIGITS_DIR',
    '/net/db/tidigits'
))
database_jsons = Path(os.getenv(
    'NT_DATABASE_JSONS_DIR',
    '/net/storage/database_jsons'
))
chime_3 = Path(os.getenv(
    'NT_CHIME_3_DIR',
    '/net/db/chime3'
))
chime_4 = Path(os.getenv(
    'NT_CHIME_4_DIR',
    '/net/db/chime4'
))
kaldi_root = Path(os.getenv(
    'KALDI_ROOT',
    '/net/ssd/jheymann/software/kaldi_latest'
    # '/net/ssd/software/kaldi'
))
merl_mixtures = Path(os.getenv(
    'NT_MERL_MIXTURES_DIR',
    '/net/db/merl_speaker_mixtures'
))
german_speechdata = Path(os.getenv(
    'NT_GERMAN_SPEECHDATA_DIR',
    '/net/storage/jheymann/speech_db/german-speechdata-package-v2/'
))
noisex92 = Path(os.getenv(
    'NT_NoiseX_92_DIR',
    '/net/db/NoiseX_92'
))
wsj = Path(os.getenv(
    'NT_WSJ_DIR',
    '/net/db/wsj'
))
dcase = Path(os.getenv(
    'NT_DCASE_DIR',
    '/home/parora/Documents/DCASE/DCASE 2016/'
))
matlab_toolbox = Path(os.getenv(
    'MATLAB_TOOLBOX_DIR',
    '/net/ssd/software/matlab_toolbox'
))
matlab_r2015a = Path(os.getenv(
    'MATLAB_R2015a',
    '/net/ssd/software/MATLAB/R2015a'
))
matlab_license = Path(os.getenv(
    'MATLAB_LICENSE',
    '/opt/MATLAB/R2016b_studis/licenses/network.lic'
))
language_model = Path(os.getenv(
    'LANGUAGE_MODEL',
    '/net/storage/jheymann/__share/ldrude/2016/2016-05-10_lm'
))

if __name__ == "__main__":
    import doctest

    doctest.testmod()
