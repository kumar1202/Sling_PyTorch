from __future__ import print_function
import os
import numpy as np
import random
import string
import tensorflow as tf
import zipfile
from six.moves import range
from six.moves.urllib.request import urlretrieve

batch_size=64
num_unrollings=14

class BatchGenerator(object):
  def __init__(self, text, batch_size, num_unrollings):
    self._text = text
    self._text_size = len(text)
    self._batch_size = batch_size
    self._num_unrollings = num_unrollings
    segment = self._text_size // batch_size
    self._cursor = [ offset * segment for offset in range(batch_size)]
    self._last_batch = self._next_batch()
  
  def _next_batch(self):
    """Generate a single batch from the current cursor position in the data."""
    batch = np.zeros(shape=(self._batch_size, vocabulary_size), dtype=np.float)
    for b in range(self._batch_size):
      batch[b, char2id(self._text[self._cursor[b]])] = 1.0
      self._cursor[b] = (self._cursor[b] + 1) % self._text_size
    return batch
  
  def next(self):
    """Generate the next array of batches from the data. The array consists of
    the last batch of the previous array, followed by num_unrollings new ones.
    """
    batches = [self._last_batch]
    batches=[]
    for step in range(self._num_unrollings-1):
      batches.append(self._next_batch())
    #The EOS character for each batch
    
    #Generating the output batches by reversing each word in a num_unrolling size sentence
    output_batches=[]
    for step in range(self._num_unrollings-1):
        output_batches.append(np.zeros(shape=(self._batch_size, vocabulary_size),dtype=np.float))
    for b in range(self._batch_size):
        words=[]
        #Will store each of characters for words, is emptied when a space is encountered
        array=[]
        for i in range(self._num_unrollings-1):
            if(np.argmax(batches[i][b,:])!=1):
                array.append(np.argmax(batches[i][b,:]))
            else:
                array=reverse(array)
                words.extend(array)
                words.append(1)
                array=[]
        array=reverse(array)
        words.extend(array)
        for i in range(self._num_unrollings-1):
            output_batches[i][b,words[i]]=1
        
    last_batch=np.zeros(shape=(self._batch_size, vocabulary_size), dtype=np.float)
    #Set the last batch character to EOS for the last batch
    
    last_batch[:,0]=1
    batches.append(last_batch)
    output_batches.append(last_batch)
    self._last_batch = batches[-1]
    return batches,output_batches

def characters(probabilities):
  """Turn a 1-hot encoding or a probability distribution over the possible
  characters back into its (most likely) character representation."""
  return [id2char(c) for c in np.argmax(probabilities, 1)]

def batches2string(batches):
  """Convert a sequence of batches back into their (most likely) string
  representation."""
  s = [''] * batches[0].shape[0]
  for b in batches:
    s = [''.join(x) for x in zip(s, characters(b))]
  return s

