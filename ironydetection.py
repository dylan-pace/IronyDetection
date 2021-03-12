# -*- coding: utf-8 -*-
"""IronyDetection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15742ZUARWTz8QT_wgu9vuDD5RyElINDF
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import re
import nltk
from scipy import stats
import matplotlib.pyplot as plt
# %matplotlib inline
import seaborn as sns
sns.set()
from sklearn import preprocessing, linear_model, model_selection, neighbors, svm, naive_bayes, metrics, tree

irony_train_df = pd.read_csv('/content/drive/MyDrive/archive/SemEval2018-Task3-master/datasets/train/SemEval2018-T3-train-taskA_emoji.txt', delimiter="\t")

irony_train_df.head(10)

"""**Pre-Processing**"""

irony_train_df.columns = ['Index', 'Label', 'Tweet']

irony_train_df = irony_train_df[['Index', 'Tweet', 'Label']]

irony_train_df.info()

def clean_text(text):
  text = re.sub('http?://\S+|www\.\S+', '', text)
  text = re.sub('@[^\s]+','', text)
  return text

# removes useless emoticons and punctuation
irony_train_df['Tweet'] = irony_train_df['Tweet'].str.replace("[^a-zA-Z#']", " " )

# removes useless emoticons and punctuation
irony_train_df['Tweet'] = irony_train_df['Tweet'].str.replace("http", " " )

irony_train_df['Tweet'] = irony_train_df['Tweet'].str.lower()

text_train = irony_train_df.Tweet.apply(lambda x: clean_text(x))
irony_train_df['Tweet'] = irony_train_df.Tweet.apply(lambda x: clean_text(x))

irony_train_df = irony_train_df.set_index('Index')

irony_train_df.head()

"""**Visualisations**"""

# find the most common occuring words in all the tweets
all_words = ' '.join([text for text in text_train])#irony_train_df['Tweet']])
from wordcloud import WordCloud
# sets up the word cloud
word_cloud = WordCloud(width=800, height=500, random_state=21, max_font_size=110).generate(all_words)

# plots the most common occuring words in a word cloud
plt.figure(figsize=(10, 7))
plt.imshow(word_cloud, interpolation='bilinear')
plt.axis('off')
plt.show()

barData = pd.read_csv('/content/drive/MyDrive/archive/SemEval2018-Task3-master/datasets/train/SemEval2018-T3-train-taskA_emoji.txt', delimiter="\t")
sns.countplot(x = 'Label',  data = barData, palette = 'magma')
plt.title('The Amount of Ironic Tweets')
plt.xlabel('Tweet Classification')
plt.ylabel('Number of Tweets')
plt.show()

#The data is perfectly balanced, as all things should be.

"""**Latent Dirichlet Allocation**"""

from sklearn.feature_extraction.text import TfidfVectorizer
vect = TfidfVectorizer(max_features=10000, max_df=.15)
X = vect.fit_transform(text_train)#irony_train_df.Tweet)

from sklearn.decomposition import LatentDirichletAllocation
lda = LatentDirichletAllocation(n_components=10, learning_method='batch', max_iter=25, random_state=0)
document_topics = lda.fit_transform(X)

print("lds.components_.shape: {}".format(lda.components_.shape))

sorting = np.argsort(lda.components_, axis=1)[:, ::-1]
feature_names = np.array(vect.get_feature_names())

!pip install mglearn

import mglearn
mglearn.tools.print_topics(topics=range(10), 
                           feature_names=feature_names, 
                           sorting=sorting, 
                           topics_per_chunk=5, 
                           n_words=10)

# Commented out IPython magic to ensure Python compatibility.
# Load the library with the CountVectorizer method
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')
# %matplotlib inline
# Helper function
def plot_10_most_common_words(count_data, count_vectorizer):
    import matplotlib.pyplot as plt
    words = count_vectorizer.get_feature_names()
    total_counts = np.zeros(len(words))
    for t in count_data:
        total_counts+=t.toarray()[0]
    
    count_dict = (zip(words, total_counts))
    count_dict = sorted(count_dict, key=lambda x:x[1], reverse=True)[0:10]
    words = [w[0] for w in count_dict]
    counts = [w[1] for w in count_dict]
    x_pos = np.arange(len(words)) 
    
    plt.figure(2, figsize=(15, 15/1.6180))
    plt.subplot(title='10 most common words')
    sns.set_context("notebook", font_scale=1.25, rc={"lines.linewidth": 2.5})
    sns.barplot(x_pos, counts, palette='husl')
    plt.xticks(x_pos, words, rotation=90) 
    plt.xlabel('words')
    plt.ylabel('counts')
    plt.show()
# Initialise the count vectorizer with the English stop words
count_vectorizer = CountVectorizer(stop_words='english')
# Fit and transform the processed titles
count_data = count_vectorizer.fit_transform(text_train)#irony_train_df['Tweet'])
# Visualise the 10 most common words
plot_10_most_common_words(count_data, count_vectorizer)

import warnings
warnings.simplefilter("ignore", DeprecationWarning)
# Load the LDA model from sk-learn
from sklearn.decomposition import LatentDirichletAllocation as LDA
 
# Helper function
def print_topics(model, count_vectorizer, n_top_words):
    words = count_vectorizer.get_feature_names()
    for topic_idx, topic in enumerate(model.components_):
        print("\nTopic #%d:" % topic_idx)
        print(" ".join([words[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
        
# Tweak the two parameters below
number_topics = 10
number_words = 10
# Create and fit the LDA model
lda = LDA(n_components=number_topics, n_jobs=-1)
lda.fit(count_data)
# Print the topics found by the LDA model
print("Topics found via LDA:")
print_topics(lda, count_vectorizer, number_words)

"""**Rescaling with TF-IDF**"""

text_train, y_train = irony_train_df.Tweet, irony_train_df.Label

from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import learning_curve, GridSearchCV
pipe = make_pipeline(TfidfVectorizer(min_df=5),
                     LogisticRegression())
param_grid = {'logisticregression__C': [0.001, 0.01, 0.1, 1, 10]}
grid = GridSearchCV(pipe, param_grid, cv=5)
grid.fit(text_train, y_train)

from sklearn.model_selection import GridSearchCV
vectorizer = grid.best_estimator_.named_steps["tfidfvectorizer"]
X_train = vectorizer.transform(irony_train_df['Tweet'])
max_value = X_train.max(axis=0).toarray().ravel()
sorted_by_tfidf = max_value.argsort()
feature_names = np.array(vectorizer.get_feature_names())

print("Features with the lowest tfidf: \n{}".format(
    feature_names[sorted_by_tfidf[:20]]
))

print("Features with the highest tfidf: \n{}".format(
    feature_names[sorted_by_tfidf[-20:]]
))

import mglearn
mglearn.tools.visualize_coefficients(
    grid.best_estimator_.named_steps["logisticregression"].coef_,
    feature_names, n_top_features=40
)

"""**K-Means Clustering Unsupervised**"""

from sklearn.cluster import KMeans

vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(text_train)

true_k = 2
model = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1)
model.fit(X)

order_centroids = model.cluster_centers_.argsort()[:, ::-1]
terms = vectorizer.get_feature_names()

for i in range(true_k):
 print("Cluster %d:" % i),
 for ind in order_centroids[i, :10]:
  print(' %s' % terms[ind])

"""**Machine Learning using the Bag-of-Words Method**"""

from sklearn.feature_extraction.text import CountVectorizer
# create a count vector to extract the words as bag-of-words
bow_vect = CountVectorizer(max_df=0.90, min_df=2, max_features=1000, stop_words='english')
# transform the tweets into the vectorisation
bow = bow_vect.fit_transform(irony_train_df['Tweet'])

from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import f1_score

# create the training and testing bag-of-words
train_bow = bow[:3817, :] #13240
test_bow = bow[3817:, :]

# set up a training and testing split 
xtrain_bow, xvalid_bow, ytrain, yvalid = train_test_split(train_bow, irony_train_df['Label'], random_state=42, test_size=0.2)

# instantiate the logistic regression function
lreg = LogisticRegression(solver='lbfgs', multi_class='ovr', max_iter=9999)
lreg.fit(xtrain_bow, ytrain)

# set up the predictions
prediction = lreg.predict_proba(xvalid_bow)
prediction_int = prediction[:,1] >= 0.3
prediction_int = prediction_int.astype(np.int)

# calculate the baseline accuracy
baseline_predictions = [1 for x in yvalid]
metrics.accuracy_score(yvalid, baseline_predictions)

# display the logistic regression f1 prediction
f1_score(yvalid, prediction_int)

# prediction accuracy
metrics.accuracy_score(yvalid, prediction_int)

# set up a heatmap to visualise the predictions of the logistic regression algorithm
cm = metrics.confusion_matrix(yvalid, prediction_int, labels = [0, 1])
fig, ax = plt.subplots()
sns.heatmap(cm, annot=True, fmt='d', cmap='coolwarm',cbar=False, ax=ax)
ax.set_xticklabels(['Non-Ironic','Ironic'])
ax.set_yticklabels(['Non-Ironic','Ironic'])
ax.set_xlabel('Predicted Class')
ax.set_title('Heatmap Showing the Predictions for the Logistic Regression Algorithm using Bag-of-Words.')
# I had to offset the ylim because matplotlib's newest update has caused them to go wonky otherwise
ax.set_ylim([0,2])
ax.set_ylabel('True Class');

# instantiate some machine learning functions
classifiers = [neighbors.KNeighborsClassifier(),
               naive_bayes.MultinomialNB(),
               linear_model.LogisticRegression(solver='lbfgs', multi_class='ovr', max_iter=9999),
               tree.DecisionTreeClassifier(),
               linear_model.SGDClassifier(loss="log", penalty="l2", max_iter=50),
               MLPClassifier(activation='relu', alpha=0.0001, batch_size='auto', beta_1=0.9,
               beta_2=0.999, early_stopping=False, epsilon=1e-08,
               hidden_layer_sizes=(20, 20, 20), learning_rate='constant',
               learning_rate_init=0.001, max_iter=500, momentum=0.9,
               nesterovs_momentum=True, power_t=0.5, random_state=None,
               shuffle=True, solver='adam', tol=0.0001, validation_fraction=0.1,
               verbose=False, warm_start=False)]

classifier_names = ['KNN','Multinomial NB','Logistic', 'Decision Tree', 'SGD', 'MLP']
accuracies_bow = []
f1_bow = []
macro_bow = []
# iterate through the loop, training and fitting the tweet data
for clf, name in zip(classifiers,classifier_names):
    clf.fit(xtrain_bow, ytrain)
    prediction = clf.predict_proba(xvalid_bow)
    prediction_int = prediction[:,1] >= 0.3
    prediction_int = prediction_int.astype(np.int)
    acc = metrics.accuracy_score(yvalid, prediction_int)
    accuracies_bow.append(acc)
    f1 = f1_score(yvalid, prediction_int)
    f1_bow.append(f1)
    macro = f1_score(yvalid, prediction_int, average='macro')
    macro_bow.append(macro)
# save the accuracies in a DataFrame
models_bow = pd.DataFrame({'Model':classifier_names, 'Accuracy Baseline':accuracies_bow})

# save the f1 scores to a dataframe
models_bow_f1 = pd.DataFrame({'Model':classifier_names, 'BoW F1 Baseline':f1_bow})

"""**Machine Learning using the TF-IDF Method**"""

from sklearn.feature_extraction.text import TfidfVectorizer
# create a count vector to extract the words as TF-IDF
tfidf_vect = TfidfVectorizer(max_df=0.90, min_df=2, max_features=1000, stop_words='english')
# transform the tweets into the vectorisation
tfidf = tfidf_vect.fit_transform(irony_train_df['Tweet'])

# create the training and testing tfidf sets
train_tfidf = tfidf[:3817, :] #31962
test_tfidf = tfidf[3817:, :]

# set up a training and testing split 
xtrain_tfidf, xvalid_tfidf, ytrain_tfidf, yvalid_tfidf = train_test_split(train_tfidf, irony_train_df['Label'], random_state=42, test_size=0.2)

# instantiate the logistic regression function
lreg = linear_model.SGDClassifier(loss="log", penalty="l2", max_iter=50)#LogisticRegression(solver='lbfgs', multi_class='ovr', max_iter=9999)
lreg.fit(xtrain_tfidf, ytrain_tfidf)

# set up the predictions
prediction = lreg.predict_proba(xvalid_tfidf)
prediction_int = prediction[:,1] >= 0.3
prediction_int = prediction_int.astype(np.int)

# display the model accuracy
metrics.accuracy_score(yvalid_tfidf, prediction_int)

# display the logistic regression f1 prediction
f1_score(yvalid_tfidf, prediction_int)

# set up a heatmap to visualise the predictions of the logistic regression algorithm
cm = metrics.confusion_matrix(yvalid_tfidf, prediction_int, labels = [0, 1])
fig, ax = plt.subplots()
sns.heatmap(cm, annot=True, fmt='d', cmap='coolwarm',cbar=False, ax=ax)
ax.set_xticklabels(['Non-Ironic','Ironic'])
ax.set_yticklabels(['Non-Ironic','Ironic'])
ax.set_xlabel('Predicted Class')
ax.set_title('Heatmap Showing the Predictions for the SGD Algorithm using TF-IDF.')
# I had to offset the ylim because matplotlib's newest update has caused them to go wonky otherwise
ax.set_ylim([0,2])
ax.set_ylabel('True Class');

# instantiate some machine learning functions
classifiers = [neighbors.KNeighborsClassifier(),
               naive_bayes.MultinomialNB(),
               linear_model.LogisticRegression(solver='lbfgs', multi_class='ovr', max_iter=9999),
               tree.DecisionTreeClassifier(),
               linear_model.SGDClassifier(loss="log", penalty="l2", max_iter=50),
               MLPClassifier(activation='relu', alpha=0.0001, batch_size='auto', beta_1=0.9,
               beta_2=0.999, early_stopping=False, epsilon=1e-08,
               hidden_layer_sizes=(20, 20, 20), learning_rate='constant',
               learning_rate_init=0.001, max_iter=500, momentum=0.9,
               nesterovs_momentum=True, power_t=0.5, random_state=None,
               shuffle=True, solver='adam', tol=0.0001, validation_fraction=0.1,
               verbose=False, warm_start=False)]

classifier_names = ['KNN','Multinomial NB','Logistic', 'Decision Tree', 'SGD', 'MLP']
accuracies_tfidf = []
tfidf_f1 = []
tfidf_macro = []
# iterate through the loop, training and fitting the tweet data
for clf, name in zip(classifiers,classifier_names):
    clf.fit(xtrain_tfidf, ytrain_tfidf)
    prediction = clf.predict_proba(xvalid_tfidf)
    prediction_int = prediction[:,1] >= 0.3
    prediction_int = prediction_int.astype(np.int)
    acc = metrics.accuracy_score(yvalid_tfidf, prediction_int)
    accuracies_tfidf.append(acc)
    f1 = f1_score(yvalid_tfidf, prediction_int)
    tfidf_f1.append(f1)
    macro = f1_score(yvalid_tfidf, prediction_int, average='macro')
    tfidf_macro.append(macro)
# save the accuracies in a DataFrame
models_tfidf = pd.DataFrame({'Model':classifier_names, 'Accuracy Baseline':accuracies_tfidf})

# f1 scores
models_tfidf = pd.DataFrame({'Model':classifier_names, 'F1 Baseline':tfidf_f1})

# accuracies of the algorithms for the two methods
models = pd.DataFrame({'Model':classifier_names, 'Bag-of-Words Accuracy':accuracies_bow, 'TF-IDF Accuracy':accuracies_tfidf})

models_all = pd.DataFrame({'Model':classifier_names, 'BoW Accuracy': accuracies_bow, 'TF-IDF Accuracy': accuracies_tfidf, 'BoW F1':f1_bow, 'TF-IDF F1':tfidf_f1, 'BoW Macro F1':macro_bow, 'TF-IDF Macro F1':tfidf_macro})

models_all

"""**Parameter-Tuning for the TF-IDF Logistic Regression Algorithm**"""

best = 0.0
best_f1 = 0.0
best_macro = 0.0
best_c = 0
best_solver = ''
best_multiclass = ''
# iterate through the parameter variables
for c in range(1,30):
    for solver in ['saga', 'newton-cg','lbfgs','sag']:
        for multiclass in ['ovr', 'multinomial', 'auto']:
                clf = linear_model.LogisticRegression(solver=solver, C=c, multi_class=multiclass, max_iter=9999)
                clf.fit(xtrain_tfidf, ytrain_tfidf)
                # set up the predictions
                prediction = clf.predict_proba(xvalid_tfidf)
                prediction_int = prediction[:,1] >= 0.3
                prediction_int = prediction_int.astype(np.int)
                acc = metrics.accuracy_score(yvalid_tfidf, prediction_int)
                f1 = f1_score(yvalid_tfidf, prediction_int)
                macro = f1_score(yvalid_tfidf, prediction_int, average='macro')
                # find the best parameters for the algorithm 
                if macro > best_macro:
                    best_macro = macro
                    best_c = c
                    best_solver = solver
                    best_multiclass = multiclass
                if acc > best:
                    best = acc
                if f1 > best_f1:
                    best_f1 = f1
print('Best Accuracy was '+str(best)+', the best Macro F1 was '+str(best_macro)+' and the best F1 was '+str(best_f1)+' using '+str(best_c)+' C, the '+str(best_solver)+' solver and using the multi class, '+str(best_multiclass))

"""**Parameter Tuning for the Bag-of-Words Logistic Regression Algorithm**"""

best = 0.0
best_f1 = 0.0
best_macro = 0.0
best_c = 0
best_solver = ''
best_multiclass = ''
# iterate through the parameter variables
for c in range(1,30):
    for solver in ['saga', 'newton-cg','lbfgs','sag']:
        for multiclass in ['ovr', 'multinomial', 'auto']:
                clf = linear_model.LogisticRegression(solver=solver, C=c, multi_class=multiclass, max_iter=9999)
                clf.fit(xtrain_bow, ytrain)
                # set up the predictions
                prediction = clf.predict_proba(xvalid_bow)
                prediction_int = prediction[:,1] >= 0.3
                prediction_int = prediction_int.astype(np.int)
                acc = metrics.accuracy_score(yvalid, prediction_int)
                f1 = f1_score(yvalid, prediction_int)
                macro = f1_score(yvalid, prediction_int, average='macro')
                # find the best parameters for the algorithm 
                if macro > best_macro:
                    best_macro = macro
                    best_c = c
                    best_solver = solver
                    best_multiclass = multiclass
                if acc > best:
                    best = acc
                if f1 > best_f1:
                    best_f1 = f1
print('Best Accuracy was '+str(best)+', the best Macro F1 was '+str(best_macro)+' and the best F1 was '+str(best_f1)+
      ' using '+str(best_c)+' C, the '+str(best_solver)+' solver and using the multi class, '+str(best_multiclass))

"""**Parameter Tuning for the TF-IDF SGD**"""

best = 0.0
best_f1 = 0.0
best_macro = 0.0
best_c = 0
best_solver = ''
best_multiclass = ''
# iterate through the parameter variables
for v in range(1,30):
    for penalty in ['l2', 'l1','elasticnet']:
        for lr in ['optimal']:
                clf = linear_model.SGDClassifier(loss='log', penalty=penalty, verbose=v, learning_rate=lr, max_iter=9999, shuffle=True)
                clf.fit(xtrain_tfidf, ytrain_tfidf)
                # set up the predictions
                prediction = clf.predict_proba(xvalid_tfidf)
                prediction_int = prediction[:,1] >= 0.3
                prediction_int = prediction_int.astype(np.int)
                acc = metrics.accuracy_score(yvalid_tfidf, prediction_int)
                f1 = f1_score(yvalid_tfidf, prediction_int)
                macro = f1_score(yvalid_tfidf, prediction_int, average='macro')
                # find the best parameters for the algorithm 
                if macro > best_macro:
                    best_macro = macro
                    best_v = v
                    best_penalty = penalty
                    best_lr = lr
                if acc > best:
                    best = acc
                if f1 > best_f1:
                    best_f1 = f1
print('Best Accuracy was '+str(best)+', the best Macro F1 was '+str(best_macro)+' and the best F1 was '+str(best_f1)+' using '+str(best_v)+' verbose, the '+str(best_penalty)+' penalty and using the learning rate, '+str(best_lr))

"""**Parameter Tuning for the Bag-of-Words SGD**"""

best = 0.0
best_f1 = 0.0
best_macro = 0.0
best_c = 0
best_solver = ''
best_multiclass = ''
# iterate through the parameter variables
for v in range(1,30):
    for penalty in ['l2', 'l1','elasticnet']:
        for lr in ['optimal']:
                clf = linear_model.SGDClassifier(loss='log', penalty=penalty, verbose=v, learning_rate=lr, max_iter=9999, shuffle=True)
                clf.fit(xtrain_bow, ytrain)
                # set up the predictions
                prediction = clf.predict_proba(xvalid_bow)
                prediction_int = prediction[:,1] >= 0.3
                prediction_int = prediction_int.astype(np.int)
                acc = metrics.accuracy_score(yvalid, prediction_int)
                f1 = f1_score(yvalid, prediction_int)
                macro = f1_score(yvalid, prediction_int, average='macro')
                # find the best parameters for the algorithm 
                if macro > best_macro:
                    best_macro = macro
                    best_v = v
                    best_penalty = penalty
                    best_lr = lr
                if acc > best:
                    best = acc
                if f1 > best_f1:
                    best_f1 = f1
print('Best Accuracy was '+str(best)+', the best Macro F1 was '+str(best_macro)+' and the best F1 was '+str(best_f1)+' using '+str(best_v)+' verbose, the '+str(best_penalty)+' penalty and using the learning rate, '+str(best_lr))

"""**Recurrent Neural Networks**"""

import tensorflow as tf
from sklearn.model_selection import train_test_split
# The maximum number of words to be used (most frequent)
MAX_NB_WORDS = 50000
# Max number of words in each complaint
MAX_SEQUENCE_LENGTH = 250
# This is fixed
EMBEDDING_DIM = 100
# tokenise the tweets 
tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=MAX_NB_WORDS, filters='!"#$%&()*+,-./:;<=>?@[\]^_`{|}~', lower=True)
tokenizer.fit_on_texts(irony_train_df['Tweet'].values)
word_index = tokenizer.word_index
print('Found %s unique tokens.' % len(word_index))

# find the sequence for all tweets in the dataset
X = tokenizer.texts_to_sequences(irony_train_df['Tweet'].values)
X = tf.keras.preprocessing.sequence.pad_sequences(X, maxlen=MAX_SEQUENCE_LENGTH)
# find the tensor shape
print('Shape of data tensor:', X.shape)

# find the tensor shape for the categories
Y = pd.get_dummies(irony_train_df['Label']).values
print('Shape of label tensor:', Y.shape)

# set up a train test split to get the data 
X_train, X_test, Y_train, Y_test = train_test_split(X,Y, test_size = 0.10, random_state = 42)
print(X_train.shape,Y_train.shape)
print(X_test.shape,Y_test.shape)

# sets up a method to compute the f1 score 
def get_f1(y_true, y_pred): #taken from old keras source code
    true_positives = tf.keras.backend.sum(tf.keras.backend.round(tf.keras.backend.clip(y_true * y_pred, 0, 1)))
    possible_positives = tf.keras.backend.sum(tf.keras.backend.round(tf.keras.backend.clip(y_true, 0, 1)))
    predicted_positives = tf.keras.backend.sum(tf.keras.backend.round(tf.keras.backend.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + tf.keras.backend.epsilon())
    recall = true_positives / (possible_positives + tf.keras.backend.epsilon())
    # f1 score is calculated using the prescision and recall from the predicted positives
    f1_val = 2*(precision*recall)/(precision+recall+tf.keras.backend.epsilon())
    return f1_val

import tensorflow as tf
import keras.backend as K

def f1(y_true, y_pred):
    y_pred = K.round(y_pred)
    tp = K.sum(K.cast(y_true*y_pred, 'float'), axis=0)
    # tn = K.sum(K.cast((1-y_true)*(1-y_pred), 'float'), axis=0)
    fp = K.sum(K.cast((1-y_true)*y_pred, 'float'), axis=0)
    fn = K.sum(K.cast(y_true*(1-y_pred), 'float'), axis=0)

    p = tp / (tp + fp + K.epsilon())
    r = tp / (tp + fn + K.epsilon())

    f1 = 2*p*r / (p+r+K.epsilon())
    #f1 = tf.where(tf.is_nan(f1), tf.zeros_like(f1), f1)
    return K.mean(f1)

"""**LSTM Model**"""

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard
from keras.callbacks import TensorBoard
!rm -rf ./logs/ #to delete previous runs
# %reload_ext tensorboard
#%tensorboard --logdir logs/
tensorboard = TensorBoard(log_dir="./logs")

# set up a sequential model for the f1 scores
model_f1 = tf.keras.Sequential()
model_f1.add(tf.keras.layers.Embedding(MAX_NB_WORDS, EMBEDDING_DIM, input_length=X.shape[1]))
model_f1.add(tf.keras.layers.LSTM(128, dropout=0.2, recurrent_dropout=0.2, return_sequences=True))
model_f1.add(tf.keras.layers.Dropout(0.2))
model_f1.add(tf.keras.layers.LSTM(64, return_sequences=True))
model_f1.add(tf.keras.layers.BatchNormalization())
model_f1.add(tf.keras.layers.Dense(32, activation='relu'))
model_f1.add(tf.keras.layers.Softmax())
model_f1.add(tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(16, return_sequences=True)))
model_f1.add(tf.keras.layers.LSTM(128, dropout=0.2, recurrent_dropout=0.2, return_sequences=True))
model_f1.add(tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(16, return_sequences=True)))
model_f1.add(tf.keras.layers.Flatten())
model_f1.add(tf.keras.layers.Dense(2, activation='relu'))
# compile the model using the f1 metric
model_f1.compile(loss='binary_crossentropy', optimizer='adam', metrics=[get_f1])

# how many iterations and the size of data batches
epochs = 10
batch_size = 16

# train the model using the training data
history = model_f1.fit(X_train, 
                    Y_train, 
                    shuffle=True,
                    epochs=epochs, 
                    batch_size=batch_size,
                    validation_split=0.2,
                    callbacks=[tensorboard])

# Commented out IPython magic to ensure Python compatibility.
# show tensorboard
# %tensorboard --logdir logs

model_f1.summary()

# find the loss and accuracy of the network
accr = model_f1.evaluate(X_test,Y_test)
print('Test set\n  Loss: {:0.3f}\n  Accuracy: {:0.3f}'.format(accr[0],accr[1]))

# create a line graph to show the training and testing loss
plt.title('Loss')
plt.plot(history.history['loss'], label='train')
plt.plot(history.history['val_loss'], label='test')
plt.legend()
plt.show();

# create a line graph to show the training and testing accuracy
plt.title('Macro F1')
plt.plot(history.history['get_f1'], label='train')
plt.plot(history.history['val_get_f1'], label='test')
plt.legend()
plt.show();

"""**GRU Model**"""

# set up a sequential model for the f1 scores
model_f1 = tf.keras.Sequential()
model_f1.add(tf.keras.layers.Embedding(MAX_NB_WORDS, EMBEDDING_DIM, input_length=X.shape[1]))
model_f1.add(tf.keras.layers.GRU(128, dropout=0.2, recurrent_dropout=0.2, return_sequences=True))
model_f1.add(tf.keras.layers.GRU(64, return_sequences=True))
model_f1.add(tf.keras.layers.BatchNormalization())
model_f1.add(tf.keras.layers.Dense(32, activation='relu'))
model_f1.add(tf.keras.layers.GRU(32, return_sequences=True))
model_f1.add(tf.keras.layers.GRU(16, return_sequences=True))
#model_f1.add(tf.keras.layers.SpatialDropout1D(0.2))
model_f1.add(tf.keras.layers.Flatten())
model_f1.add(tf.keras.layers.Dense(2, activation='relu'))
# compile the model using the f1 metric
model_f1.compile(loss='binary_crossentropy', optimizer='adam', metrics=[get_f1])

# how many iterations and the size of data batches
epochs = 10
batch_size = 64

# train the model using the training data
history = model_f1.fit(X_train, 
                    Y_train, 
                    shuffle=True,
                    epochs=epochs, 
                    batch_size=batch_size,
                    validation_split=0.1,
                    callbacks=[tensorboard])

# Commented out IPython magic to ensure Python compatibility.
# show tensorboard
# %tensorboard --logdir logs

model_f1.summary()

# find the loss and f1 of the network
f1 = model_f1.evaluate(X_test,Y_test)
print('Test set\n  Loss: {:0.3f}\n  F1 Score: {:0.3f}'.format(f1[0],f1[1]))

# create a line graph to show the training and testing loss
plt.title('Loss')
plt.plot(history.history['loss'], label='train')
plt.plot(history.history['val_loss'], label='test')
plt.legend()
plt.show();

# create a line graph to show the training and testing accuracy
plt.title('Macro F1')
plt.plot(history.history['get_f1'], label='train')
plt.plot(history.history['val_get_f1'], label='test')
plt.legend()
plt.show();

"""**DistilBert**"""

!pip install transformers

!pip install simpletransformers

from simpletransformers.classification import ClassificationModel
from sklearn.model_selection import train_test_split



# Create a ClassificationModel
model = ClassificationModel('distilbert', 'distilbert-base-uncased', num_labels=2, use_cuda=False)

irony_train_df.head()

xtrain, ytrain, xvalid, yvalid = train_test_split(irony_train_df, irony_train_df['Label'], test_size=0.2)

train_df = pd.DataFrame(xtrain)
eval_df = pd.DataFrame(ytrain)

# Train the model
model.train_model(train_df)

from sklearn.metrics import f1_score, accuracy_score


def f1_multiclass(labels, preds):
    return f1_score(labels, preds, average='macro')
    
result, model_outputs, wrong_predictions = model.eval_model(eval_df, f1=f1_multiclass, acc=accuracy_score)

result

"""**Bert**"""

from simpletransformers.classification import ClassificationModel
from sklearn.model_selection import train_test_split


# Create a ClassificationModel
model_bert = ClassificationModel('bert', 'bert-base-uncased', num_labels=2, use_cuda=False)

xtrain, ytrain, xvalid, yvalid = train_test_split(irony_train_df, irony_train_df['Label'], test_size=0.2)

train_df = pd.DataFrame(xtrain)
eval_df = pd.DataFrame(ytrain)

# Train the model
model_bert.train_model(train_df)

from sklearn.metrics import f1_score, accuracy_score

def f1_multiclass(labels, preds):
    return f1_score(labels, preds, average='macro')
    
result, model_outputs, wrong_predictions = model_bert.eval_model(eval_df, f1=f1_multiclass, acc=accuracy_score)

result

"""**XLNet**"""

from simpletransformers.classification import ClassificationModel
from sklearn.model_selection import train_test_split


model_xlnet = ClassificationModel('xlnet', 'xlnet-base-cased', num_labels=2, use_cuda=False)

xtrain, ytrain, xvalid, yvalid = train_test_split(irony_train_df, irony_train_df['Label'], test_size=0.2)

train_df = pd.DataFrame(xtrain)
eval_df = pd.DataFrame(ytrain)

# Train the model
model_xlnet.train_model(train_df)

from sklearn.metrics import f1_score, accuracy_score

def f1_multiclass(labels, preds):
    return f1_score(labels, preds, average='macro')
    
result, model_outputs, wrong_predictions = model_xlnet.eval_model(eval_df, f1=f1_multiclass, acc=accuracy_score)

result

"""**Flair**"""

!pip install flair

import flair
import torch

data = pd.read_csv("/content/drive/MyDrive/archive/SemEval2018-Task3-master/datasets/train/SemEval2018-T3-train-taskA_emoji.txt", encoding='latin-1', error_bad_lines=False).sample(frac=1).drop_duplicates()
 
data = irony_train_df[['Tweet', 'Label']].rename(columns={"Tweet":"text", "Label":"labels"})
 
data['labels'] = '__labels__' + data['labels'].astype(str)
 
data.iloc[0:int(len(data)*0.8)].to_csv('train.csv', sep='\t', index = False, header = False)
data.iloc[int(len(data)*0.8):int(len(data)*0.9)].to_csv('test.csv', sep='\t', index = False, header = False)
data.iloc[int(len(data)*0.9):].to_csv('dev.csv', sep='\t', index = False, header = False);

from flair.data import Corpus
from flair.datasets import CSVClassificationCorpus

data_folder = ''
column_name_map = {0: "text", 1: "labels"}

corpus: Corpus = CSVClassificationCorpus(data_folder,
                                         column_name_map,
                                         skip_header=False,
                                         delimiter='\t') 
label_dict = corpus.make_label_dictionary()
len(corpus.dev)

from flair.data import Corpus
from flair.datasets import TREC_6
from flair.embeddings import WordEmbeddings, FlairEmbeddings, DocumentRNNEmbeddings, ELMoEmbeddings, TransformerWordEmbeddings
from flair.models import TextClassifier
from flair.trainers import ModelTrainer


# 1. get the corpus
#corpus: Corpus = TREC_6()

# 2. create the label dictionary
label_dict = corpus.make_label_dictionary()

# 3. make a list of word embeddings
word_embeddings = [WordEmbeddings('glove')]
#word_embeddings = [TransformerWordEmbeddings('bert-base-uncased', layers='-1')]

# 4. initialize document embedding by passing list of word embeddings
# Can choose between many RNN types (GRU by default, to change use rnn_type parameter)
document_embeddings = DocumentRNNEmbeddings(word_embeddings, hidden_size=256)

# 5. create the text classifier
classifier = TextClassifier(document_embeddings, label_dictionary=label_dict)

# 6. initialize the text classifier trainer
trainer = ModelTrainer(classifier, corpus)

# 7. start the training
trainer.train('resources/taggers/trec',
              learning_rate=0.1,
              mini_batch_size=32,
              anneal_factor=0.5,
              patience=5,
              max_epochs=10)



# set up a sequential model for the f1 scores
model_f1 = tf.keras.Sequential()
model_f1.add(tf.keras.layers.Embedding(MAX_NB_WORDS, EMBEDDING_DIM, input_length=X.shape[1]))

model_f1.add(tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(300, return_sequences=True)))
model_f1.add(tf.keras.layers.Conv1D(250, 3, activation='relu'))
model_f1.add(tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(200, return_sequences=True)))
model_f1.add(tf.keras.layers.Conv1D(150, 3, activation='relu'))
model_f1.add(tf.keras.layers.BatchNormalization())
model_f1.add(tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(100, return_sequences=True)))
model_f1.add(tf.keras.layers.Conv1D(50, 3, activation='relu'))
model_f1.add(tf.keras.layers.GlobalMaxPooling1D())
model_f1.add(tf.keras.layers.Dropout(0.3))

model_f1.add(tf.keras.layers.Flatten())
model_f1.add(tf.keras.layers.Dense(2, activation='relu'))
# compile the model using the f1 metric
model_f1.compile(loss='binary_crossentropy', optimizer='adam', metrics=[get_f1])

# how many iterations and the size of data batches
epochs = 10
batch_size = 16

# train the model using the training data
history = model_f1.fit(X_train, 
                    Y_train, 
                    shuffle=True,
                    epochs=epochs, 
                    batch_size=batch_size,
                    validation_split=0.2,
                    callbacks=[tensorboard])

model_f1.summary()

"""**Word2Vec**"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
pd.options.mode.chained_assignment = None 
import numpy as np
import re
import nltk
nltk.download('stopwords')

