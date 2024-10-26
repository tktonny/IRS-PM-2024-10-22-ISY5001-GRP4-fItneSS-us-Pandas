from .bert import get_bert_embeddings
#from .sentence_bert import get_sentence_bert_embeddings
from .resnet import get_image_embeddings
from .combining import concatenation, weighted_sum, attention_mechanisms, bilinear_pooling, outer_product, CoAttention, GatedMultimodalUnit
import torch
import numpy as np
import pymysql

def tensor_to_bytes(tensor):
    tensor_np = tensor.numpy()
    tensor_bytes = tensor_np.tobytes()
    return tensor_bytes

def save_tensor_to_mysql(tensor, table_name, column_name):
    tensor_np = tensor.numpy()
    tensor_bytes = tensor_np.tobytes()
    
    conn = pymysql.connect(host='localhost', user='root', password='password', db='your_db')
    cursor = conn.cursor()
    
    cursor.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (%s)", (tensor_bytes,))
    conn.commit()
    
    cursor.close()
    conn.close()

def load_tensor_from_mysql(table_name, column_name):
    conn = pymysql.connect(host='localhost', user='root', password='password', db='your_db')
    cursor = conn.cursor()

def reduce_dimensionality(embeddings, target_dim):
    projection = torch.nn.Linear(embeddings.shape[1], target_dim)
    projected_embeddings = projection(embeddings)
    return projected_embeddings

def post_embeddings(img_path, title, text):
    img_embeddings = get_image_embeddings(img_path)
    #title_embeddings = get_sentence_bert_embeddings(title)
    title_embeddings = get_bert_embeddings(title)
    text_embeddings = get_bert_embeddings(text)
    
    multimodal_embeddings = concatenation(img_embeddings, title_embeddings, text_embeddings)    #shape [1, 3200]
    
    '''
    weight_text = 0.6
    weight_image = 0.4
    multimodal_embeddings = weighted_sum(img_embeddings, text_embeddings, weight_image, weight_text)    #shape [1, 768]
    '''
    
    '''
    multimodal_embeddings,wights = attention_mechanisms(img_embeddings, title_embeddings, text_embeddings)  #shape [1, 384]
    '''
    
    '''
    multimodal_embeddings = bilinear_pooling(img_embeddings, text_embeddings)    #shape [1, 1572864]
    '''
    
    '''
    multimodal_embeddings = outer_product(img_embeddings, title_embeddings, text_embeddings)    #shape [1, 603979776]
    '''
    
    '''
    projected_image_embeddings = reduce_dimensionality(img_embeddings, 384) + 0*title_embeddings
    projected_text_embeddings = reduce_dimensionality(text_embeddings, 384) + 0*title_embeddings
    
    coattention_layer = CoAttention(embed_dim=384)
    image_to_text, text_to_image  = coattention_layer(projected_image_embeddings, projected_text_embeddings)    #shape [1, 384] [1, 384]
    multimodal_embeddings = torch.cat((image_to_text, text_to_image), dim=1)    #shape [1, 768]
    '''
    
    '''
    projected_image_embeddings = reduce_dimensionality(img_embeddings, 384) + 0*title_embeddings
    projected_text_embeddings = reduce_dimensionality(text_embeddings, 384) + 0*title_embeddings
    gmu = GatedMultimodalUnit(input_dim=384)
    multimodal_embeddings = gmu(projected_image_embeddings, projected_text_embeddings)    #shape [1, 384]
    '''

    return multimodal_embeddings

'''
def main():
    title = "title"
    text = "This is an example sentence."
    img_path = '/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/celebA_50k/000001.jpg'
    
    multimodal_embeddings = post_embeddings(img_path, title, text)
    print(multimodal_embeddings.shape)

if __name__ == "__main__":
    main()
'''