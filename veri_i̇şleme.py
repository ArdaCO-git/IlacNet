# -*- coding: utf-8 -*-
"""Veri_İşleme"""

#Importlar
#Pip ve importlar orijinal olarak Google Colab'de yapıldığı için Colab dışında çalışmayabilirler

! wget https://repo.anaconda.com/miniconda/Miniconda3-py37_4.8.2-Linux-x86_64.sh
! chmod +x Miniconda3-py37_4.8.2-Linux-x86_64.sh
! bash ./Miniconda3-py37_4.8.2-Linux-x86_64.sh -b -f -p /usr/local
! conda install -c rdkit rdkit -y
import sys
sys.path.append('/usr/local/lib/python3.7/site-packages/')

import networkx as nx
from rdkit import Chem
from rdkit.Chem import Descriptors, AllChem
from rdkit.Chem.Descriptors import qed, MolLogP
from rdkit.Chem import RDConfig
import os
import sys
sys.path.append(os.path.join(RDConfig.RDContribDir, 'SA_Score'))
import sascorer

!pip install selfies
!pip install SmilesPE

from selfies import encoder
from SmilesPE.pretokenizer import atomwise_tokenizer

import numpy as np
import pandas as pd
import os
import tensorflow as tf
import tensorflow_probability as tfp
from tensorflow import clip_by_global_norm
from tensorflow.keras.callbacks import TensorBoard
from tensorflow.keras.initializers import lecun_normal
from tensorflow.keras.optimizers import Adam,SGD
from tensorflow.keras.losses import binary_crossentropy,MAE
from tensorflow.keras.layers import MaxPool1D,Attention,Conv1DTranspose,GRU,LSTM,Conv1D,Bidirectional,Dense,Input,RepeatVector,Reshape,Flatten,AveragePooling1D,GlobalAvgPool1D,GlobalMaxPool1D,Lambda,AlphaDropout,TimeDistributed,Embedding,Activation,BatchNormalization,LayerNormalization
from tensorflow import keras
from tensorflow.keras import Model
from tensorflow.keras.layers import Concatenate as concat
import tensorflow.keras.backend as back
from tensorflow.keras.metrics import BinaryAccuracy
from tensorflow.math import reduce_logsumexp, reduce_mean, reduce_sum
from tensorflow.keras.backend import clip
from tensorflow.linalg import tensor_diag
from tensorflow.nn import softplus
from collections import Counter
import sklearn
from sklearn.mixture import BayesianGaussianMixture, GaussianMixture
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from time import time

from google.colab import drive
drive.mount('/content/drive')

#MAE Veri Seti

moses = pd.read_csv("https://media.githubusercontent.com/media/molecularsets/moses/master/data/train.csv")

moses = moses["SMILES"]
moses.drop_duplicates(inplace = True)

