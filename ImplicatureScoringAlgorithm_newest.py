import pandas as pd # module used for interacting with excel datasets
import re #module used for cleaning sentences
import nltk
from nltk.corpus import wordnet #module used to get synonyms
from nltk.tokenize import word_tokenize #module used for dividing text into words
from nltk.stem.lancaster import LancasterStemmer #module used to get root of words
from nltk.corpus import stopwords
from nltk.corpus import names
import spacy

class Algorithm:

#====== Accessing the files ================#
    
    def __init__(self,results, diagnosticwords): 
        self.data= pd.read_excel(results)
        self.diagnostics= pd.read_excel(diagnosticwords)
        self.diagnostics.index=self.diagnostics['Vignettes'] #diagnostics dataset indexed by name vignettes to locate other items in the dataset
        self.st = LancasterStemmer()
        self.nlp = spacy.load('en_core_web_sm')
        self.df= pd.read_excel("survey_diagnostics.xls")

 
        
         

#====== Dividing sentences into words ======#
        
        #Some words modified for processing#
        
    def clean(self,text):
        w_rpc=["d","ll","m","ok","im","Im","Ill","can't","won't","don't","ill","'s","'re","ve","'ve","s","re"]
        r_rpc=["would",'will','am','okay','I am','I am','I will','can not','will not','do not','I will',"is","are", "have","have","is","are"]
        text=str(text).lower()
        text_new=' '
        text= re.sub(r"(@\.[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?", "", text)
        text= re.sub(r"!", "", text)
        text= re.sub(r'"', '', text)
        
        text = list(text.split(" "))

        for i in text:
            if i=='':
                text.remove(i)
                
        
        for i in range(len(text)):
            for a in range(len(w_rpc)):
                if text[i]==w_rpc[a]:
                    text[i]=r_rpc[a]

        text2=' '
        text3= text2.join(text)
        text3=text3.lower()
        doc = self.nlp(text3)                 
        text = [token.lemma_ for token in doc]       
        return text

    def remove_names(self,text):
        # Ensure nltk corpus is downloaded
        nltk.download('names', quiet=True)
        
        # Get a list of common English names
        male_names = names.words('male.txt')
        female_names = names.words('female.txt')
        all_names = male_names + female_names
        for x in all_names:
            if x.lower()==text:
                return True

    def stopwords_delete(self,text, diagnostic, tt, explicature):
        file = open("stop_words_english.txt", "r", encoding='utf-8') 
        fff = file.read() 
        stop_words =fff.split("\n")
        #set(stopwords.words('english'))
        file.close()
        
        filtered_sentence = [w for w in text if not w.lower() in stop_words]
        #with no lower case conversion
        filtered_sentence = []
         
        for w in text:
            if self.remove_names(w)!= True:
                if explicature:
                    if w in tt:
                        filtered_sentence.append(w)
                    elif w not in stop_words:
                        filtered_sentence.append(w)
                if w not in stop_words:
                    filtered_sentence.append(w)
                else:
                    if diagnostic != False:
                        #if w in diagnostic:
                            #filtered_sentence.append(w)
                        pass
        return filtered_sentence
    def stopwords_deletev2(self,text):
        file = open("stop_words_english.txt", "r", encoding='utf-8') 
        fff = file.read() 
        stop_words =fff.split("\n")
        #set(stopwords.words('english'))
        file.close()
        
        filtered_sentence = [w for w in text if not w.lower() in stop_words]
        #with no lower case conversion
        filtered_sentence = []
         
        for w in text:
            if self.remove_names(w)!= True:
                    if w not in stop_words:
                        filtered_sentence.append(w)


        return filtered_sentence

