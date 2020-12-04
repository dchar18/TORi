from training import train_nlp_model
import random
import json
import pickle
import numpy as np

import os.path
from os import path

import nltk
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import load_model

class NLP():
    lemmatizer = None
    intents = None
    words = []
    classes = []
    model = None
    
    def __init__(self) -> None:
        self.lemmatizer = WordNetLemmatizer()
        self.intents = json.loads(open('intents.json').read())
        self.words = pickle.load(open('words.pkl', 'rb'))
        self.classes = pickle.load(open('classes.pkl', 'rb'))

        # check if a model was already trained
        if path.exists('nlp_model.h5'):
            # store the model
            self.model = load_model('nlp_model.h5')
        else:
            # train model and generate a file that contains the trained model
            train_nlp_model()
            # store the model
            self.model = load_model('nlp_model.h5')

    def retrain_model(self):
        train_nlp_model()
        self.model = load_model('nlp_model.h5')

    # tokenize and lemmatize the input sentence
    def clean_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [self.lemmatizer.lemmatize(word) for word in sentence_words]
        return sentence_words

    #converts a sentence into a bag of words (1s and 0s)
    def bag_of_words(self, sentence_words):
        bag = [0] * len(self.words)
        
        for w in sentence_words:
            for i, word in enumerate(self.words):
                if word == w:
                    bag[i] = 1
        return np.array(bag)

    # predict the class that the input sentence belongs to
    def predict_class(self, sentence):
        sentence_words = self.clean_sentence(sentence)
        bag = self.bag_of_words(sentence_words)
        # run the model using the generated bag of words
        model_result = self.model.predict([bag])[0]
        # if the uncertainty if above the threshold, don't consider it
        error_threshold = 0.25
        # store the nodes that are above the error threshold
        results = [[i, r] for i,r in enumerate(model_result) if r > error_threshold]
        # sort in descending order based on the error
        results.sort(key=lambda x: x[1], reverse=True)
        # used to store the intent and the probability that the sentence belongs to that class
        return_list = []
        for r in results:
            return_list.append({'intent': self.classes[r[0]], 'probability': str(r[1])})
        return return_list