#CSV olarak ChEMBL ana veri seti alınır / https://www.ebi.ac.uk/chembl/g/#browse/compounds/full_state/eyJsaXN0Ijp7InNldHRpbmdzX3BhdGgiOiJFU19JTkRFWEVTX05PX01BSU5fU0VBUkNILkNPTVBPVU5EX0NPT0xfQ0FSRFMiLCJjdXN0b21fcXVlcnkiOiIqIiwidXNlX2N1c3RvbV9xdWVyeSI6dHJ1ZSwic2VhcmNoX3Rlcm0iOiIiLCJhdF9sZWFzdF9vbmVfZmFjZXRfaXNfc2VsZWN0ZWQiOnRydWUsImZhY2V0c19zdGF0ZSI6eyJtb2xlY3VsZV90eXBlIjp7ImVzX2luZGV4IjoiY2hlbWJsX21vbGVjdWxlIiwiZXNfcHJvcGVydHlfbmFtZSI6Im1vbGVjdWxlX3R5cGUiLCJmYWNldGluZ190eXBlIjoiQ0FURUdPUlkiLCJwcm9wZXJ0eV90eXBlIjp7ImludGVnZXIiOmZhbHNlLCJ5ZWFyIjpudWxsLCJhZ2dyZWdhdGFibGUiOnRydWV9LCJpc1llYXIiOm51bGwsInNvcnQiOiJhc2MiLCJpbnRlcnZhbHMiOjIwLCJyZXBvcnRfY2FyZF9lbnRpdHkiOm51bGwsImZhY2V0aW5nX2tleXNfaW5vcmRlciI6WyItIE4vQSAtIiwiQW50aWJvZHkiLCJDZWxsIiwiRW56eW1lIiwiT2xpZ29udWNsZW90aWRlIiwiT2xpZ29zYWNjaGFyaWRlIiwiUHJvdGVpbiIsIlNtYWxsIG1vbGVjdWxlIiwiVW5jbGFzc2lmaWVkIiwiVW5rbm93biJdLCJmYWNldGluZ19kYXRhIjp7IlNtYWxsIG1vbGVjdWxlIjp7ImluZGV4IjowLCJjb3VudCI6MTkxOTcwMSwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IlNtYWxsIG1vbGVjdWxlIiwia2V5IjoiU21hbGwgbW9sZWN1bGUiLCJpZCI6IlNtYWxsIG1vbGVjdWxlOjE5MTk3MDEifSwiUHJvdGVpbiI6eyJpbmRleCI6MSwiY291bnQiOjIyNjA0LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiUHJvdGVpbiIsImtleSI6IlByb3RlaW4iLCJpZCI6IlByb3RlaW46MjI2MDQifSwiVW5rbm93biI6eyJpbmRleCI6MiwiY291bnQiOjE3OTg4LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiVW5rbm93biIsImtleSI6IlVua25vd24iLCJpZCI6IlVua25vd246MTc5ODgifSwiQW50aWJvZHkiOnsiaW5kZXgiOjMsImNvdW50Ijo4MjgsInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiJBbnRpYm9keSIsImtleSI6IkFudGlib2R5IiwiaWQiOiJBbnRpYm9keTo4MjgifSwiT2xpZ29udWNsZW90aWRlIjp7ImluZGV4Ijo0LCJjb3VudCI6MTI4LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiT2xpZ29udWNsZW90aWRlIiwia2V5IjoiT2xpZ29udWNsZW90aWRlIiwiaWQiOiJPbGlnb251Y2xlb3RpZGU6MTI4In0sIkVuenltZSI6eyJpbmRleCI6NSwiY291bnQiOjEwOCwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IkVuenltZSIsImtleSI6IkVuenltZSIsImlkIjoiRW56eW1lOjEwOCJ9LCJPbGlnb3NhY2NoYXJpZGUiOnsiaW5kZXgiOjYsImNvdW50Ijo2OSwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6Ik9saWdvc2FjY2hhcmlkZSIsImtleSI6Ik9saWdvc2FjY2hhcmlkZSIsImlkIjoiT2xpZ29zYWNjaGFyaWRlOjY5In0sIkNlbGwiOnsiaW5kZXgiOjcsImNvdW50IjoyOSwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IkNlbGwiLCJrZXkiOiJDZWxsIiwiaWQiOiJDZWxsOjI5In0sIi0gTi9BIC0iOnsiaW5kZXgiOjgsImNvdW50Ijo1LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiLSBOL0EgLSIsImtleSI6Ii0gTi9BIC0iLCJpZCI6Ii0gTi9BIC06NSJ9LCJVbmNsYXNzaWZpZWQiOnsiaW5kZXgiOjksImNvdW50IjoyLCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiVW5jbGFzc2lmaWVkIiwia2V5IjoiVW5jbGFzc2lmaWVkIiwiaWQiOiJVbmNsYXNzaWZpZWQ6MiJ9fSwiaW50ZXJ2YWxzTGltaXRzIjpudWxsfSwibWF4X3BoYXNlIjp7ImVzX2luZGV4IjoiY2hlbWJsX21vbGVjdWxlIiwiZXNfcHJvcGVydHlfbmFtZSI6Im1heF9waGFzZSIsImZhY2V0aW5nX3R5cGUiOiJJTlRFUlZBTCIsInByb3BlcnR5X3R5cGUiOnsiaW50ZWdlciI6dHJ1ZSwieWVhciI6bnVsbCwiYWdncmVnYXRhYmxlIjp0cnVlfSwiaXNZZWFyIjpudWxsLCJzb3J0IjpudWxsLCJpbnRlcnZhbHMiOm51bGwsInJlcG9ydF9jYXJkX2VudGl0eSI6bnVsbCwiZmFjZXRpbmdfa2V5c19pbm9yZGVyIjpbIjAiLCIxIiwiMiIsIjMiLCI0Il0sImZhY2V0aW5nX2RhdGEiOnsiMCI6eyJtaW4iOjAsIm1heCI6MSwiaW5kZXgiOjAsImNvdW50IjoxOTUyODYzLCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiMCIsImtleSI6IjAiLCJpZCI6IjA6MTk1Mjg2MyJ9LCIxIjp7Im1pbiI6MSwibWF4IjoyLCJpbmRleCI6MSwiY291bnQiOjEyNDEsInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiIxIiwia2V5IjoiMSIsImlkIjoiMToxMjQxIn0sIjIiOnsibWluIjoyLCJtYXgiOjMsImluZGV4IjoyLCJjb3VudCI6MTk5Niwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IjIiLCJrZXkiOiIyIiwiaWQiOiIyOjE5OTYifSwiMyI6eyJtaW4iOjMsIm1heCI6NCwiaW5kZXgiOjMsImNvdW50IjoxNDEzLCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiMyIsImtleSI6IjMiLCJpZCI6IjM6MTQxMyJ9LCI0Ijp7Im1pbiI6NCwibWF4Ijo1LCJpbmRleCI6NCwiY291bnQiOjM5NDQsInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiI0Iiwia2V5IjoiNCIsImlkIjoiNDozOTQ0In19LCJpbnRlcnZhbHNMaW1pdHMiOlswLDEsMiwzLDQsNV19LCJtb2xlY3VsZV9wcm9wZXJ0aWVzLm51bV9ybzVfdmlvbGF0aW9ucyI6eyJlc19pbmRleCI6ImNoZW1ibF9tb2xlY3VsZSIsImVzX3Byb3BlcnR5X25hbWUiOiJtb2xlY3VsZV9wcm9wZXJ0aWVzLm51bV9ybzVfdmlvbGF0aW9ucyIsImZhY2V0aW5nX3R5cGUiOiJJTlRFUlZBTCIsInByb3BlcnR5X3R5cGUiOnsiaW50ZWdlciI6dHJ1ZSwieWVhciI6bnVsbCwiYWdncmVnYXRhYmxlIjp0cnVlfSwiaXNZZWFyIjpudWxsLCJzb3J0IjpudWxsLCJpbnRlcnZhbHMiOm51bGwsInJlcG9ydF9jYXJkX2VudGl0eSI6bnVsbCwiZmFjZXRpbmdfa2V5c19pbm9yZGVyIjpbIjAiLCIxIiwiMiIsIjMiLCI0Il0sImZhY2V0aW5nX2RhdGEiOnsiMCI6eyJtaW4iOjAsIm1heCI6MSwiaW5kZXgiOjAsImNvdW50IjoxMzQ4NjQ3LCJzZWxlY3RlZCI6dHJ1ZSwia2V5X2Zvcl9odW1hbnMiOiIwIiwia2V5IjoiMCIsImlkIjoiMDoxMzQ4NjQ3In0sIjEiOnsibWluIjoxLCJtYXgiOjIsImluZGV4IjoxLCJjb3VudCI6MzM5ODk3LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiMSIsImtleSI6IjEiLCJpZCI6IjE6MzM5ODk3In0sIjIiOnsibWluIjoyLCJtYXgiOjMsImluZGV4IjoyLCJjb3VudCI6MTc4MTQ0LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiMiIsImtleSI6IjIiLCJpZCI6IjI6MTc4MTQ0In0sIjMiOnsibWluIjozLCJtYXgiOjQsImluZGV4IjozLCJjb3VudCI6Mjc4NjksInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiIzIiwia2V5IjoiMyIsImlkIjoiMzoyNzg2OSJ9LCI0Ijp7Im1pbiI6NCwibWF4Ijo1LCJpbmRleCI6NCwiY291bnQiOjkwOCwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IjQiLCJrZXkiOiI0IiwiaWQiOiI0OjkwOCJ9fSwiaW50ZXJ2YWxzTGltaXRzIjpbMCwxLDIsMyw0LDVdfSwibW9sZWN1bGVfcHJvcGVydGllcy5mdWxsX213dCI6eyJlc19pbmRleCI6ImNoZW1ibF9tb2xlY3VsZSIsImVzX3Byb3BlcnR5X25hbWUiOiJtb2xlY3VsZV9wcm9wZXJ0aWVzLmZ1bGxfbXd0IiwiZmFjZXRpbmdfdHlwZSI6IklOVEVSVkFMIiwicHJvcGVydHlfdHlwZSI6eyJpbnRlZ2VyIjp0cnVlLCJ5ZWFyIjpudWxsLCJhZ2dyZWdhdGFibGUiOnRydWV9LCJpc1llYXIiOm51bGwsInNvcnQiOm51bGwsImludGVydmFscyI6bnVsbCwicmVwb3J0X2NhcmRfZW50aXR5IjpudWxsLCJmYWNldGluZ19rZXlzX2lub3JkZXIiOlsiWzQgIHRvICA5OV0iLCJbMTAwICB0byAgMTk5XSIsIlsyMDAgIHRvICAyOTldIiwiWzMwMCAgdG8gIDM5OV0iLCJbNDAwICB0byAgNDk5XSIsIls1MDAgIHRvICA1OTldIiwiWzYwMCAgdG8gIDY5OV0iLCJbNzAwICB0byAgNzk5XSIsIls4MDAgIHRvICA4OTldIiwiWzkwMCAgdG8gIDk5OV0iLCJbMSwwMDAgIHRvICAxMywwMjAuNDldIl0sImZhY2V0aW5nX2RhdGEiOnsiWzQgIHRvICA5OV0iOnsibWluIjo0LCJtYXgiOjEwMCwiaW5kZXgiOjAsImNvdW50Ijo4OTEsInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiJbNCAgdG8gIDk5XSIsImtleSI6Ils0ICB0byAgOTldIiwiaWQiOiJbNCAgdG8gIDk5XTo4OTEifSwiWzEwMCAgdG8gIDE5OV0iOnsibWluIjoxMDAsIm1heCI6MjAwLCJpbmRleCI6MSwiY291bnQiOjM0Njc2LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiWzEwMCAgdG8gIDE5OV0iLCJrZXkiOiJbMTAwICB0byAgMTk5XSIsImlkIjoiWzEwMCAgdG8gIDE5OV06MzQ2NzYifSwiWzIwMCAgdG8gIDI5OV0iOnsibWluIjoyMDAsIm1heCI6MzAwLCJpbmRleCI6MiwiY291bnQiOjI4ODM5NCwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IlsyMDAgIHRvICAyOTldIiwia2V5IjoiWzIwMCAgdG8gIDI5OV0iLCJpZCI6IlsyMDAgIHRvICAyOTldOjI4ODM5NCJ9LCJbMzAwICB0byAgMzk5XSI6eyJtaW4iOjMwMCwibWF4Ijo0MDAsImluZGV4IjozLCJjb3VudCI6NjgxNTAwLCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiWzMwMCAgdG8gIDM5OV0iLCJrZXkiOiJbMzAwICB0byAgMzk5XSIsImlkIjoiWzMwMCAgdG8gIDM5OV06NjgxNTAwIn0sIls0MDAgIHRvICA0OTldIjp7Im1pbiI6NDAwLCJtYXgiOjUwMCwiaW5kZXgiOjQsImNvdW50Ijo1NTQwNTYsInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiJbNDAwICB0byAgNDk5XSIsImtleSI6Ils0MDAgIHRvICA0OTldIiwiaWQiOiJbNDAwICB0byAgNDk5XTo1NTQwNTYifSwiWzUwMCAgdG8gIDU5OV0iOnsibWluIjo1MDAsIm1heCI6NjAwLCJpbmRleCI6NSwiY291bnQiOjIxNzg4Mywic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6Ils1MDAgIHRvICA1OTldIiwia2V5IjoiWzUwMCAgdG8gIDU5OV0iLCJpZCI6Ils1MDAgIHRvICA1OTldOjIxNzg4MyJ9LCJbNjAwICB0byAgNjk5XSI6eyJtaW4iOjYwMCwibWF4Ijo3MDAsImluZGV4Ijo2LCJjb3VudCI6NzI4NDksInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiJbNjAwICB0byAgNjk5XSIsImtleSI6Ils2MDAgIHRvICA2OTldIiwiaWQiOiJbNjAwICB0byAgNjk5XTo3Mjg0OSJ9LCJbNzAwICB0byAgNzk5XSI6eyJtaW4iOjcwMCwibWF4Ijo4MDAsImluZGV4Ijo3LCJjb3VudCI6MzA2MDksInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiJbNzAwICB0byAgNzk5XSIsImtleSI6Ils3MDAgIHRvICA3OTldIiwiaWQiOiJbNzAwICB0byAgNzk5XTozMDYwOSJ9LCJbODAwICB0byAgODk5XSI6eyJtaW4iOjgwMCwibWF4Ijo5MDAsImluZGV4Ijo4LCJjb3VudCI6MTcyMzIsInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiJbODAwICB0byAgODk5XSIsImtleSI6Ils4MDAgIHRvICA4OTldIiwiaWQiOiJbODAwICB0byAgODk5XToxNzIzMiJ9LCJbOTAwICB0byAgOTk5XSI6eyJtaW4iOjkwMCwibWF4IjoxMDAwLCJpbmRleCI6OSwiY291bnQiOjEwNTI4LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiWzkwMCAgdG8gIDk5OV0iLCJrZXkiOiJbOTAwICB0byAgOTk5XSIsImlkIjoiWzkwMCAgdG8gIDk5OV06MTA1MjgifSwiWzEsMDAwICB0byAgMTMsMDIwLjQ5XSI6eyJtaW4iOjEwMDAsIm1heCI6MTMwMjEuNDksImluZGV4IjoxMCwiY291bnQiOjM2MzAzLCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiWzEsMDAwICB0byAgMTMsMDIwLjQ5XSIsImtleSI6IlsxLDAwMCAgdG8gIDEzLDAyMC40OV0iLCJpZCI6IlsxLDAwMCAgdG8gIDEzLDAyMC40OV06MzYzMDMifX0sImludGVydmFsc0xpbWl0cyI6WzQsMTAwLDIwMCwzMDAsNDAwLDUwMCw2MDAsNzAwLDgwMCw5MDAsMTAwMCwxMzAyMS40OV19LCJtb2xlY3VsZV9wcm9wZXJ0aWVzLmFsb2dwIjp7ImVzX2luZGV4IjoiY2hlbWJsX21vbGVjdWxlIiwiZXNfcHJvcGVydHlfbmFtZSI6Im1vbGVjdWxlX3Byb3BlcnRpZXMuYWxvZ3AiLCJmYWNldGluZ190eXBlIjoiSU5URVJWQUwiLCJwcm9wZXJ0eV90eXBlIjp7ImludGVnZXIiOnRydWUsInllYXIiOm51bGwsImFnZ3JlZ2F0YWJsZSI6dHJ1ZX0sImlzWWVhciI6bnVsbCwic29ydCI6bnVsbCwiaW50ZXJ2YWxzIjpudWxsLCJyZXBvcnRfY2FyZF9lbnRpdHkiOm51bGwsImZhY2V0aW5nX2tleXNfaW5vcmRlciI6WyJbLTE0LjI2ICB0byAgLTFdIiwiMCIsIjEiLCIyIiwiMyIsIjQiLCI1IiwiNiIsIjciLCJbOCAgdG8gIDIyLjU3XSJdLCJmYWNldGluZ19kYXRhIjp7IjAiOnsibWluIjowLCJtYXgiOjEsImluZGV4IjoxLCJjb3VudCI6ODM0NDgsInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiIwIiwia2V5IjoiMCIsImlkIjoiMDo4MzQ0OCJ9LCIxIjp7Im1pbiI6MSwibWF4IjoyLCJpbmRleCI6MiwiY291bnQiOjIwNjM5Miwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IjEiLCJrZXkiOiIxIiwiaWQiOiIxOjIwNjM5MiJ9LCIyIjp7Im1pbiI6MiwibWF4IjozLCJpbmRleCI6MywiY291bnQiOjM3NjE1NSwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IjIiLCJrZXkiOiIyIiwiaWQiOiIyOjM3NjE1NSJ9LCIzIjp7Im1pbiI6MywibWF4Ijo0LCJpbmRleCI6NCwiY291bnQiOjQ1MzcwMCwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IjMiLCJrZXkiOiIzIiwiaWQiOiIzOjQ1MzcwMCJ9LCI0Ijp7Im1pbiI6NCwibWF4Ijo1LCJpbmRleCI6NSwiY291bnQiOjM1OTM2Miwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IjQiLCJrZXkiOiI0IiwiaWQiOiI0OjM1OTM2MiJ9LCI1Ijp7Im1pbiI6NSwibWF4Ijo2LCJpbmRleCI6NiwiY291bnQiOjIwMjQwOSwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IjUiLCJrZXkiOiI1IiwiaWQiOiI1OjIwMjQwOSJ9LCI2Ijp7Im1pbiI6NiwibWF4Ijo3LCJpbmRleCI6NywiY291bnQiOjg5ODA5LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiNiIsImtleSI6IjYiLCJpZCI6IjY6ODk4MDkifSwiNyI6eyJtaW4iOjcsIm1heCI6OCwiaW5kZXgiOjgsImNvdW50IjozNTk1MCwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IjciLCJrZXkiOiI3IiwiaWQiOiI3OjM1OTUwIn0sIlstMTQuMjYgIHRvICAtMV0iOnsibWluIjotMTQuMjYsIm1heCI6MCwiaW5kZXgiOjAsImNvdW50Ijo2MjM0MSwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IlstMTQuMjYgIHRvICAtMV0iLCJrZXkiOiJbLTE0LjI2ICB0byAgLTFdIiwiaWQiOiJbLTE0LjI2ICB0byAgLTFdOjYyMzQxIn0sIls4ICB0byAgMjIuNTddIjp7Im1pbiI6OCwibWF4IjoyMy41NywiaW5kZXgiOjksImNvdW50IjoyNTg5OSwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6Ils4ICB0byAgMjIuNTddIiwia2V5IjoiWzggIHRvICAyMi41N10iLCJpZCI6Ils4ICB0byAgMjIuNTddOjI1ODk5In19LCJpbnRlcnZhbHNMaW1pdHMiOlstMTQuMjYsMCwxLDIsMyw0LDUsNiw3LDgsMjMuNTddfSwiX21ldGFkYXRhLmF0Y19jbGFzc2lmaWNhdGlvbnMubGV2ZWwxX2Rlc2NyaXB0aW9uIjp7ImVzX2luZGV4IjoiY2hlbWJsX21vbGVjdWxlIiwiZXNfcHJvcGVydHlfbmFtZSI6Il9tZXRhZGF0YS5hdGNfY2xhc3NpZmljYXRpb25zLmxldmVsMV9kZXNjcmlwdGlvbiIsImZhY2V0aW5nX3R5cGUiOiJDQVRFR09SWSIsInByb3BlcnR5X3R5cGUiOnsiaW50ZWdlciI6ZmFsc2UsInllYXIiOm51bGwsImFnZ3JlZ2F0YWJsZSI6dHJ1ZX0sImlzWWVhciI6bnVsbCwic29ydCI6ImFzYyIsImludGVydmFscyI6MjAsInJlcG9ydF9jYXJkX2VudGl0eSI6bnVsbCwiZmFjZXRpbmdfa2V5c19pbm9yZGVyIjpbIi0gTi9BIC0iLCJBIC0gQUxJTUVOVEFSWSBUUkFDVCBBTkQgTUVUQUJPTElTTSIsIkIgLSBCTE9PRCBBTkQgQkxPT0QgRk9STUlORyBPUkdBTlMiLCJDIC0gQ0FSRElPVkFTQ1VMQVIgU1lTVEVNIiwiRCAtIERFUk1BVE9MT0dJQ0FMUyIsIkcgLSBHRU5JVE8gVVJJTkFSWSBTWVNURU0gQU5EIFNFWCBIT1JNT05FUyIsIkggLSBTWVNURU1JQyBIT1JNT05BTCBQUkVQQVJBVElPTlMsIEVYQ0wuIFNFWCBIT1JNT05FUyBBTkQgSU5TVUxJTlMiLCJKIC0gQU5USUlORkVDVElWRVMgRk9SIFNZU1RFTUlDIFVTRSIsIkwgLSBBTlRJTkVPUExBU1RJQyBBTkQgSU1NVU5PTU9EVUxBVElORyBBR0VOVFMiLCJNIC0gTVVTQ1VMTy1TS0VMRVRBTCBTWVNURU0iLCJOIC0gTkVSVk9VUyBTWVNURU0iLCJQIC0gQU5USVBBUkFTSVRJQyBQUk9EVUNUUywgSU5TRUNUSUNJREVTIEFORCBSRVBFTExFTlRTIiwiUiAtIFJFU1BJUkFUT1JZIFNZU1RFTSIsIlMgLSBTRU5TT1JZIE9SR0FOUyIsIlYgLSBWQVJJT1VTIl0sImZhY2V0aW5nX2RhdGEiOnsiLSBOL0EgLSI6eyJpbmRleCI6MCwiY291bnQiOjE5NTgxODAsInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiItIE4vQSAtIiwia2V5IjoiLSBOL0EgLSIsImlkIjoiLSBOL0EgLToxOTU4MTgwIn0sIk4gLSBORVJWT1VTIFNZU1RFTSI6eyJpbmRleCI6MSwiY291bnQiOjUxMiwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6Ik4gLSBORVJWT1VTIFNZU1RFTSIsImtleSI6Ik4gLSBORVJWT1VTIFNZU1RFTSIsImlkIjoiTiAtIE5FUlZPVVMgU1lTVEVNOjUxMiJ9LCJBIC0gQUxJTUVOVEFSWSBUUkFDVCBBTkQgTUVUQUJPTElTTSI6eyJpbmRleCI6MiwiY291bnQiOjQ1OCwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IkEgLSBBTElNRU5UQVJZIFRSQUNUIEFORCBNRVRBQk9MSVNNIiwia2V5IjoiQSAtIEFMSU1FTlRBUlkgVFJBQ1QgQU5EIE1FVEFCT0xJU00iLCJpZCI6IkEgLSBBTElNRU5UQVJZIFRSQUNUIEFORCBNRVRBQk9MSVNNOjQ1OCJ9LCJDIC0gQ0FSRElPVkFTQ1VMQVIgU1lTVEVNIjp7ImluZGV4IjozLCJjb3VudCI6NDEyLCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiQyAtIENBUkRJT1ZBU0NVTEFSIFNZU1RFTSIsImtleSI6IkMgLSBDQVJESU9WQVNDVUxBUiBTWVNURU0iLCJpZCI6IkMgLSBDQVJESU9WQVNDVUxBUiBTWVNURU06NDEyIn0sIkogLSBBTlRJSU5GRUNUSVZFUyBGT1IgU1lTVEVNSUMgVVNFIjp7ImluZGV4Ijo0LCJjb3VudCI6MzU2LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiSiAtIEFOVElJTkZFQ1RJVkVTIEZPUiBTWVNURU1JQyBVU0UiLCJrZXkiOiJKIC0gQU5USUlORkVDVElWRVMgRk9SIFNZU1RFTUlDIFVTRSIsImlkIjoiSiAtIEFOVElJTkZFQ1RJVkVTIEZPUiBTWVNURU1JQyBVU0U6MzU2In0sIkwgLSBBTlRJTkVPUExBU1RJQyBBTkQgSU1NVU5PTU9EVUxBVElORyBBR0VOVFMiOnsiaW5kZXgiOjUsImNvdW50IjozNDEsInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiJMIC0gQU5USU5FT1BMQVNUSUMgQU5EIElNTVVOT01PRFVMQVRJTkcgQUdFTlRTIiwia2V5IjoiTCAtIEFOVElORU9QTEFTVElDIEFORCBJTU1VTk9NT0RVTEFUSU5HIEFHRU5UUyIsImlkIjoiTCAtIEFOVElORU9QTEFTVElDIEFORCBJTU1VTk9NT0RVTEFUSU5HIEFHRU5UUzozNDEifSwiRCAtIERFUk1BVE9MT0dJQ0FMUyI6eyJpbmRleCI6NiwiY291bnQiOjI5Nywic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IkQgLSBERVJNQVRPTE9HSUNBTFMiLCJrZXkiOiJEIC0gREVSTUFUT0xPR0lDQUxTIiwiaWQiOiJEIC0gREVSTUFUT0xPR0lDQUxTOjI5NyJ9LCJSIC0gUkVTUElSQVRPUlkgU1lTVEVNIjp7ImluZGV4Ijo3LCJjb3VudCI6MjY4LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiUiAtIFJFU1BJUkFUT1JZIFNZU1RFTSIsImtleSI6IlIgLSBSRVNQSVJBVE9SWSBTWVNURU0iLCJpZCI6IlIgLSBSRVNQSVJBVE9SWSBTWVNURU06MjY4In0sIlYgLSBWQVJJT1VTIjp7ImluZGV4Ijo4LCJjb3VudCI6MjE5LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiViAtIFZBUklPVVMiLCJrZXkiOiJWIC0gVkFSSU9VUyIsImlkIjoiViAtIFZBUklPVVM6MjE5In0sIlMgLSBTRU5TT1JZIE9SR0FOUyI6eyJpbmRleCI6OSwiY291bnQiOjIxMiwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IlMgLSBTRU5TT1JZIE9SR0FOUyIsImtleSI6IlMgLSBTRU5TT1JZIE9SR0FOUyIsImlkIjoiUyAtIFNFTlNPUlkgT1JHQU5TOjIxMiJ9LCJHIC0gR0VOSVRPIFVSSU5BUlkgU1lTVEVNIEFORCBTRVggSE9STU9ORVMiOnsiaW5kZXgiOjEwLCJjb3VudCI6MTg4LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiRyAtIEdFTklUTyBVUklOQVJZIFNZU1RFTSBBTkQgU0VYIEhPUk1PTkVTIiwia2V5IjoiRyAtIEdFTklUTyBVUklOQVJZIFNZU1RFTSBBTkQgU0VYIEhPUk1PTkVTIiwiaWQiOiJHIC0gR0VOSVRPIFVSSU5BUlkgU1lTVEVNIEFORCBTRVggSE9STU9ORVM6MTg4In0sIkIgLSBCTE9PRCBBTkQgQkxPT0QgRk9STUlORyBPUkdBTlMiOnsiaW5kZXgiOjExLCJjb3VudCI6MTc5LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiQiAtIEJMT09EIEFORCBCTE9PRCBGT1JNSU5HIE9SR0FOUyIsImtleSI6IkIgLSBCTE9PRCBBTkQgQkxPT0QgRk9STUlORyBPUkdBTlMiLCJpZCI6IkIgLSBCTE9PRCBBTkQgQkxPT0QgRk9STUlORyBPUkdBTlM6MTc5In0sIk0gLSBNVVNDVUxPLVNLRUxFVEFMIFNZU1RFTSI6eyJpbmRleCI6MTIsImNvdW50IjoxNjYsInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiJNIC0gTVVTQ1VMTy1TS0VMRVRBTCBTWVNURU0iLCJrZXkiOiJNIC0gTVVTQ1VMTy1TS0VMRVRBTCBTWVNURU0iLCJpZCI6Ik0gLSBNVVNDVUxPLVNLRUxFVEFMIFNZU1RFTToxNjYifSwiUCAtIEFOVElQQVJBU0lUSUMgUFJPRFVDVFMsIElOU0VDVElDSURFUyBBTkQgUkVQRUxMRU5UUyI6eyJpbmRleCI6MTMsImNvdW50IjoxMDMsInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiJQIC0gQU5USVBBUkFTSVRJQyBQUk9EVUNUUywgSU5TRUNUSUNJREVTIEFORCBSRVBFTExFTlRTIiwia2V5IjoiUCAtIEFOVElQQVJBU0lUSUMgUFJPRFVDVFMsIElOU0VDVElDSURFUyBBTkQgUkVQRUxMRU5UUyIsImlkIjoiUCAtIEFOVElQQVJBU0lUSUMgUFJPRFVDVFMsIElOU0VDVElDSURFUyBBTkQgUkVQRUxMRU5UUzoxMDMifSwiSCAtIFNZU1RFTUlDIEhPUk1PTkFMIFBSRVBBUkFUSU9OUywgRVhDTC4gU0VYIEhPUk1PTkVTIEFORCBJTlNVTElOUyI6eyJpbmRleCI6MTQsImNvdW50Ijo4OSwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IkggLSBTWVNURU1JQyBIT1JNT05BTCBQUkVQQVJBVElPTlMsIEVYQ0wuIFNFWCBIT1JNT05FUyBBTkQgSU5TVUxJTlMiLCJrZXkiOiJIIC0gU1lTVEVNSUMgSE9STU9OQUwgUFJFUEFSQVRJT05TLCBFWENMLiBTRVggSE9STU9ORVMgQU5EIElOU1VMSU5TIiwiaWQiOiJIIC0gU1lTVEVNSUMgSE9STU9OQUwgUFJFUEFSQVRJT05TLCBFWENMLiBTRVggSE9STU9ORVMgQU5EIElOU1VMSU5TOjg5In19LCJpbnRlcnZhbHNMaW1pdHMiOm51bGx9LCJfbWV0YWRhdGEuYXRjX2NsYXNzaWZpY2F0aW9ucy5sZXZlbDJfZGVzY3JpcHRpb24iOnsiZXNfaW5kZXgiOiJjaGVtYmxfbW9sZWN1bGUiLCJlc19wcm9wZXJ0eV9uYW1lIjoiX21ldGFkYXRhLmF0Y19jbGFzc2lmaWNhdGlvbnMubGV2ZWwyX2Rlc2NyaXB0aW9uIiwiZmFjZXRpbmdfdHlwZSI6IkNBVEVHT1JZIiwicHJvcGVydHlfdHlwZSI6eyJpbnRlZ2VyIjpmYWxzZSwieWVhciI6bnVsbCwiYWdncmVnYXRhYmxlIjp0cnVlfSwiaXNZZWFyIjpudWxsLCJzb3J0IjoiYXNjIiwiaW50ZXJ2YWxzIjoyMCwicmVwb3J0X2NhcmRfZW50aXR5IjpudWxsLCJmYWNldGluZ19rZXlzX2lub3JkZXIiOlsiLSBOL0EgLSIsIkEwMyAtIERSVUdTIEZPUiBGVU5DVElPTkFMIEdBU1RST0lOVEVTVElOQUwgRElTT1JERVJTIiwiQTA3IC0gQU5USURJQVJSSEVBTFMsIElOVEVTVElOQUwgQU5USUlORkxBTU1BVE9SWS9BTlRJSU5GRUNUSVZFIEFHRU5UUyIsIkIwMSAtIEFOVElUSFJPTUJPVElDIEFHRU5UUyIsIkMwMSAtIENBUkRJQUMgVEhFUkFQWSIsIkcwMyAtIFNFWCBIT1JNT05FUyBBTkQgTU9EVUxBVE9SUyBPRiBUSEUgR0VOSVRBTCBTWVNURU0iLCJKMDEgLSBBTlRJQkFDVEVSSUFMUyBGT1IgU1lTVEVNSUMgVVNFIiwiSjA1IC0gQU5USVZJUkFMUyBGT1IgU1lTVEVNSUMgVVNFIiwiTDAxIC0gQU5USU5FT1BMQVNUSUMgQUdFTlRTIiwiTDA0IC0gSU1NVU5PU1VQUFJFU1NBTlRTIiwiTTAxIC0gQU5USUlORkxBTU1BVE9SWSBBTkQgQU5USVJIRVVNQVRJQyBQUk9EVUNUUyIsIk4wMiAtIEFOQUxHRVNJQ1MiLCJOMDUgLSBQU1lDSE9MRVBUSUNTIiwiTjA2IC0gUFNZQ0hPQU5BTEVQVElDUyIsIk90aGVyIENhdGVnb3JpZXMiLCJSMDEgLSBOQVNBTCBQUkVQQVJBVElPTlMiLCJSMDMgLSBEUlVHUyBGT1IgT0JTVFJVQ1RJVkUgQUlSV0FZIERJU0VBU0VTIiwiUjA1IC0gQ09VR0ggQU5EIENPTEQgUFJFUEFSQVRJT05TIiwiUjA2IC0gQU5USUhJU1RBTUlORVMgRk9SIFNZU1RFTUlDIFVTRSIsIlMwMSAtIE9QSFRIQUxNT0xPR0lDQUxTIiwiVjA5IC0gRElBR05PU1RJQyBSQURJT1BIQVJNQUNFVVRJQ0FMUyJdLCJmYWNldGluZ19kYXRhIjp7Ii0gTi9BIC0iOnsiaW5kZXgiOjAsImNvdW50IjoxOTU4MTgwLCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiLSBOL0EgLSIsImtleSI6Ii0gTi9BIC0iLCJpZCI6Ii0gTi9BIC06MTk1ODE4MCJ9LCJKMDEgLSBBTlRJQkFDVEVSSUFMUyBGT1IgU1lTVEVNSUMgVVNFIjp7ImluZGV4IjoxLCJjb3VudCI6MjIzLCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiSjAxIC0gQU5USUJBQ1RFUklBTFMgRk9SIFNZU1RFTUlDIFVTRSIsImtleSI6IkowMSAtIEFOVElCQUNURVJJQUxTIEZPUiBTWVNURU1JQyBVU0UiLCJpZCI6IkowMSAtIEFOVElCQUNURVJJQUxTIEZPUiBTWVNURU1JQyBVU0U6MjIzIn0sIkwwMSAtIEFOVElORU9QTEFTVElDIEFHRU5UUyI6eyJpbmRleCI6MiwiY291bnQiOjIxNSwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IkwwMSAtIEFOVElORU9QTEFTVElDIEFHRU5UUyIsImtleSI6IkwwMSAtIEFOVElORU9QTEFTVElDIEFHRU5UUyIsImlkIjoiTDAxIC0gQU5USU5FT1BMQVNUSUMgQUdFTlRTOjIxNSJ9LCJTMDEgLSBPUEhUSEFMTU9MT0dJQ0FMUyI6eyJpbmRleCI6MywiY291bnQiOjIwNSwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IlMwMSAtIE9QSFRIQUxNT0xPR0lDQUxTIiwia2V5IjoiUzAxIC0gT1BIVEhBTE1PTE9HSUNBTFMiLCJpZCI6IlMwMSAtIE9QSFRIQUxNT0xPR0lDQUxTOjIwNSJ9LCJOMDUgLSBQU1lDSE9MRVBUSUNTIjp7ImluZGV4Ijo0LCJjb3VudCI6MTY3LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiTjA1IC0gUFNZQ0hPTEVQVElDUyIsImtleSI6Ik4wNSAtIFBTWUNIT0xFUFRJQ1MiLCJpZCI6Ik4wNSAtIFBTWUNIT0xFUFRJQ1M6MTY3In0sIkMwMSAtIENBUkRJQUMgVEhFUkFQWSI6eyJpbmRleCI6NSwiY291bnQiOjEyMCwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IkMwMSAtIENBUkRJQUMgVEhFUkFQWSIsImtleSI6IkMwMSAtIENBUkRJQUMgVEhFUkFQWSIsImlkIjoiQzAxIC0gQ0FSRElBQyBUSEVSQVBZOjEyMCJ9LCJOMDYgLSBQU1lDSE9BTkFMRVBUSUNTIjp7ImluZGV4Ijo2LCJjb3VudCI6MTAzLCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiTjA2IC0gUFNZQ0hPQU5BTEVQVElDUyIsImtleSI6Ik4wNiAtIFBTWUNIT0FOQUxFUFRJQ1MiLCJpZCI6Ik4wNiAtIFBTWUNIT0FOQUxFUFRJQ1M6MTAzIn0sIk4wMiAtIEFOQUxHRVNJQ1MiOnsiaW5kZXgiOjcsImNvdW50Ijo3OSwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6Ik4wMiAtIEFOQUxHRVNJQ1MiLCJrZXkiOiJOMDIgLSBBTkFMR0VTSUNTIiwiaWQiOiJOMDIgLSBBTkFMR0VTSUNTOjc5In0sIk0wMSAtIEFOVElJTkZMQU1NQVRPUlkgQU5EIEFOVElSSEVVTUFUSUMgUFJPRFVDVFMiOnsiaW5kZXgiOjgsImNvdW50Ijo3OCwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6Ik0wMSAtIEFOVElJTkZMQU1NQVRPUlkgQU5EIEFOVElSSEVVTUFUSUMgUFJPRFVDVFMiLCJrZXkiOiJNMDEgLSBBTlRJSU5GTEFNTUFUT1JZIEFORCBBTlRJUkhFVU1BVElDIFBST0RVQ1RTIiwiaWQiOiJNMDEgLSBBTlRJSU5GTEFNTUFUT1JZIEFORCBBTlRJUkhFVU1BVElDIFBST0RVQ1RTOjc4In0sIkIwMSAtIEFOVElUSFJPTUJPVElDIEFHRU5UUyI6eyJpbmRleCI6OSwiY291bnQiOjcyLCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiQjAxIC0gQU5USVRIUk9NQk9USUMgQUdFTlRTIiwia2V5IjoiQjAxIC0gQU5USVRIUk9NQk9USUMgQUdFTlRTIiwiaWQiOiJCMDEgLSBBTlRJVEhST01CT1RJQyBBR0VOVFM6NzIifSwiUjAzIC0gRFJVR1MgRk9SIE9CU1RSVUNUSVZFIEFJUldBWSBESVNFQVNFUyI6eyJpbmRleCI6MTAsImNvdW50Ijo3Miwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IlIwMyAtIERSVUdTIEZPUiBPQlNUUlVDVElWRSBBSVJXQVkgRElTRUFTRVMiLCJrZXkiOiJSMDMgLSBEUlVHUyBGT1IgT0JTVFJVQ1RJVkUgQUlSV0FZIERJU0VBU0VTIiwiaWQiOiJSMDMgLSBEUlVHUyBGT1IgT0JTVFJVQ1RJVkUgQUlSV0FZIERJU0VBU0VTOjcyIn0sIlYwOSAtIERJQUdOT1NUSUMgUkFESU9QSEFSTUFDRVVUSUNBTFMiOnsiaW5kZXgiOjExLCJjb3VudCI6NzIsInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiJWMDkgLSBESUFHTk9TVElDIFJBRElPUEhBUk1BQ0VVVElDQUxTIiwia2V5IjoiVjA5IC0gRElBR05PU1RJQyBSQURJT1BIQVJNQUNFVVRJQ0FMUyIsImlkIjoiVjA5IC0gRElBR05PU1RJQyBSQURJT1BIQVJNQUNFVVRJQ0FMUzo3MiJ9LCJHMDMgLSBTRVggSE9STU9ORVMgQU5EIE1PRFVMQVRPUlMgT0YgVEhFIEdFTklUQUwgU1lTVEVNIjp7ImluZGV4IjoxMiwiY291bnQiOjcxLCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiRzAzIC0gU0VYIEhPUk1PTkVTIEFORCBNT0RVTEFUT1JTIE9GIFRIRSBHRU5JVEFMIFNZU1RFTSIsImtleSI6IkcwMyAtIFNFWCBIT1JNT05FUyBBTkQgTU9EVUxBVE9SUyBPRiBUSEUgR0VOSVRBTCBTWVNURU0iLCJpZCI6IkcwMyAtIFNFWCBIT1JNT05FUyBBTkQgTU9EVUxBVE9SUyBPRiBUSEUgR0VOSVRBTCBTWVNURU06NzEifSwiQTAzIC0gRFJVR1MgRk9SIEZVTkNUSU9OQUwgR0FTVFJPSU5URVNUSU5BTCBESVNPUkRFUlMiOnsiaW5kZXgiOjEzLCJjb3VudCI6NjgsInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiJBMDMgLSBEUlVHUyBGT1IgRlVOQ1RJT05BTCBHQVNUUk9JTlRFU1RJTkFMIERJU09SREVSUyIsImtleSI6IkEwMyAtIERSVUdTIEZPUiBGVU5DVElPTkFMIEdBU1RST0lOVEVTVElOQUwgRElTT1JERVJTIiwiaWQiOiJBMDMgLSBEUlVHUyBGT1IgRlVOQ1RJT05BTCBHQVNUUk9JTlRFU1RJTkFMIERJU09SREVSUzo2OCJ9LCJKMDUgLSBBTlRJVklSQUxTIEZPUiBTWVNURU1JQyBVU0UiOnsiaW5kZXgiOjE0LCJjb3VudCI6NjgsInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiJKMDUgLSBBTlRJVklSQUxTIEZPUiBTWVNURU1JQyBVU0UiLCJrZXkiOiJKMDUgLSBBTlRJVklSQUxTIEZPUiBTWVNURU1JQyBVU0UiLCJpZCI6IkowNSAtIEFOVElWSVJBTFMgRk9SIFNZU1RFTUlDIFVTRTo2OCJ9LCJSMDYgLSBBTlRJSElTVEFNSU5FUyBGT1IgU1lTVEVNSUMgVVNFIjp7ImluZGV4IjoxNSwiY291bnQiOjY0LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiUjA2IC0gQU5USUhJU1RBTUlORVMgRk9SIFNZU1RFTUlDIFVTRSIsImtleSI6IlIwNiAtIEFOVElISVNUQU1JTkVTIEZPUiBTWVNURU1JQyBVU0UiLCJpZCI6IlIwNiAtIEFOVElISVNUQU1JTkVTIEZPUiBTWVNURU1JQyBVU0U6NjQifSwiQTA3IC0gQU5USURJQVJSSEVBTFMsIElOVEVTVElOQUwgQU5USUlORkxBTU1BVE9SWS9BTlRJSU5GRUNUSVZFIEFHRU5UUyI6eyJpbmRleCI6MTYsImNvdW50Ijo2MCwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IkEwNyAtIEFOVElESUFSUkhFQUxTLCBJTlRFU1RJTkFMIEFOVElJTkZMQU1NQVRPUlkvQU5USUlORkVDVElWRSBBR0VOVFMiLCJrZXkiOiJBMDcgLSBBTlRJRElBUlJIRUFMUywgSU5URVNUSU5BTCBBTlRJSU5GTEFNTUFUT1JZL0FOVElJTkZFQ1RJVkUgQUdFTlRTIiwiaWQiOiJBMDcgLSBBTlRJRElBUlJIRUFMUywgSU5URVNUSU5BTCBBTlRJSU5GTEFNTUFUT1JZL0FOVElJTkZFQ1RJVkUgQUdFTlRTOjYwIn0sIkwwNCAtIElNTVVOT1NVUFBSRVNTQU5UUyI6eyJpbmRleCI6MTcsImNvdW50Ijo1OSwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IkwwNCAtIElNTVVOT1NVUFBSRVNTQU5UUyIsImtleSI6IkwwNCAtIElNTVVOT1NVUFBSRVNTQU5UUyIsImlkIjoiTDA0IC0gSU1NVU5PU1VQUFJFU1NBTlRTOjU5In0sIlIwNSAtIENPVUdIIEFORCBDT0xEIFBSRVBBUkFUSU9OUyI6eyJpbmRleCI6MTgsImNvdW50Ijo1OSwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IlIwNSAtIENPVUdIIEFORCBDT0xEIFBSRVBBUkFUSU9OUyIsImtleSI6IlIwNSAtIENPVUdIIEFORCBDT0xEIFBSRVBBUkFUSU9OUyIsImlkIjoiUjA1IC0gQ09VR0ggQU5EIENPTEQgUFJFUEFSQVRJT05TOjU5In0sIlIwMSAtIE5BU0FMIFBSRVBBUkFUSU9OUyI6eyJpbmRleCI6MTksImNvdW50Ijo1Niwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IlIwMSAtIE5BU0FMIFBSRVBBUkFUSU9OUyIsImtleSI6IlIwMSAtIE5BU0FMIFBSRVBBUkFUSU9OUyIsImlkIjoiUjAxIC0gTkFTQUwgUFJFUEFSQVRJT05TOjU2In0sIk90aGVyIENhdGVnb3JpZXMiOnsiaW5kZXgiOjIwLCJjb3VudCI6MjA1Niwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6Ik90aGVyIENhdGVnb3JpZXMiLCJrZXkiOiJPdGhlciBDYXRlZ29yaWVzIiwiaWQiOiJPdGhlciBDYXRlZ29yaWVzOjIwNTYifX0sImludGVydmFsc0xpbWl0cyI6bnVsbH0sIl9tZXRhZGF0YS5yZWxhdGVkX3RhcmdldHMuY291bnQiOnsiZXNfaW5kZXgiOiJjaGVtYmxfbW9sZWN1bGUiLCJlc19wcm9wZXJ0eV9uYW1lIjoiX21ldGFkYXRhLnJlbGF0ZWRfdGFyZ2V0cy5jb3VudCIsImZhY2V0aW5nX3R5cGUiOiJJTlRFUlZBTCIsInByb3BlcnR5X3R5cGUiOnsiaW50ZWdlciI6dHJ1ZSwieWVhciI6bnVsbCwiYWdncmVnYXRhYmxlIjp0cnVlfSwiaXNZZWFyIjpudWxsLCJzb3J0IjpudWxsLCJpbnRlcnZhbHMiOm51bGwsInJlcG9ydF9jYXJkX2VudGl0eSI6bnVsbCwiZmFjZXRpbmdfa2V5c19pbm9yZGVyIjpbIjEiLCIyIiwiWzMgIHRvICA0XSIsIjUiLCJbNiAgdG8gIDEwXSIsIlsxMSAgdG8gIDEsMjkyXSJdLCJmYWNldGluZ19kYXRhIjp7IjEiOnsibWluIjoxLCJtYXgiOjIsImluZGV4IjowLCJjb3VudCI6NTU3NzUzLCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiMSIsImtleSI6IjEiLCJpZCI6IjE6NTU3NzUzIn0sIjIiOnsibWluIjoyLCJtYXgiOjMsImluZGV4IjoxLCJjb3VudCI6MzY4Mjg3LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiMiIsImtleSI6IjIiLCJpZCI6IjI6MzY4Mjg3In0sIjUiOnsibWluIjo1LCJtYXgiOjYsImluZGV4IjozLCJjb3VudCI6MTEwOTQ2LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiNSIsImtleSI6IjUiLCJpZCI6IjU6MTEwOTQ2In0sIlszICB0byAgNF0iOnsibWluIjozLCJtYXgiOjUsImluZGV4IjoyLCJjb3VudCI6MzY2MDcwLCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiWzMgIHRvICA0XSIsImtleSI6IlszICB0byAgNF0iLCJpZCI6IlszICB0byAgNF06MzY2MDcwIn0sIls2ICB0byAgMTBdIjp7Im1pbiI6NiwibWF4IjoxMSwiaW5kZXgiOjQsImNvdW50IjoyNTg5MjEsInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiJbNiAgdG8gIDEwXSIsImtleSI6Ils2ICB0byAgMTBdIiwiaWQiOiJbNiAgdG8gIDEwXToyNTg5MjEifSwiWzExICB0byAgMSwyOTJdIjp7Im1pbiI6MTEsIm1heCI6MTI5MywiaW5kZXgiOjUsImNvdW50IjoyMDMxNzIsInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiJbMTEgIHRvICAxLDI5Ml0iLCJrZXkiOiJbMTEgIHRvICAxLDI5Ml0iLCJpZCI6IlsxMSAgdG8gIDEsMjkyXToyMDMxNzIifX0sImludGVydmFsc0xpbWl0cyI6WzEsMiwzLDUsNiwxMSwxMjkzXX0sIl9tZXRhZGF0YS5yZWxhdGVkX2FjdGl2aXRpZXMuY291bnQiOnsiZXNfaW5kZXgiOiJjaGVtYmxfbW9sZWN1bGUiLCJlc19wcm9wZXJ0eV9uYW1lIjoiX21ldGFkYXRhLnJlbGF0ZWRfYWN0aXZpdGllcy5jb3VudCIsImZhY2V0aW5nX3R5cGUiOiJJTlRFUlZBTCIsInByb3BlcnR5X3R5cGUiOnsiaW50ZWdlciI6dHJ1ZSwieWVhciI6bnVsbCwiYWdncmVnYXRhYmxlIjp0cnVlfSwiaXNZZWFyIjpudWxsLCJzb3J0IjpudWxsLCJpbnRlcnZhbHMiOm51bGwsInJlcG9ydF9jYXJkX2VudGl0eSI6bnVsbCwiZmFjZXRpbmdfa2V5c19pbm9yZGVyIjpbIjEiLCIyIiwiMyIsIjQiLCI1IiwiWzYgIHRvICA4XSIsIls5ICB0byAgMTZdIiwiWzE3ICB0byAgMTYsNDk1XSJdLCJmYWNldGluZ19kYXRhIjp7IjEiOnsibWluIjoxLCJtYXgiOjIsImluZGV4IjowLCJjb3VudCI6MzcxNTMwLCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiMSIsImtleSI6IjEiLCJpZCI6IjE6MzcxNTMwIn0sIjIiOnsibWluIjoyLCJtYXgiOjMsImluZGV4IjoxLCJjb3VudCI6MzM5MzQ5LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiMiIsImtleSI6IjIiLCJpZCI6IjI6MzM5MzQ5In0sIjMiOnsibWluIjozLCJtYXgiOjQsImluZGV4IjoyLCJjb3VudCI6MjA0MzYwLCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiMyIsImtleSI6IjMiLCJpZCI6IjM6MjA0MzYwIn0sIjQiOnsibWluIjo0LCJtYXgiOjUsImluZGV4IjozLCJjb3VudCI6MTU5MTU0LCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiNCIsImtleSI6IjQiLCJpZCI6IjQ6MTU5MTU0In0sIjUiOnsibWluIjo1LCJtYXgiOjYsImluZGV4Ijo0LCJjb3VudCI6MTI1MDYxLCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiNSIsImtleSI6IjUiLCJpZCI6IjU6MTI1MDYxIn0sIls2ICB0byAgOF0iOnsibWluIjo2LCJtYXgiOjksImluZGV4Ijo1LCJjb3VudCI6MjQyNjMxLCJzZWxlY3RlZCI6ZmFsc2UsImtleV9mb3JfaHVtYW5zIjoiWzYgIHRvICA4XSIsImtleSI6Ils2ICB0byAgOF0iLCJpZCI6Ils2ICB0byAgOF06MjQyNjMxIn0sIls5ICB0byAgMTZdIjp7Im1pbiI6OSwibWF4IjoxNywiaW5kZXgiOjYsImNvdW50IjoyMzY0OTQsInNlbGVjdGVkIjpmYWxzZSwia2V5X2Zvcl9odW1hbnMiOiJbOSAgdG8gIDE2XSIsImtleSI6Ils5ICB0byAgMTZdIiwiaWQiOiJbOSAgdG8gIDE2XToyMzY0OTQifSwiWzE3ICB0byAgMTYsNDk1XSI6eyJtaW4iOjE3LCJtYXgiOjE2NDk2LCJpbmRleCI6NywiY291bnQiOjE4NjU3MCwic2VsZWN0ZWQiOmZhbHNlLCJrZXlfZm9yX2h1bWFucyI6IlsxNyAgdG8gIDE2LDQ5NV0iLCJrZXkiOiJbMTcgIHRvICAxNiw0OTVdIiwiaWQiOiJbMTcgIHRvICAxNiw0OTVdOjE4NjU3MCJ9fSwiaW50ZXJ2YWxzTGltaXRzIjpbMSwyLDMsNCw1LDYsOSwxNywxNjQ5Nl19fX19
a = pd.read_csv()[["Smiles","QED Weighted"]]
#CSV olarak ChEMBL Covid-19 veri seti alınır / https://www.ebi.ac.uk/chembl/g/#browse/compounds/filter/_metadata.compound_records.src_id%3A52
b = pd.read_csv()[["Smiles","QED Weighted"]]
chembl = a.copy()
chembl.drop_duplicates(inplace = True)
b.drop_duplicates(inplace = True)

