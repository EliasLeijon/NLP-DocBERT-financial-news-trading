import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
from torch.utils.data import Dataset
import math

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class FinancialNewsDataset(Dataset):
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

                if max_size and i >= max_size:
                    break
                try:
                  header, body, sentiment_value =  line.strip().split(",")
                  count += 1
                except:
                  print( "Error when processing the following data ", [line.rstrip().split('|')])
                # print(sentence)
                financial_news = f"{header} {body}"
                self.xs.append(financial_news)
                self.ys.append(int(sentiment_value)+1) # make sure negative/neutral/positive is labelled correct
                self.sentence_lengths = np.append(self.sentence_lengths, len(financial_news.split(" ")))

    def __getitem__(self, idx):
        return self.xs[idx], self.ys[idx]

    def __len__(self):
        return len(self.xs)
    
class FinancialNewsDataset_shell_class(FinancialNewsDataset):
    def __init__(self, xs, ys, sentence_lengths):
      self.xs = xs
      self.ys = ys
      self.sentence_lengths = sentence_lengths

class DocBert(torch.nn.Module):
    def __init__(self, bert,  hidden_dim, num_labels):
        super(DocBert, self).__init__()
        self.bert =  bert.to(device)
        for param in self.bert.parameters():
            param.requires_grad = False
        self.lstm = nn.LSTM(bert.config.hidden_size, hidden_dim, batch_first=True).to(device)
        self.relu = nn.ReLU()
        self.linear = nn.Linear(hidden_dim, num_labels).to(device)

    def forward(self, x, attention_mask):
      output = []
      for x_seq, a_seq in zip(x, attention_mask):
        output.append(self.bert(x_seq, a_seq)[0][:,0,:])

      _ , (output, _) = self.lstm(torch.stack(output, dim=1))
      output = self.relu(output)
      output = self.linear(torch.squeeze(output, dim=0))
      return output

def tensor_split(text1, seq_size=200, overlap=50, add_to_start = 2):
  l_total = []
  l_parcial = []
  cls_tokens = torch.unsqueeze(torch.as_tensor([add_to_start]* text1.shape[0]), dim=1)
  if text1.shape[1]//(seq_size-overlap) >0:
    n = text1.shape[1]//(seq_size-overlap)
  else: 
    n = 1
  for w in range(n):
    if w == 0:
      # l_parcial = torch.concat([cls_tokens, text1[:,:seq_size]], dim=1)
      l_parcial = text1[:,:seq_size]
      l_total.append(l_parcial.to(device))
    else:
      # l_parcial = torch.concat([cls_tokens, text1[:,w*(seq_size-overlap):w*(seq_size-overlap) + seq_size]], dim=1)
      l_parcial = text1[:,w*(seq_size-overlap):w*(seq_size-overlap) + seq_size]
      l_total.append(l_parcial.to(device))
  return l_total

def create_collate_fn(tokenizer):
    def our_collate_fn(data):
        x = [a[0] for a in data]
        y = [a[1] for a in data]
        tokenized = tokenizer(text=x, padding='longest', return_tensors='pt')

        return tokenized['input_ids'], torch.as_tensor(y), tokenized['attention_mask']
    return our_collate_fn

def create_training_examples(dataset, tokenizer, batch_size = 64, seq_size = 200, overlap = 50):
    batch_sort_order = np.array_split(dataset.sentence_lengths.argsort()[::-1], round(len(dataset) / batch_size))
    our_collate_fn = create_collate_fn(tokenizer)
    tokenized_train_data = DataLoader(dataset, collate_fn=our_collate_fn, batch_sampler=batch_sort_order) #

    for bindex, (bx, by, ba) in enumerate(tokenized_train_data):
        by = by.type(torch.LongTensor)
        yield tensor_split(bx, seq_size, overlap), tensor_split(ba, seq_size, overlap, add_to_start=1), by.to(device)


def divide_dataset_to_train_and_test(SNLIDataset, shell_class, percentage_to_train):
    random_indices = torch.randperm(len(SNLIDataset.xs))
    num_of_sent_in_train = math.floor(len(SNLIDataset.xs)*(percentage_to_train))
 
    train_dataset_xs = np.array(list(map(SNLIDataset.xs.__getitem__, random_indices[0:num_of_sent_in_train])))
    train_dataset_ys = np.array(list(map(SNLIDataset.ys.__getitem__, random_indices[0:num_of_sent_in_train])))
    train_dataset_sent_lengths = np.array(list(map(SNLIDataset.sentence_lengths.__getitem__, random_indices[0:num_of_sent_in_train])))


    test_dataset_xs = np.array(list(map(SNLIDataset.xs.__getitem__, random_indices[num_of_sent_in_train:])))
    test_dataset_ys = np.array(list(map(SNLIDataset.ys.__getitem__, random_indices[num_of_sent_in_train:])))
    test_dataset_sent_lengths = np.array(list(map(SNLIDataset.sentence_lengths.__getitem__, random_indices[num_of_sent_in_train:])))
  
    train_dataset = shell_class(train_dataset_xs, train_dataset_ys, train_dataset_sent_lengths)

    test_dataset = shell_class(test_dataset_xs, test_dataset_ys, test_dataset_sent_lengths)
    

    return train_dataset, test_dataset

def do_inference(model, tokenizer, text):
    model.eval()
    tokenized = tokenizer(text, return_tensors="pt", padding="longest")

    x, a = tokenized['input_ids'], tokenized['attention_mask']
    xs, a_s = tensor_split(x, seq_size=200, overlap=50), tensor_split(a, seq_size=200, overlap=50, add_to_start=1)

    preds = model(xs, a_s)
    return preds