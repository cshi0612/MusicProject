import pickle

import labels as labels
import nltk
import ssl

#try:
 # _create_unverified_https_context=ssl._create_unverified_context
#except AttributeError:
#  pass
#else:
  #ssl._create_default_https_context = _create_unverified_https_context

#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('wordnet')
import pandas as pd
# import matplotlib.pyplot as plt
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import re, collections
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import mean_squared_error, r2_score, cohen_kappa_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import AdaBoostRegressor

from nltk.tokenize import word_tokenize
import string
from sklearn.metrics import classification_report
from sklearn import svm
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report
from sklearn.preprocessing import MinMaxScaler


def avg_word_len(text):
  clean_essay =re.sub(r'\w','',text)
  words=nltk.word_tokenize(clean_essay)
  total=0
  for word in words:
    total+= len(word)
    average= total/len(words)

    return average
# words count in a given text
def word_count(text):
  clean_essay =re.sub(r'\w', '',text)
  return len(nltk.word_tokenize(clean_essay))

# char count in given text
def char_count(text):
  return len(re.sub(r'\s','', str(text).lower()))

# sentence count in a given text
def sent_count(text):
  return len(nltk.sent_tokenize(text))

# tokenization of texts to sentence
def sent_tokenize(text):
  stripped_essay=text.strip()

  tokenizer= nltk.data.load('tokenizers/punkt/english.pickle')
  raw_sentences= tokenizer.tokenize(stripped_essay)

  tokenized_sentences=[]
  for raw_sentence in raw_sentences:
    if len(raw_sentence)>0:
      clean_sentence= re.sub("[^a-zA-Z0-9]","", raw_sentence)
      tokens=nltk.word_tokenize(clean_sentence)
      tokenized_sentences.append(tokens)
  return tokenized_sentences

# lemma,
def count_lemmas(text):
  noun_count=0
  adj_count=0
  verb_count=0
  adv_count=0

  lemmas=[]
  lemmatizer=WordNetLemmatizer()
  tokenized_sentences=sent_tokenize(text)

  for sentence in tokenized_sentences:
    tagged_tokens= nltk.pos_tag(sentence)

    for token_tuple in tagged_tokens:
      pos_tag=token_tuple[1]

      if pos_tag.startswith('N'):
        noun_count+=1
        pos = wordnet.NOUN
        lemmas.append(lemmatizer.lemmatize(token_tuple[0],pos))
      elif pos_tag.startswith('J'):
        adj_count+=1
        pos = wordnet.ADJ
        lemmas.append(lemmatizer.lemmatize(token_tuple[0],pos))
      elif pos_tag.startswith('V'):
        verb_count+=1
        pos = wordnet.VERB
        lemmas.append(lemmatizer.lemmatize(token_tuple[0],pos))
      elif pos_tag.startswith('R'):
        adv_count+=1
        pos = wordnet.ADV
        lemmas.append(lemmatizer.lemmatize(token_tuple[0],pos))
      else :
        pos = wordnet.NOUN
        lemmas.append(lemmatizer.lemmatize(token_tuple[0],pos))


    lemma_count= len(set(lemmas))

    return noun_count, adj_count, verb_count, adv_count, lemma_count


def create_features(texts):
  data=pd.DataFrame(columns=(
    'Average_Word_length', 'Sentence_Count','Word_Count',
    'Character_Count', 'Noun_Count','Adjective_Count',
    'Verb_Count','Adverb_Count', 'Lemma_Count'
    ))

  data['Average_Word_length']=texts.apply(avg_word_len)
  data['Sentence_Count']=texts.apply(sent_count)
  data['Word_Count']=texts.apply(word_count)
  data['Character_Count']= texts.apply(char_count)
  temp= texts.apply(count_lemmas)
  noun_count,adj_count,verb_count, adverb_count, lemma_count=zip(*temp)
  data['Noun_Count']=noun_count
  data['Adjective_Count']=adj_count
  data['Verb_Count']=verb_count
  data['Adverb_Count']=adverb_count
  data['Lemma_Count']=lemma_count

  return data

def load_model(filename):
    with open(filename, 'rb') as f:
      model = pickle.load(f)
    return model


def prediction(context):
  mydata = {'essay': [context]}
  df_context = pd.DataFrame(data=mydata)

  df_context = create_features(df_context['essay'])
  clf = load_model('grade_writing.sav')
  labels = ['bad', 'average', 'good']
  first_column_name = df_context.columns[0]
  pred = clf.predict(df_context)

  print(pred, labels[pred[0]])

  return labels[pred[0]]  # Corrected here


df_context = "I am writing the sentence and it is very bad. "
print(prediction(df_context))