smiles_chembl = chembl["Smiles"]
smiles_moses = moses.copy()
smiles_chembl.drop_duplicates(inplace = True)
smiles_moses.drop_duplicates(inplace = True)
smiles_chembl = smiles_chembl.to_numpy()
smiles_moses = smiles_moses.to_numpy()
corona_smiles = b["Smiles"].to_numpy()

#Chembl
qed_values_chembl = np.empty(shape = (len(smiles_chembl,)))
for i in range(len(smiles_chembl)):
  qed_values_chembl[i] = qed(Chem.MolFromSmiles(smiles_chembl[i]))

#Moses
qed_values_moses = np.empty(shape = (len(smiles_moses,)))
for i in range(len(smiles_moses)):
  qed_values_moses[i] = qed(Chem.MolFromSmiles(smiles_moses[i]))

smiles_chembl_copy = smiles_chembl.copy()
faulty_index = []
for i in range(len(smiles_chembl)):
  if qed_values_chembl[i] < 0.5:
    faulty_index.append(i)
smiles_chembl_copy = np.delete(smiles_chembl_copy,faulty_index)

smiles_moses_copy = smiles_moses.copy()
faulty_index = []
for i in range(len(smiles_moses)):
  if qed_values_moses[i] < 0.9:
    faulty_index.append(i)
