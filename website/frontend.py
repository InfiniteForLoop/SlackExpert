from flask import Flask, render_template, request, redirect
from flask_table import Table, Col
from wtforms import Form, StringField, SelectField
import ast
import json
import operator
import numpy as np

with open("output/key_words.json") as f:
	    key_words = json.load(f)

with open("output/user_info.json") as f:
	    user_info = json.load(f)

with open("output/word_user_score.json") as f:
	    word_user_score = json.load(f)

class searchForm(Form):
    search = StringField('')

class PeopleTable(Table):
    classes = ['table', 'table-striped']
    name = Col('Name ')
    description = Col('Role ')
    score = Col('Score ')

class People(object):
    def __init__(self, name, description, score):
        self.name = name
        self.description = description
        self.score = score

class PeopleTable2(Table):
    classes = ['table', 'table-striped']
    pid = Col('Id')
    name = Col('Name ')
    description = Col('Role ')

class People2(object):
    def __init__(self, pid, name, description):
        self.pid = pid
        self.name = name
        self.description = description

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
	search = searchForm(request.form)

	if request.method == 'POST':
		return index_results(search)

	return render_template('index.html', form=search)

@app.route('/index_results')
def index_results(search):

	message = search.data['search']
	words = message.lower().split()
        
	word_imp_dict = {}
	score_dict = {}
	word_list = []

	for word in words:
		ret = similarityRank(word)
		word = ret[0] if ret else ''
		if not word: break
		if word in word_user_score:
			word_list.append(word)
		if word in key_words:
			word_imp_dict[word] = key_words[word]
		else:
			word_imp_dict[word] = 0

	for word in word_list:
	    for user_score in word_user_score[word]:
	    	if user_score['user_id'] in score_dict:
	    		score_dict[user_score['user_id']] += user_score['score'] * word_imp_dict[word]
	    	else:
	    		score_dict[user_score['user_id']] = user_score['score'] * word_imp_dict[word]

	sorted_id = sorted(score_dict, key=score_dict.get, reverse=True)
	peep = []

	for id in sorted_id[0:5]:
		# peep.append(People(user_info[str(id)]['name'], str(user_info[str(id)]['tag']), str(round(score_dict[id] * 10000, 2))))
		peep.append(People(user_info[str(id)]['name'], ','.join(user_info[str(id)]['tag']), str(round(score_dict[id] * 10000, 2))))

	print(peep)
	peeptab = PeopleTable(peep, no_items='There is nothing')

	return render_template('index_results.html', people=peeptab)
@app.route('/people', methods=['GET', 'POST'])
def people():
	search = searchForm(request.form)

	if request.method == 'POST':
		return people_results(search)

	return render_template('people.html', form=search)

@app.route('/people_results')
def people_results(search):

	search_string = search.data['search']

	peep = []
	for id in user_info:
		if search_string.lower() in user_info[id]['name'].lower():
			# peep.append(People2(user_info[str(id)]['name'], str(user_info[str(id)]['tag'])))
			tags = user_info[str(id)]['tag']
			tags = tags[:5] + ['...'] if len(tags) > 5 else tags
			tags = [str(tag) for tag in tags]
			peep.append(People2(str(id), user_info[str(id)]['name'], ','.join(tags)))

	peeptab = PeopleTable2(peep, no_items='There is nothing')

	return render_template('people_results.html', person=peeptab)


@app.route('/map')
def map():
	return render_template('map.html')

def fuzzyPeach(s, t, ratio_calc = False):
    rows = len(s) + 1
    cols = len(t) + 1
    distance = np.zeros((rows,cols),dtype = int)

    for i in range(1, rows):
        for k in range(1, cols):
            distance[i][0] = i
            distance[0][k] = k

    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0
            else:
                if ratio_calc == True:
                    cost = 2
                else:
                    cost = 1
            distance[row][col] = min(distance[row-1][col] + 1, distance[row][col-1] + 1, distance[row-1][col-1] + cost)

    if ratio_calc == True:
        Ratio = (float)((len(s)+len(t))-distance[row][col])/(len(s)+len(t))
        return Ratio
    else:
        return "The strings are {} edits away".format(distance[row][col])


def similarityRank(userMsg):

    if userMsg in key_words:
        return [userMsg]

    similarWords = {}
    for keyWord in key_words:
        simRatio = fuzzyPeach(userMsg, keyWord, ratio_calc = True)
        if (simRatio > 0.8):
            similarWords[keyWord] = simRatio
    sorted_words = sorted(similarWords, key=similarWords.get, reverse=True)
    return sorted_words if sorted_words else []

if __name__ == '__main__':
	app.run(debug=True)

