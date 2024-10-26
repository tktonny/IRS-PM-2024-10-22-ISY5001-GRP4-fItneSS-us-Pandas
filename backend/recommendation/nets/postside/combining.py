import torch
from .bert import get_bert_embeddings
from .resnet import get_image_embeddings
#from .sentence_bert import get_sentence_bert_embeddings
from torch.nn import MultiheadAttention
import torch.nn as nn


def concatenation(img_embeddings, title_embeddings, text_embeddings):
    # Concatenate image, title, and text embeddings
    # Assuming img_embeddings and text_embeddings are both torch tensors
    multimodal_embeddings = torch.cat((img_embeddings, title_embeddings, text_embeddings), dim=1)
    return multimodal_embeddings


def weighted_sum(img_embeddings, text_embeddings, weight_img, weight_text):
    image_embeddings_pooled = torch.mean(img_embeddings, dim=0)  # [batch_size, 2048]

    # Optionally, apply a linear projection to match the text embedding size (e.g., 384)
    image_projection = torch.nn.Linear(2048, 768)
    projected_image_embeddings = image_projection(image_embeddings_pooled)  # [batch_size, 384]
    return weight_text * text_embeddings + weight_img * projected_image_embeddings

def attention_mechanisms(img_embeddings, title_embeddings, text_embeddings):
    image_embeddings_pooled = torch.mean(img_embeddings, dim=0)
    image_projection = torch.nn.Linear(2048, 384)
    projected_image_embeddings = image_projection(image_embeddings_pooled) + 0*title_embeddings # [batch_size, 384]
    text_embeddings_pooled = torch.mean(text_embeddings, dim=0)  # [batch_size, 2048]
    text_projection = torch.nn.Linear(768,384)
    projected_text_embeddings = text_projection(text_embeddings_pooled)+0*title_embeddings  # [batch_size, 384]

    attention = MultiheadAttention(embed_dim=384, num_heads=8)
    attn_output, attn_weights = attention(projected_image_embeddings, title_embeddings, projected_text_embeddings)
    return attn_output, attn_weights

def bilinear_pooling(emb1, emb2):
    return torch.einsum('bi,bj->bij', emb1, emb2).view(emb1.size(0), -1)

def outer_product(t1, t2, t3):
    return torch.einsum('bi,bj,bk->bijk', t1, t2, t3).view(t1.size(0), -1)

class CoAttention(nn.Module):
    def __init__(self, embed_dim):
        super(CoAttention, self).__init__()
        self.text_att = MultiheadAttention(embed_dim, num_heads=8)
        self.image_att = MultiheadAttention(embed_dim, num_heads=8)

    def forward(self, text, image):
        text_to_image, _ = self.text_att(text, image, image)
        image_to_text, _ = self.image_att(image, text, text)
        return text_to_image, image_to_text

class GatedMultimodalUnit(nn.Module):
    def __init__(self, input_dim):
        super(GatedMultimodalUnit, self).__init__()
        self.gate = nn.Linear(input_dim * 2, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, modality1, modality2):
        combined = torch.cat((modality1, modality2), dim=1)
        gate_value = self.sigmoid(self.gate(combined))
        output = gate_value * modality1 + (1 - gate_value) * modality2
        return output

'''
torch.Size([1, 3200])
torch.Size([1, 768])
torch.Size([1, 384])
torch.Size([1, 1572864])
torch.Size([1, 603979776])
torch.Size([1, 384]) torch.Size([1, 384])
torch.Size([1, 384])
'''

'''
title = "title"
text = "This is an example sentence."
img_path = "/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/celebA_50k/000001.jpg"

img_embeddings = get_image_embeddings(img_path)
title_embeddings = get_sentence_bert_embeddings(title)
text_embeddings = get_bert_embeddings(text)


multimodal_embeddings = concatenation(img_embeddings, title_embeddings, text_embeddings)
print(multimodal_embeddings.shape)  

weight_text = 0.6
weight_image = 0.4
multimodal_embeddings = weighted_sum(img_embeddings, text_embeddings, weight_image, weight_text)
print(multimodal_embeddings.shape)  

multimodal_embeddings,wights = attention_mechanisms(img_embeddings, title_embeddings, text_embeddings)
print(multimodal_embeddings.shape)  

multimodal_embeddings = bilinear_pooling(img_embeddings, text_embeddings)
print(multimodal_embeddings.shape)  

multimodal_embeddings = outer_product(img_embeddings, title_embeddings, text_embeddings)
print(multimodal_embeddings.shape)  


image_embeddings_pooled = torch.mean(img_embeddings, dim=0)
image_projection = torch.nn.Linear(2048, 384)
projected_image_embeddings = image_projection(image_embeddings_pooled) + 0*title_embeddings 
text_embeddings_pooled = torch.mean(text_embeddings, dim=0)  
text_projection = torch.nn.Linear(768,384)
projected_text_embeddings = text_projection(text_embeddings_pooled)+0*title_embeddings  

coattention_layer = CoAttention(embed_dim=384)
image_to_text, text_to_image  = coattention_layer(projected_image_embeddings, projected_text_embeddings)
print(image_to_text.shape, text_to_image.shape)

gmu = GatedMultimodalUnit(input_dim=384)
multimodal_embeddings = gmu(projected_image_embeddings, projected_text_embeddings)
print(multimodal_embeddings.shape)  
'''