smiles_moses_copy = np.delete(smiles_moses_copy,faulty_index)

smiles = np.append(smiles_chembl_copy,smiles_moses_copy)

smiles_df = pd.DataFrame(smiles)
smiles_df.drop_duplicates(inplace = True)
smiles = smiles_df.to_numpy()

smiles = smiles.reshape((len(smiles),))

corona_selfies = []
for i in range(len(corona_smiles)):
  try:
    temp = encoder(corona_smiles[i])
    corona_selfies.append(atomwise_tokenizer(temp))
  except:
    print(i)

selfies = []
for i in range(len(smiles)):
  try:
    temp = encoder(smiles[i])
    selfies.append(atomwise_tokenizer(temp))
  except:
    print(i)

corona_max = 0
for i in corona_selfies:
  if len(i) > corona_max:
    corona_max = len(i)

max = 0
for i in selfies:
  if len(i) > max:
    max = len(i)

corona_lengths = []
for i in corona_selfies:
  corona_lengths.append(len(i))
corona_lengths = pd.DataFrame(corona_lengths)

corona_distribution = corona_lengths[0].plot.hist(bins = 12,alpha = 0.5)

corona_lengths = {}
for i in corona_selfies:
  if len(i) not in corona_lengths:
    corona_lengths[len(i)] = 1
  else:
    corona_lengths[len(i)] += 1
  if len(i) == 1:
    print(corona_selfies.index(i))

