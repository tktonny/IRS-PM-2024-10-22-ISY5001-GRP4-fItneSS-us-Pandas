from transformers import BertTokenizer, BertModel
import torch

def get_bert_embeddings(text):
    # Load pretrained BERT model and tokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')
    model.eval()  # Set to evaluation mode

    # Tokenize and encode text
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)

    # Get text embeddings
    with torch.no_grad():
        outputs = model(**inputs)
        # Use the embeddings from the [CLS] token, which is commonly used for sentence-level embeddings
        text_embeddings = outputs.last_hidden_state[:, 0, :]

    return text_embeddings
'''
# Example text
text = "This is an example sentence."
text_embeddings = get_bert_embeddings(text)
print(text_embeddings.shape)  # Should be [1, 768] for BERT base
'''