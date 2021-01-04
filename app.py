from flask import Flask,render_template,request
import requests,nltk,pandas,re
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

app = Flask(__name__)

def text_from_url(url):  # extracting text from url
    obj = requests.get(url)
    text = obj.text
    soup = BeautifulSoup(text)
    paragraph = soup.find_all("p")
    paratext = ''
    for para in paragraph:
        paratext += para.text
    return paratext

def top_sentences(url): # return top sentences
    required_text = text_from_url(url)
    stopword = stopwords.words('english') # assigning stopwords
    sentences  = nltk.sent_tokenize(required_text) #tokeninzing text in sentences
    words = nltk.word_tokenize(required_text)# tokenizing text into words
    frequency = {} # dict for word frquency count
    for word in words:
        if word not in stopword:
            if word not in frequency:
                frequency[word] = 1
            else:
                frequency[word] += 1
    max_frequency = max(frequency.values())
    for key in frequency.keys(): # weighted weights 
        frequency[key] /= max_frequency
    
    sentence_score = []
    for sentence in sentences:
        curr_words = nltk.word_tokenize(sentence)
        curr_score = 0
        for word in curr_words:
            if word in frequency:
                curr_score += frequency[word]
        sentence_score.append(curr_score)

    sentence_data  = pandas.DataFrame({"sent":sentences,"score":sentence_score})
    data_sorted = sentence_data.sort_values(by = "score",ascending = False).reset_index()
    summary = data_sorted.iloc[0:11,:]

    reult = "  ".join(list(summary['sent']))
    return re.sub("[\(\[].*?[\)\]]", "", reult) #return the top sentences after removing text in betweeen square brackets



@app.route("/", methods = ['POST','GET'])
def index():
    if request.method == 'POST':
        url = request.form.get("url")
        result = top_sentences(url)
        # content_of_url = text_from_url(url)
        # return content_of_url
        return result
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)