lengths = []
for i in selfies:
  lengths.append(len(i))
lengths = pd.DataFrame(lengths)

distribution = lengths[0].plot.hist(bins = 12,alpha = 0.5)

lengths = {}
for i in selfies:
  if len(i) not in lengths:
    lengths[len(i)] = 1
  else:
    lengths[len(i)] += 1
  if len(i) == 1:
    print(selfies.index(i))

chosen_corona_max = 128
corona_selfies_copy_1 = corona_selfies.copy()
corona_selfies_copy_2 = corona_selfies.copy()

for i in corona_selfies_copy_1:
  if len(i) > chosen_corona_max:
    corona_selfies_copy_2.remove(i)

corona_selfies_copy = corona_selfies_copy_2

num = 0
for i in corona_selfies_copy:
  if len(i) > 182:
    num += 1
print(num)

chosen_max = 128
selfies_copy = selfies.copy()
selfies_copy_1 = selfies.copy()

indexes = []
for i in range(len(selfies_copy_1)):
  if len(selfies_copy_1[i]) > chosen_max:
    indexes.append(i)
    selfies_copy.remove(selfies_copy_1[i])

down_limit = 10
for i in corona_selfies_copy:
  if len(i) < down_limit:
    corona_selfies_copy.remove(i)

num = 0
for i in corona_selfies_copy:
  if len(i) < down_limit:
    num+=1
