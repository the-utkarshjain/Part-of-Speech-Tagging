# -*- coding: utf-8 -*-
"""
POS Tagging.ipynb
Implementation of a baseline maximum likelihood POS tagger.
"""

from torchtext.datasets import CoNLL2000Chunking

class BaseTagger:
  def __init__(self, train_iter):
    self.tag_dict = self.train(train_iter)
  
  def train(self, train_iter):
    words = {}
    word_count = {}

    for sample in train_iter:
      for i in range(len(sample[0])):
        word = sample[0][i]
        tag = sample[1][i]

        if word not in word_count.keys():
          word_count[word] = 1
        else:
          word_count[word] += 1
        
        if word not in words.keys():
          words[word] = {}
          words[word][tag] = 1
        else:
          if tag not in words[word].keys():
            words[word][tag] = 1
          else:
            words[word][tag] += 1
      
    return words
  
  def lookup(self, word):
    if word in self.tag_dict.keys():
      word_dict = sorted(self.tag_dict[word].items(), key=lambda kv: kv[1], reverse = True)
      
      for key, value in word_dict:
        return key
    else:
      return False

  def test(self, test_iter):
    total_tags = 0
    total_correct = 0
    total_wrong = 0
    total_OOV = 0
    total_OOV_correct = 0
    total_OOV_wrong = 0

    for sample in test_iter:
      for i in range(len(sample[0])):
        total_tags += 1

        word = sample[0][i]
        real_tag = sample[1][i]

        if word in self.tag_dict.keys():
          word_dict = sorted(self.tag_dict[word].items(), key=lambda kv: kv[1], reverse = True)

          for key, value in word_dict:
            predicted_tag = key
            break
    
          if(predicted_tag == real_tag):
            total_correct += 1
          else:
            total_wrong += 1

        else:
          total_OOV += 1

          if word[0].isupper():
            predicted_tag = ['NNP', 'NNPS']
          elif word.endswith('ed'):
            predicted_tag = ['VBD', 'VBN']
          elif word.endswith('ly'):
            predicted_tag = ['RB', 'RBR', 'RBS']
          elif self.lookup(sample[0][min(i+1, len(sample[0]) - 1)]) == 'NN':
            if i+1 > (len(sample[0]) - 1):
              predicted_tag = ['NN']
            else:
              predicted_tag = ['JJ', 'JJR', 'JJS']
          else:
            predicted_tag = ['NN']
          
          if real_tag in predicted_tag:
            total_correct += 1
            total_OOV_correct += 1
          else:
            total_wrong += 1
            total_OOV_wrong += 1
    
    return total_correct/total_tags, total_OOV_correct/total_OOV

train_iter = CoNLL2000Chunking(split='train')
test_iter = CoNLL2000Chunking(split='test')

baseTagger = BaseTagger(train_iter)
correct_accuracy, OOV_accuracy = baseTagger.test(test_iter)
print(correct_accuracy, OOV_accuracy)
