import torch
from Docbert import docbert
from transformers import RobertaTokenizer, RobertaModel

device = torch.device('cpu')

tokenizer = RobertaTokenizer.from_pretrained('distilbert/distilroberta-base', do_lower_case=False)
internal_bert = RobertaModel.from_pretrained('distilbert/distilroberta-base')

# Load the model
model = docbert.DocBert(internal_bert, 512, 3)

# Load the weights
model.load_state_dict(torch.load("distilroberta_60e_1-0.03-0.2w_8e-4lr", weights_only=True))

docbert.do_inference(model, tokenizer, "The company will go under :(")