print(num)

down_limit = 10
for i in selfies_copy:
  if len(i) < down_limit:
    selfies_copy.remove(i)

num = 0
for i in selfies_copy:
  if len(i) < down_limit:
    num+=1
print(num)

labels = ['[C]',
 '[#C]',
 '[=C]',
 '[c]',
 '[=c]',
 '[-c]',
 '[N]',
 '[#N]',
 '[=N]',
 '[-n]',
 '[n]',
 '[N+expl]',
 '[=N+expl]',
 '[=N-expl]',
 '[NHexpl]',
 '[=NH2+expl]',
 '[O]',
 '[=O]',
 '[o]',
 '[Oexpl]',
 '[O-expl]',
 '[F]',
 '[P]',
 '[S]',
 '[=S]',
 '[s]',
 '[Cl]',
 '[Cl-expl]',
 '[Br]',
 '[Br-expl]',
 '[I]',
 '[I-expl]',
 '[nHexpl]',
 '[Hexpl]',
 '[epsilon]',
 '[Branch1_1]',
 '[Branch1_2]',
 '[Branch1_3]',
 '[Branch2_1]',
 '[Branch2_2]',
 '[Branch2_3]',
 '[Branch3_3]',
 '[Branch3_1]',
 '[Branch3_2]',
 '[Ring1]',
 '[Expl-Ring1]',
 '[Expl=Ring1]',
 '[Ring2]',
 '[Expl-Ring2]',
 '[Expl=Ring2]',
 '[Ring3]',
 '.',
 '[C@@Hexpl]',
 '[C@Hexpl]',
 '[C@expl]',
 '[C@@expl]',
 '[/C]',
 '[\\C]',
 '[/S]',
 '[Expl\\Ring1]',
 '[/N]',
 '[\\N]',
 '[/C@Hexpl]',
 '[H+expl]',
 '[S-expl]',
 '[Zn+2expl]',
 '[Siexpl]',
 '[Na+expl]',
 '[\\S]',
 '[/O]',
 '[P@expl]',
 '[Expl/Ring2]',
 '[N-expl]',
 '[B]',
 '[\\C@@Hexpl]',
 '[/C@@Hexpl]',
 '[=S+expl]',
 '[Cexpl]',
 '[=Cexpl]',
 '[/Br]',
 '[/Cexpl]',
 '[/Cl]',
 '[Znexpl]',
 '[P@@expl]']

