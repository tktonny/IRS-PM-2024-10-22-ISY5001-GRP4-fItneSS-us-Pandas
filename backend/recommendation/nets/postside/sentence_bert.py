'''
from sentence_transformers import SentenceTransformer
import torch

# Check for GPU availability
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def get_sentence_bert_embeddings(texts):
    # Load pretrained Sentence-BERT model
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    model = model.to(device)  # Move model to device (GPU if available)
    
    # Check if input is a single string or a list of strings
    if isinstance(texts, str):
        texts = [texts]  # Convert single sentence to list
    
    # Get sentence embeddings and convert them to tensors
    sentence_embeddings = model.encode(texts, convert_to_tensor=True, device=device)
    
    return sentence_embeddings
'''
'''
# Example usage:
sentences = ["This is an example sentence.", "Sentence-BERT is great for text embeddings."]
embeddings = get_sentence_bert_embeddings(sentences)

print(type(embeddings))  # Should show <class 'torch.Tensor'>
print(embeddings.shape)  # Output shape (number_of_sentences, embedding_dim)
'''