from gensim.models import word2vec

from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
# %matplotlib inline

STOP_WORDS = nltk.corpus.stopwords.words()

def clean_sentence(val):
    "remove chars that are not letters or numbers, downcase, then remove stop words"
    regex = re.compile('([^\s\w]|_)+')
    sentence = regex.sub('', val).lower()
    sentence = sentence.split(" ")
    
    for word in list(sentence):
        if word in STOP_WORDS:
            sentence.remove(word)  
            
    sentence = " ".join(sentence)
    return sentence

def clean_dataframe(irony_train_df):
    "drop nans, then apply 'clean_sentence' function to question1 and 2"
    #data = data.dropna(how="any")
    
    for col in ['Tweet']:
        irony_train_df[col] = irony_train_df[col].apply(clean_sentence)
    
    return irony_train_df

irony_train_df = clean_dataframe(irony_train_df)
irony_train_df.head(5)

def build_corpus(data):
    "Creates a list of lists containing words from each sentence"
    corpus = []
    for col in ['Tweet']:
        for sentence in irony_train_df[col].iteritems():
            word_list = sentence[1].split(" ")
            corpus.append(word_list)
            
    return corpus

corpus = build_corpus(irony_train_df)        
corpus[0:2]

model = word2vec.Word2Vec(corpus, size=50, window=20, min_count=10, workers=4)
model.wv['love']

def tsne_plot(model):
    "Creates and TSNE model and plots it"
    labels = []
    tokens = []

    for word in model.wv.vocab:
        tokens.append(model[word])
        labels.append(word)
    
    tsne_model = TSNE(perplexity=40, n_components=2, init='pca', n_iter=2500, random_state=23)
    new_values = tsne_model.fit_transform(tokens)

    x = []
    y = []
    for value in new_values:
        x.append(value[0])
        y.append(value[1])
        
    plt.figure(figsize=(16, 16)) 
    for i in range(len(x)):
        plt.scatter(x[i],y[i])
        plt.annotate(labels[i],
                     xy=(x[i], y[i]),
                     xytext=(5, 2),
                     textcoords='offset points',
                     ha='right',
                     va='bottom')
    plt.show()

tsne_plot(model)

!curl https://sdk.cloud.google.com | bash

!mkdir train2017

!gsutil -m rsync gs://images.cocodataset.org/train2017 train2017