import faiss
import numpy as np
#import lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import accuracy_score
import tensorflow as tf
from tensorflow.keras.layers import Input, Embedding, Dense, Concatenate, Flatten, Attention
from tensorflow.keras.models import Model
from .nets.postside.postside import reduce_dimensionality, post_embeddings

def main():
    print(create_post_embedding('/Users/macbookair/Documents/Project/fItneSS_us/backend/recommendation/datasets/celebA_50k/000001.jpg', 'title', 'This is an example sentence.'))
    #recall()
    #rough_ranking()
    #fine_ranking()

def create_post_embedding(img_path, title, description):
    return(post_embeddings(img_path, title, description))

def search_similar_posts(query_embedding, index, post_ids, k=100):
    D, I = index.search(query_embedding.reshape(1, -1), k)  # D: Distances, I: Indices
    return post_ids[I[0]], D[0]

def recall(embeddings_path, user_embeddings):
    embeddings, post_ids = read_embeddings(embeddings_path)

    # Normalize the embeddings for cosine similarity
    faiss.normalize_L2(embeddings)

    # Create the index
    index = faiss.IndexFlatL2(64)  # Use IndexFlatIP for cosine similarity (inner product)
    index.add(embeddings)

    similar_post_ids, distances = search_similar_posts(user_embeddings, index, post_ids, 100)
    print("Similar Post IDs:", similar_post_ids)
    print("Distances:", distances)
    return similar_post_ids

def rough_ranking():
    # 生成一个分类数据集
    X, y = make_classification(n_samples=10000, n_features=20, random_state=42)

    # 分割数据集为训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 训练 GBDT 模型
    gbdt_model = lgb.LGBMClassifier(n_estimators=100, max_depth=4)
    gbdt_model.fit(X_train, y_train)

    # 获取训练数据在 GBDT 模型上的叶子节点索引
    train_leaves = gbdt_model.predict(X_train, pred_leaf=True)
    test_leaves = gbdt_model.predict(X_test, pred_leaf=True)

    # 使用 OneHotEncoder 对叶子节点进行编码
    encoder = OneHotEncoder()
    X_train_leaves = encoder.fit_transform(train_leaves)
    X_test_leaves = encoder.transform(test_leaves)

    # 训练 LR 模型
    lr_model = LogisticRegression(max_iter=1000)
    lr_model.fit(X_train_leaves, y_train)

    # 在测试集上进行预测
    y_pred = lr_model.predict(X_test_leaves)

    # 评估模型
    accuracy = accuracy_score(y_test, y_pred)
    print(f'GBDT + LR Accuracy: {accuracy}')

def fine_ranking():
    # 生成一个分类数据集
    X, y = make_classification(n_samples=10000, n_features=20, random_state=42)

    # 分割数据集为训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 假设特征向量的维度为 20
    feature_dim = 20

    # 输入层
    user_input = Input(shape=(feature_dim,), name='user_input')
    item_input = Input(shape=(feature_dim,), name='item_input')

    # 嵌入层
    user_embedding = Embedding(input_dim=10000, output_dim=8, input_length=feature_dim)(user_input)
    item_embedding = Embedding(input_dim=10000, output_dim=8, input_length=feature_dim)(item_input)

    # Attention 机制
    attention = Attention()([user_embedding, item_embedding])
    attention = Flatten()(attention)

    # 拼接用户和物品的嵌入向量
    concat = Concatenate()([Flatten()(user_embedding), Flatten()(item_embedding), attention])

    # 全连接层
    dense = Dense(128, activation='relu')(concat)
    dense = Dense(64, activation='relu')(dense)
    output = Dense(1, activation='sigmoid')(dense)

    # 构建模型
    model = Model(inputs=[user_input, item_input], outputs=output)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # 训练模型
    model.fit([X_train, X_train], y_train, epochs=10, batch_size=32, validation_split=0.2)

    # 在测试集上进行预测
    y_pred = model.predict([X_test, X_test])
    y_pred = (y_pred > 0.5).astype(int)

    # 评估模型
    accuracy = accuracy_score(y_test, y_pred)
    print(f'DIN with Attention Mechanism Accuracy: {accuracy}')

def read_embeddings(file_path, dim=64):
    # Adjust dtype based on how data is stored and the precise structure
    dt = np.dtype([('embedding', np.float32, (dim,)), ('post_id', np.int32)])
    data = np.fromfile(file_path, dtype=dt)
    embeddings = np.array([d['embedding'] for d in data])
    post_ids = np.array([d['post_id'] for d in data])
    return embeddings, post_ids

if __name__ == '__main__':
    main()