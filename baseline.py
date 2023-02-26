# -*- coding: utf-8 -*-
"""financialNewsBert.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Yr_gRBuW9s-WOel13bcTYIKqqWZcQ3Mq

## Importing swe-BERT for initial training
"""

import torch
import numpy as np
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

# collab command to install transformers
# !pip install transformers
# !pip install tqdm

from torch.utils.data import Dataset


import re
def clean_txt (text):
  text = re.sub("¹", "", text)
  text=re.sub("(\\W)+","  ", text)
  return text


class SNLIDataset(Dataset):

    def __init__(self, filename, max_size=None):
        super().__init__()
        self.xs = []
        self.ys = []
        self.sentence_lengths = np.array([])
        count = 0
        with open(filename, encoding="utf-8") as source:
            for i, line in enumerate(source):
                if i == 0:
                  continue
                # print(line)
                if max_size and i >= max_size:
                    break
                try:
                  sentence, sentiment_value = line.rstrip().split('|') # Delimeter to be chosen
                  count += 1
                except:
                  print( "Error when processing the following data ", [line.rstrip().split('|')])
                # print(sentence)
                self.xs.append(clean_txt(sentence))
                self.ys.append(int(sentiment_value)) # make sure negative/neutral/positive is labelled correct
                self.sentence_lengths = np.append(self.sentence_lengths, len(sentence.split(" ")))

    def __getitem__(self, idx):
        return self.xs[idx], self.ys[idx]

    def __len__(self):
        return len(self.xs)

"""## Create all datasets"""

financial_news_train_dataset = SNLIDataset('./Financial Data/financial_phrases_labeled_psv_train.csv', max_size=4000)
financial_news_test_dataset = SNLIDataset('./Financial Data/financial_phrases_labeled_psv_test.csv')
amazon_review_dataset = SNLIDataset('./amazon-review-data/amazon_review_data_psv.csv', max_size = 400)
# data = financial_news_train_dataset[121]
print(financial_news_train_dataset.xs[0])
print(financial_news_test_dataset.xs[0])
print(max(amazon_review_dataset.sentence_lengths))
print(max(financial_news_train_dataset.sentence_lengths))
print(min(financial_news_train_dataset.sentence_lengths))

"""## Import swedish bert"""

# !pip install transformers
from transformers import BertTokenizer, BertForSequenceClassification

tokenizer = BertTokenizer.from_pretrained('KB/bert-base-swedish-cased', do_lower_case=True)

tokenized = tokenizer(text=financial_news_train_dataset[1][0], padding='longest', return_tensors='pt')
print(financial_news_train_dataset[1][0])
print(tokenized.input_ids)
print(tokenized)

"""### Define colate function that tokenizes"""

def our_collate_fn(data):
    x = [a[0] for a in data]
    y = [a[1] for a in data]
    tokenized = tokenizer(text=x, padding='longest', return_tensors='pt')

    if tokenized['input_ids'].shape[1] > 512:
      return tokenized['input_ids'][:,0:511], torch.as_tensor(y)[0:511], tokenized['attention_mask'][:,0:511]
    return tokenized['input_ids'], torch.as_tensor(y), tokenized['attention_mask']

"""#### Functions for training and testing a model"""

from torch.utils.data import DataLoader
from tqdm import tqdm
def train_model(train_data, batch_size):
  batch_sort_order = np.array_split(train_data.sentence_lengths.argsort()[::-1], round(len(train_data) / batch_size))
  tokenized_train_data = DataLoader(train_data, collate_fn=our_collate_fn, batch_sampler=batch_sort_order) #
  
  # print(tokenized_train_data)
  # for batch in tokenized_train_data:
  #     for sent_pair in batch[0]:
  #       print(sent_pair)
  #     print(batch)
  #     break
  

  model = BertForSequenceClassification.from_pretrained('KB/bert-base-swedish-cased', num_labels=3)
  model = model.to(device)
  optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)
  # softmax = torch.nn.Softmax(dim=1)
  epochs = 1

  for _ in range(epochs):
    model.train()

    with tqdm(total=len(train_data)) as pbar:

      for bindex, (bx, by, ba) in enumerate(tokenized_train_data):
        bx, by, ba = bx.to(device), by.to(device), ba.to(device)
        optimizer.zero_grad()
        # forward pass
        train_output = model(bx, labels=by, attention_mask=ba)
        # backward pass
        train_output.loss.backward()
        optimizer.step()
        pbar.update(len(bx))
  return model

def evaluate_model(model, valid_data, batch_size):
    batch_sort_order = np.array_split(valid_data.sentence_lengths.argsort()[::-1], round(len(valid_data) / batch_size))
    tokenized_valid_data = DataLoader(valid_data, batch_sampler=batch_sort_order, collate_fn=our_collate_fn)
    model.eval()
    valids = []
    for bx, by, ba in tokenized_valid_data:
      with torch.no_grad():
        bx, by, ba = bx.to(device), by.to(device), ba.to(device)
        # forward pass
        try:
          eval_output = model(bx, attention_mask=ba)
          guess = torch.argmax(eval_output.logits, dim=1)
          valids.append(sum(guess == by)/len(by))
        except Exception as e:
          print(bx.shape, by.shape)
          print(ba.shape)
          print(e)
        
    print('Accuracy: {}'.format(sum(valids)/len(valids)))

"""## Train and save the financial model"""

financial_trained_model = train_model(financial_news_train_dataset, 64)
evaluate_model(financial_trained_model, financial_news_test_dataset)
financial_trained_model.save_pretrained("./financial_trained_model")

"""## Load the financial model and evaluate it on similar test-data 
accuracy should be 88%+
"""

loadedModel = BertForSequenceClassification.from_pretrained("./financial_trained_model/")
evaluate_model(loadedModel, financial_news_test_dataset, 32)

evaluate_model(loadedModel, amazon_review_dataset, 16)