new_corona_labels = []
for i in corona_selfies_copy:
  for j in i:
    if(j not in labels) and (j not in new_corona_labels):
      new_corona_labels.append(j)

corona_label_num = 0
for i in corona_selfies_copy:
  for j in i:
    try:
      a = new_corona_labels.index(j)
      corona_label_num += 1
      break
    except:
      pass

corona_label_dict = dict(zip(new_corona_labels,[0 for i in range(37)]))
for i in corona_selfies_copy:
  for j in i:
    try:
      corona_label_dict[j] += 1
    except:
      pass

new_labels = []
for i in concated_selfies:
  for j in i:
    if (j not in labels) and (j not in new_labels):
      new_labels.append(j)

declined_labels = new_corona_labels + new_labels

accepted_labels = labels

label_dict = dict(zip(accepted_labels,range(1,len(accepted_labels)+1)))

for a in range(3):
  for i in concated_selfies:
    for j in i:
      try:
        ind = declined_labels.index(j)
        concated_selfies.remove(i)
        break
      except:
        pass

final_selfies = np.zeros(shape = (len(concated_selfies),chosen_max),dtype = object)
for i in range(len(concated_selfies)):
  for j in range(len(concated_selfies[i])):
    final_selfies[i][j] = concated_selfies[i][j]

