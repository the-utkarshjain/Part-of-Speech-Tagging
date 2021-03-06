# -*- coding: utf-8 -*-
"""
POS Tagging.ipynb
Implementation of Hidden Markov Model Tagger. 
"""

from torchtext.datasets import CoNLL2000Chunking
import string
import numpy as np

punctuations = string.punctuation

class HMMTagger:
  def __init__(self, train_iter):
    self.vocab = set()
    self.states = {}
    self.initial_probabilities = {}
    self.transition_probabilities = {}
    self.emission_probabilities = {}
    self.__buildComponents(train_iter)
  
  def __removePunctuations(self, sample):
    observation_sequence, state_sequence = sample[0], sample[1]
    new_observation_sequence, new_state_sequence = [], []

    for i in range(len(state_sequence)):
      if (state_sequence[i] in punctuations) or (state_sequence[i] in ['$', "''", '(', ')', ':', '``']):
        continue
      else:
        new_observation_sequence.append(observation_sequence[i])
        new_state_sequence.append(state_sequence[i])
    
    return new_observation_sequence, new_state_sequence

  def __buildComponents(self, train_iter):
    for sample in train_iter:
      observation_sequence, state_sequence = self.__removePunctuations(sample)

      if len(observation_sequence) != len(state_sequence):
        raise Exception("Raised from __buildComponents. Problem detected in __removePunctuations method.")

      if len(observation_sequence) == 0:
        continue

      self.initial_probabilities[state_sequence[0]] = self.initial_probabilities.get(state_sequence[0], 0) + 1

      for i in range(len(observation_sequence) - 1):
        observation_t = observation_sequence[i]
        state_t = state_sequence[i]
        next_state_t = state_sequence[i+1]

        self.vocab.add(observation_t)
        self.states[state_t] = self.states.get(state_t, 0) + 1
        self.emission_probabilities[(state_t, observation_t)] = self.emission_probabilities.get((state_t, observation_t), 0) + 1
        self.transition_probabilities[(state_t, next_state_t)] = self.transition_probabilities.get((state_t, next_state_t), 0) + 1
      
      self.states[state_sequence[-1]] = self.states.get(state_sequence[-1], 0) + 1
      self.emission_probabilities[(state_sequence[-1], observation_sequence[-1])] = self.emission_probabilities.get((state_sequence[-1], observation_sequence[-1]), 0) + 1

    for key, value in self.transition_probabilities.items():
      state, _ = key
      self.transition_probabilities[key] = value/self.states[state]

    for key, value in self.emission_probabilities.items():
      state, _ = key
      self.emission_probabilities[key] = value/self.states[state]
    
    for key, value in self.initial_probabilities.items():
      self.initial_probabilities[key] = self.initial_probabilities[key]/len(train_iter)

  def viterbi(self, observation_sequence):
    if observation_sequence[0] not in self.vocab:
      return None, None

    states_list = list(self.states.keys())
    viterbi_matrix = np.zeros((len(observation_sequence), len(self.states.keys())))
    backward_matrix = np.zeros((len(observation_sequence), len(self.states.keys())))

    for i in range(len(states_list)):
      state = states_list[i]
      viterbi_matrix[0][i] = self.initial_probabilities.get(state, 0) * self.emission_probabilities.get((state, observation_sequence[0]), 0)
      backward_matrix[0][i] = 0

    for i in range(1, len(observation_sequence)):
      for s in range(len(states_list)):
        moment_matrix = [viterbi_matrix[i-1][j] * self.transition_probabilities.get((states_list[j], states_list[s]), 0) for j in range(len(states_list))]
        moment_matrix = np.array(moment_matrix) * self.emission_probabilities.get((states_list[s], observation_sequence[i]), 0)

        max_index = np.argmax(moment_matrix)
        viterbi_matrix[i][s] = moment_matrix[max_index]
        backward_matrix[i][s] = max_index
    
    best_path_probability_index = np.argmax(viterbi_matrix[-1])
    best_path_probability = viterbi_matrix[-1][best_path_probability_index]
    best_path = [states_list[best_path_probability_index]]

    for i in range(len(observation_sequence) - 2, -1, -1):
      best_path_probability_index = int(backward_matrix[i+1][best_path_probability_index])
      best_path.append(states_list[best_path_probability_index])

    return best_path_probability, best_path[::-1]
  
  def test(self, test_iter, iterations = None):
    for sample in test_iter:
      observation_sequence, state_sequence = self.__removePunctuations(sample)
      best_path_probability, best_path = self.viterbi(observation_sequence)
      
      if(best_path == None):
        continue
      
      print(best_path)
      print(state_sequence)
      print()

      if iterations is not None:
        iterations -= 1
        if iterations <= 0:
          return

train_iter = CoNLL2000Chunking(split='train')
test_iter = CoNLL2000Chunking(split='test')

HMM = HMMTagger(train_iter)
HMM.test(test_iter, 1)
