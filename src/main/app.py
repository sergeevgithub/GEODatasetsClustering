from flask import Flask, request, render_template
from clustering import process_pmids

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    content = file.read().decode('utf-8')
    pmids = [pmid.strip() for pmid in content.replace('\n', ',').split(',') if pmid.strip()]
    print(pmids)

    # plots = process_pmids(pmids)  # returns dictionary of plots

    # return render_template('index.html', **plots)