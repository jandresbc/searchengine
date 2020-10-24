#!/usr/bin/env python
# coding: utf-8

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn import tree
from sklearn import svm
from sklearn.svm import SVR
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LinearRegression
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import confusion_matrix
import numpy as np

# to persist the model to avoid re-training
from joblib import dump, load

class modelos():

    prepositions =['a','ante','bajo','cabe','con','contra','de','desde','en','entre','hacia','hasta','para','por','según','sin','so','sobre','tras']
    prep_alike = ['durante','mediante','excepto','salvo','incluso','más','menos']
    adverbs = ['no','si','sí']
    articles = ['el','la','los','las','un','una','unos','unas','este','esta','estos','estas','aquel','aquella','aquellos','aquellas']
    aux_verbs = ['he','has','ha','hemos','habéis','han','había','habías','habíamos','habíais','habían']
    specials = ['-']
    
    retrain = False
    
    def clientsaid(self,string):
        return string.split()
    
    def train_test_split(self, train, labels, testsize = 0.25):
        X_train, X_test, y_train, y_test = train_test_split(train, labels, test_size=testsize)
        return {
            "test":{
                "X_test" : X_test,
                "y_test" : y_test
            },
            "train": {
                "X_train" : X_train,
                "y_train" : y_train
            }
            
        }
    
    def classifier(self, classifier):
        if classifier == 'tfid':
            self.classif = TfidfVectorizer(stop_words=self.prepositions+self.prep_alike+self.adverbs+self.articles+self.aux_verbs+self.specials,encoding='utf-8')
        elif classifier == 'countVectorizer':
            self.classif = CountVectorizer(stop_words=self.prepositions+self.prep_alike+self.adverbs+self.articles+self.aux_verbs+self.specials)
            
        return self.classif

    def fit(self,model,train,labels,deep=30):
        #Datos de entrenamiento del modelo
        X_train = self.classif.fit_transform(train)
        y_train = labels
        
        if self.retrain == True:
            ##Se elige el modelo de machine learning a usar.
            if model == 'kneigbors':
                #Se entrena al modelo de machine learning
                self.clf = KNeighborsClassifier(n_neighbors=150)
                self.clf.fit(X_train, y_train)
            elif model == 'tree':
                self.clf = tree.DecisionTreeClassifier(criterion='entropy', max_depth=deep)
                self.clf.fit(X_train,y_train)
            elif model == 'logistic':
                self.clf = LogisticRegression(random_state=200, solver='newton-cg',multi_class='multinomial', class_weight = "balanced")
                self.clf.fit(X_train, y_train)
                print("REENTRENAR")
            elif model == 'naive':
                self.clf = MultinomialNB()
                self.clf.fit(X_train, y_train)
            elif model == 'linear':
                self.clf = LinearRegression()
                self.clf.fit(X_train, y_train)
            elif model == 'svc':
                self.clf = svm.SVC(kernel='linear')
                self.clf.fit(X_train, y_train)
            elif model == 'svr':
                self.clf = SVR(gamma='scale', C=1.0, epsilon=0.2)
                self.clf.fit(X_train,y_train)

            ##Persist the model
            self.namemodel = model+'.joblib'
            dump(self.clf, self.namemodel)
        elif self.retrain == False:
            self.clf = load(model+'.joblib')
        
        return self.clf
    
    def predict(self,text,proba = False):
        textUser = self.classif.transform(text)
        
        if proba == False:
            self.pred = np.unique(self.clf.predict(textUser))
        elif proba == True:
            self.pred = np.unique(self.clf.predict_proba(textUser))
        return self.pred
    
    def scoreModel(self,X_test,y_test):
        X_test = self.classif.transform(X_test)
        
        resultscore = self.clf.score(X_test,y_test)
        
        return resultscore
    
    def showDataPredict(self,predictions,df,column,columnsreturn = 'no'):
        searchpredict = []
        for p in predictions:
            if columnsreturn == 'no':
                searchpredict.append(df[df[column] == p].values[0][0])
            else:
                searchpredict.append(df[df[column] == p][columnsreturn].values[0][0])
        return searchpredict
    
    def matrix_confusion(self,X_test):
        X_test = self.classif.transform(X_test)
        predict = self.clf.predict(X_test)
        self.matix = confusion_matrix(X_test,predict)
