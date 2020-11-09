import os
from flask import Flask, render_template, request, redirect, url_for
import stripe
import requests 
from bs4 import BeautifulSoup
from googlesearch import search
import json
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz, process
import re
import sys
from google.cloud import automl_v1beta1
from google.cloud.automl_v1beta1.proto import service_pb2
from newspaper import Article
import nltk

credential_path = ""
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

nltk.download('punkt')

app = Flask(__name__)

text = ''

def get_prediction(content, project_id, model_id):
  prediction_client = automl_v1beta1.PredictionServiceClient()

  name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
  payload = {'text_snippet': {'content': content, 'mime_type': 'text/plain' }}
  params = {}
  request = prediction_client.predict(name, payload, params)
  return request

def predict(line):
	#if __name__ == '__main__':
  		content = line
  		project_id = "test-yeet-111"
  		model_id = "TCN6320210674505053725"
  		return (get_prediction(content, project_id,  model_id))

def refine(term):
    term = term.replace('http://', '')
    term = term.replace('https://', '')
    term = term.replace('www.', '')
    term = term.replace('-', ' ')
    term = term.replace('.html', '')
    first = term.find('/')
    term = term[first:]
    term = term.replace ('/', ' ')
    return term

def match(link, original, term, name):
    count = 0
    for result in search(term, tld='com', lang='en', num=3, start=0, stop=3, pause=3.0):
        result = refine(result)
        print(name + ": " + result)
        print(compare(original, result))
        if(compare(original, result) > 65):
            print("true")
            count += 1
        else:
            print("false")
        print("prelim count: " + str(count))
    return count
        
def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()
    
def compare(a, b):
    return fuzz.token_set_ratio(a, b)

def getHeadline(url):
    r = requests.get(url)
    soup  = BeautifulSoup(r.content, 'html5lib')
    h1 = soup.body.find('h1')
    h1 = str(h1)
    
    c = 0
    c = int(c)
    h = h1.replace('</h1>', '')
    while(c < len(h) or h[c] != '>'):
        if(h[c] == '>'):
            h = h[c + 1:]
            break
        c += 1
    
    print(h)

def runner(original):
	att = refine(original)
	print(att)
	query = att
	n1 = 'cnn'
	n2 = 'washington post'
	n3 = 'new york times'
	n4 = 'wall street journal'
	name1 = 'CNN'
	name2 = 'WP'
	name3 = 'NYT'
	name4 = 'WSJ'
	go1 = query + n1
	go2 = query + n2
	go3 = query + n3
	go4 = query + n4
	a = match(original, att, go1, name1)
	b = match(original, att, go2, name2)
	c = match(original, att, go3, name3)
	d = match(original, att, go4, name4)
	total = a + b + c + d
	return total

@app.route('/')
def home():
    return render_template('ha.html')

@app.route('/', methods=['POST'])
def form():
	text = request.form['text']
	text = text.lower()
	setText(text)
	art = Article(text, language="en")
	art.download()
	art.parse()
	art.nlp()
	print("Text: " + art.text)
	js = str(predict(art.text))
	print(type(js))
	print(js)
	#score = js.split(" ")
	score1 = js[js.index("score:"):js.index("\"") + 6]
	score2 = js[js.rfind("score:"):js.rfind("\"") + 6]
	print("S1:     " + score1 + "END")
	print("S2:     " + score2 + "END")
	score1 = score1.replace("\"", "")
	score1 = score1.replace("\n", "")
	score1 = score1.replace("}", "")
	print(score1 + "DONE")
	dir1 = score1[-5:]
	dir1 = dir1.replace(" ", "")
	print(dir1 + "END")
	score2 = score2.replace("\"", "")
	score2 = score2.replace("\n", "")
	score2 = score2.replace("}", "")
	print(score2 + "DONE")
	dir2 = score2[-5:]
	dir2 = dir2.replace(" ", "")
	print(dir2 + "END")
	7 - 22
	score1 = score1[7:22]
	score2 = score2[7:22]
	print(score1 + "," + score2)
	score1 = float(score1)
	score2 = float(score2)
	dictt = {dir1 : score1, dir2 : score2}
	print(dictt)

# 	payload {
#   classification {
#     score: 0.7518262267112732
#   }
#   display_name: "left"
# }
# payload {
#   classification {
#     score: 0.26866796612739563
#   }
#   display_name: "right"
# }
	#refinedJSON = convertJSON(json)
	print("Prediction: " + js)
	print("Count: " + str(runner(text)))
	return render_template('res.html')

@app.route('/results', methods=['GET', 'POST'])
def res():
	return render_template('res.html')

def setText(t):
	text = t
	print(text)

if __name__ == '__main__':
    app.run(debug=True)
