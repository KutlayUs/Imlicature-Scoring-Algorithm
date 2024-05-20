import pandas as pd # module used for interacting with excel datasets
import re #module used for cleaning sentences
import nltk
from nltk.tokenize import word_tokenize #module used for dividing text into words
from nltk.corpus import names #module used to get name corpus
import spacy #module used to get 'en_core_web_sm' corpus

class Algorithm:

#====== Accessing the files ================#
    
    def __init__(self,results, diagnosticwords): 
        self.data= pd.read_excel(results) #importing the experiment data
        self.diagnostics= pd.read_excel(diagnosticwords) #importing the diagnostics words
        self.diagnostics.index=self.diagnostics[#column name of vignettes] #diagnostics dataset indexed by name vignettes to locate other items in the dataset
        self.nlp = spacy.load('en_core_web_sm') #importing corpus for getting the root of words
        self.df= pd.read_excel("survey_diagnostics.xls") #importing the diagnostic words

#====== Dividing sentences into words ======#
        
        #Some words modified for processing#
        
    def clean(self,text):
        w_rpc=["d","ll","m","ok","im","Im","Ill","can't","won't","don't","ill","'s","'re","ve","'ve","s","re"] #special expressions participants might use
        r_rpc=["would",'will','am','okay','I am','I am','I will','can not','will not','do not','I will',"is","are", "have","have","is","are"] #correction of those expressions
        #punctuation removing 
        text=str(text).lower()
        text_new=' '
        text= re.sub(r"(@\.[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?", "", text)
        text= re.sub(r"!", "", text)
        text= re.sub(r'"', '', text)
        
        #special expression correcting and splitting the sentences into words
        
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
        
    # Deleting the names
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
    # Deleting the stopwords in diagnostic words #/ Ensure that the stopwords.txt is downloaded
    def stopwords_delete_diagnotic(self,text, diagnostic, tt, explicature):
        file = open("stop_words_english.txt", "r", encoding='utf-8') 
        fff = file.read() 
        stop_words =fff.split("\n")
        file.close()
        filtered_sentence = [w for w in text if not w.lower() in stop_words]
        #with no lowercase conversion
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
                        pass
        return filtered_sentence
        
    # Deleting the stopwords in sentences #/ Ensure that the stopwords.txt is downloaded

    def stopwords_delete_sentence(self,text):
        file = open("stop_words_english.txt", "r", encoding='utf-8') 
        fff = file.read() 
        stop_words =fff.split("\n")
        file.close()
        filtered_sentence = [w for w in text if not w.lower() in stop_words]

        filtered_sentence = []
         
        for w in text:
            if self.remove_names(w)!= True:
                    if w not in stop_words:
                        filtered_sentence.append(w)


        return filtered_sentence

#====== Checking whether the words in the sentence match with diagnostic words ======#
    
    def diag(self,vignette,target):
        ACTUAL=[]
        for x in self.df[vignette]:
            target= self.clean(self.diagnostics.loc[vignette,'Target'])
            A=self.stopwords_delete_diagnotic(self.clean(x),diagnostic=False, tt=target, explicature=False)
            
            B=self.stopwords_delete_diagnotic(target,diagnostic=False, tt=target, explicature=False)
            for y in A:
                if y not in B:
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
        tt=self.stopwords_delete_sentence(self.clean(self.diagnostics.loc[i1,'Target'])) #Finding the target sentence regarding the given vignette

        pa=self.stopwords_delete_sentence(self.clean(i0)) # participants' sentecence divided into words

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
    
#====== Applying the algorithm to given dataset ===============#

    #>For the data wanted to be analyzed<#
        #column_name_sentences= Name of the column containing participant memory recalls
        #column_name_vignettes= Name of the vignettes contains the name of the vignettes participants recalled
        #save_path= Path of the output
    
    def apply(self, column_name_sentences, column_name_vignettes, save_path):

            scores=[]
            Implicature_Score=[]
            Accuracy_Score=[]
            doc=self.data[column_name_sentences]
            for i in range(len(doc)):
                token=self.clean(doc[i])
                print('Raw----->',token)
                vignette=self.data[column_name_vignettes][i]
                print('IMPLICATURE-------')
                imp=self.implicature(doc[i],vignette)
                print('ACCURACY-------')
                accu=self.accuracy(doc[i],vignette)
                print(imp,exp,accu)

                Implicature_Score.append(imp)
                Accuracy_Score.append(accu)

            self.data['Implicature_score']=Implicature_Score
            self.data['Accuracy_score']=Accuracy_Score
            self.data.to_excel(save_path, index=False)
        
#====== Calling the codes to run the algorithm ===============#
            
Algorithm_run= Algorithm(#path of Excel data, #target and diagnostic words)
        
Algorithm_run.apply( #column_name_sentences,  #column_name_vignettes, #save_path)

    #>For the data wanted to be analyzed<#
        #column_name_sentences= Name of the column containing participant memory recalls
        #column_name_vignettes= Name of the vignettes contains the name of the vignettes participants recalled
        #save_path= Path of the output
        