#====== Finding synonyms of given word ======#
    
    def diag(self,vignette,target):
        ACTUAL=[]
        for x in self.df[vignette]:
            target= self.clean(self.diagnostics.loc[vignette,'Target'])
            A=self.stopwords_delete(self.clean(x),diagnostic=False, tt=target, explicature=False)
            
            B=self.stopwords_delete(target,diagnostic=False, tt=target, explicature=False)
            for y in A:
                if y not in B:
                    #doc = self.nlp(y)                 
                    #lemmatized_tokens = [token.lemma_ for token in doc]
                    #for i in lemmatized_tokens:
                    ACTUAL.append(y)

        ACTUAL_unq= list(set(ACTUAL))

        return ACTUAL_unq
    
#====== Scoring the sentence ===============#

    def accuracy(self,c1,c2):


        txt=  self.clean(c1)
        txt2=self.clean(self.diagnostics.loc[c2,'Target']) #Finding the target sentence regarding the given vignette


        a=0
        b=0
        for i in txt:
            if i in txt2:
                a+=1
        for t in txt2:
            b+=1

        return a/b


    def implicature(self,i0,i1):
        a=0
        b=0
        tt=self.stopwords_deletev2(self.clean(self.diagnostics.loc[i1,'Target']))

        pa=self.stopwords_deletev2(self.clean(i0)) # participants' sentecence divided into words

        imp= self.diag(i1,tt)

        print(pa)
        for i in pa:
            if i not in tt:       
                b+=1    
                if i in imp:
                    a+=1
        if a + b == 0:
            return 0
        else:
            return (a/b)

    def explicature(self,inp,tt):
        target= self.clean(self.diagnostics.loc[tt,'Target'])
        tt=self.stopwords_delete(target,diagnostic=False, tt=target, explicature=True)#Finding the target sentence regarding the given vignette
        text_syn=self.stopwords_delete(self.clean(inp),diagnostic=False, tt=target, explicature=True)
        ts_syn=[]
        for x in text_syn:
            ts_syn.append(x) #adding target sentence's words into the list
        
        ts_syn=list(set(ts_syn))#creating set to discard repeated words in the list

        a = 0   #somme du haut
            
        b = 0   #somme du bas

        for s in tt: #pour tout s dans pa
            
            b += 1
            
            for i in ts_syn:  # si s est aussi dans inp

                if s == i:
                    
                    a += 1   #on ajoute R(s) dans la somme du haut

        if a + b == 0:
            return 0           
        return (a/b)
    
#====== Applying the algorithm to given dataset ===============#

    #>For the data wanted to be analyzed<#
        #column_name_sentences= Name of the column contains participants memory recalls
        #column_name_vignettes= Name of the vignettes contains name of the vignettes participants recalled
        #save_path= Path of the output
    
    def apply(self, column_name_sentences, column_name_vignettes, save_path):

            scores=[]
            Implicature_Score=[]
            Explicature_Score=[]
            Accuracy_Score=[]
            doc=self.data[column_name_sentences]
            for i in range(len(doc)):
                token=self.clean(doc[i])
                print('Raw----->',token)
                vignette=self.data[column_name_vignettes][i]
                print('IMPLICATURE-------')
                imp=self.implicature(doc[i],vignette)
                print('EXPLICATURE-------')
                exp=self.explicature(doc[i],vignette)
                print('ACCURACY-------')
                accu=self.accuracy(doc[i],vignette)
                print(imp,exp,accu)

                Implicature_Score.append(imp)
                Explicature_Score.append(exp)
                Accuracy_Score.append(accu)

            self.data['Explicated_Score']=Explicature_Score
            self.data['Implicated_score']=Implicature_Score
            self.data['Accuracy_score']=Accuracy_Score
            self.data.to_excel(save_path, index=False)
#====== Calling the codes to run the algorithm ===============#
            
Algorithm_run= Algorithm("CombinedOutput_DelayNoDelay.xlsx","target_and_diagnostic_words.xlsx")
        
Algorithm_run.apply("Sentence", "Vignette", "New_CombinedOutput_DelayNoDelay.xlsx")


        