numbered_selfies = np.zeros(shape = (len(final_selfies),chosen_max),dtype = "float32")
for i in range(len(final_selfies)):
  for j in range(len(final_selfies[i])):
    if final_selfies[i][j] != 0:
      numbered_selfies[i][j] = label_dict[final_selfies[i][j]]
    else:
      break

#MAE Veri Setini Kaydetme
np.save("",numbered_selfies)

#DeepADTP Veri Seti

#Ayrıştırılmış KIBA Veri Seti çekilir
test = pd.read_csv("https://raw.githubusercontent.com/zhaoqichang/AttentionDTA_BIBM/master/tfrecord/kiba_str_all.txt",header = None,sep = " ")

kiba_mols = test[2]
kiba_proteins = test[3]
kiba_bindaff = test[4]

kiba_mols = kiba_mols.to_numpy()
kiba_proteins = kiba_proteins.to_numpy()
kiba_bindaff = kiba_bindaff.to_numpy()

labels = ['[C]',
 '[#C]',
 '[=C]',
 '[c]',
 '[=c]',
 '[-c]',
 '[N]',
 '[#N]',
 '[=N]',
 '[-n]',
 '[n]',
 '[N+expl]',
 '[=N+expl]',
 '[=N-expl]',
 '[NHexpl]',
 '[=NH2+expl]',
 '[O]',
 '[=O]',
 '[o]',
 '[Oexpl]',
 '[O-expl]',
 '[F]',
 '[P]',
 '[S]',
 '[=S]',
 '[s]',
 '[Cl]',
 '[Cl-expl]',
 '[Br]',
 '[Br-expl]',
 '[I]',
 '[I-expl]',
 '[nHexpl]',
 '[Hexpl]',
 '[epsilon]',
 '[Branch1_1]',
 '[Branch1_2]',
 '[Branch1_3]',
 '[Branch2_1]',
 '[Branch2_2]',
 '[Branch2_3]',
 '[Branch3_3]',
 '[Branch3_1]',
 '[Branch3_2]',
 '[Ring1]',
 '[Expl-Ring1]',
 '[Expl=Ring1]',
 '[Ring2]',
 '[Expl-Ring2]',
 '[Expl=Ring2]',
 '[Ring3]',
 '.',
 '[C@@Hexpl]',
 '[C@Hexpl]',
 '[C@expl]',
 '[C@@expl]',
 '[/C]',
 '[\\C]',
 '[/S]',
 '[Expl\\Ring1]',
 '[/N]',
 '[\\N]',
 '[/C@Hexpl]',
 '[H+expl]',
 '[S-expl]',
 '[Zn+2expl]',
 '[Siexpl]',
 '[Na+expl]',
 '[\\S]',
 '[/O]',
 '[P@expl]',
 '[Expl/Ring2]',
 '[N-expl]',
 '[B]',
 '[\\C@@Hexpl]',
 '[/C@@Hexpl]',
 '[=S+expl]',
 '[Cexpl]',
 '[=Cexpl]',
 '[/Br]',
 '[/Cexpl]',
 '[/Cl]',
 '[Znexpl]',
 '[P@@expl]']

label_dict = dict(zip(labels,range(1,len(labels)+1)))

kiba_mols_selfies = []

for i in kiba_mols:
  temp = encoder(i)
  kiba_mols_selfies.append(atomwise_tokenizer(temp))

test_kiba_mols_selfies = kiba_mols_selfies

kiba_mols_tokenized = []
kiba_temp_proteins = []
kiba_temp_bindaff = []
for i in range(len(kiba_mols_selfies)):
  if len(kiba_mols_selfies[i]) <= 128:
    temp = []
    for j in range(128):
      try:
        temp.append(label_dict[kiba_mols_selfies[i][j]])
      except:
        temp.append(0)
    kiba_mols_tokenized.append(temp)
    kiba_temp_proteins.append(kiba_proteins[i])
    kiba_temp_bindaff.append(kiba_bindaff[i])

error_indexes = []
for i in range(len(kiba_mols_tokenized)):
  zero_found = False
  for j in range(len(kiba_mols_tokenized[i])):
    if (kiba_mols_tokenized[i][j] == 0) and (zero_found == False):
      zero_found = True
    elif (kiba_mols_tokenized[i][j] != 0) and (zero_found == True):
      error_indexes.append([i,j])
      break

protein_dict = {'A': 7,
 'C': 11,
 'D': 17,
 'E': 10,
 'F': 3,
 'G': 2,
 'H': 19,
 'I': 20,
 'K': 5,
 'L': 14,
 'M': 6,
 'N': 15,
 'P': 8,
 'Q': 12,
 'R': 4,
 'S': 1,
 'T': 13,
 'V': 9,
 'W': 16,
 'Y': 18}

remove_indexes = []
kiba_proteins_tokenized = []
for i in range(len(kiba_temp_proteins)):
  if len(kiba_temp_proteins[i]) <= 1500:
    temp = []
    for j in kiba_temp_proteins[i]:
      temp.append(protein_dict[j])
    kiba_proteins_tokenized.append(temp)
  else:
    remove_indexes.append(i)

kiba_proteins_tokenized_copy = kiba_proteins_tokenized.copy()
kiba_proteins_tokenized = np.zeros(shape = (len(kiba_proteins_tokenized),1500))
for i in range(len(kiba_proteins_tokenized_copy)):
  for j in range(len(kiba_proteins_tokenized_copy[i])):
    kiba_proteins_tokenized[i][j] = kiba_proteins_tokenized_copy[i][j]

for i in remove_indexes[::-1]:
  kiba_mols_tokenized.pop(i)
  kiba_temp_bindaff.pop(i)

kiba_mols_tokenized_copy = kiba_mols_tokenized.copy()
kiba_mols_tokenized = np.zeros(shape = (len(kiba_mols_tokenized),128))
for i in range(len(kiba_mols_tokenized_copy)):
  for j in range(len(kiba_mols_tokenized_copy[i])):
    kiba_mols_tokenized[i][j] = kiba_mols_tokenized_copy[i][j]

kiba_temp_bindaff = np.asarray(kiba_temp_bindaff)

#Molekül, Protein ve Binding Affinity Verileri kaydedilir
np.save("",kiba_mols_tokenized)
np.save("",kiba_proteins_tokenized)
np.save("",kiba_temp_bindaff)
