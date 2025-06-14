from flask import Flask, request
import pandas as pd
import IPython.display as ipd
import numpy as np


def wordle_solver(answer_list=[]):

    def value_word(word):
        word = word.lower()
        word_score = 0
        if len(word) != 5:
            raise ValueError("Word must be exactly 5 letters long")
        else:
            word_lst = list(word)
            for i in range(5):
                for j in range(i + 1, 5):
                    if word_lst[i] == word_lst[j]:
                        word_score += 1
        return word_score

    knowledge=['','','','','']
    maybes=[]
    faults=[]
    exact_yellows=[[],[],[],[],[]]

    with open("valid-wordle-words.txt", "r") as f:
        wordle_words = f.readlines()
        wordle_words = [line.strip() for line in wordle_words]

    wordle_words_df = pd.DataFrame(wordle_words, columns=['word'])

    wordle_words_df['value'] = wordle_words_df['word'].apply(value_word)

    wordle_words_rand = wordle_words_df.sample(frac=1).reset_index(drop=True)

    wordle_words_sort = wordle_words_rand.sort_values(by='value', ascending=True)

    if answer_list != [['', '']]:
        answer_list = [item for item in answer_list if item != ['', '']]

    if answer_list == [['', '']]:
        return wordle_words_sort['word'].iloc[0]
    
    else:

        for j in range (len(answer_list)):
            result_str=answer_list[j][1]
            word = answer_list[j][0]
            result = list(result_str)
            word_lst=list(word)
            for i in range(5):
                if result[i] == 'g':
                    knowledge[i] = word_lst[i]
                elif result[i] == 'y':
                    if word_lst[i] not in maybes:
                        maybes.append(word_lst[i])
                    exact_yellows[i].append(word_lst[i])
                elif result[i] == 'x' and word_lst[i] not in knowledge and word_lst[i] not in maybes:
                    faults.append(word_lst[i])
        
        for knowls in knowledge:
            maybes = [char for char in maybes if char != knowls]

        def match_knowl_logic(row):
            row_lst = list(row)
            good=1
            maybe_bad=0
            
            for k in range (5):
                if row_lst[k] != knowledge[k] and knowledge[k] != '':
                    good = 0
                if row_lst[k] in faults and row_lst[k] not in knowledge:
                    good = 0
                if row_lst[k] in exact_yellows[k]:
                    good = 0
                if knowledge[k] == '' and row_lst[k] not in faults and row_lst[k] in maybes:
                    maybe_bad+=1
            if maybe_bad != len(maybes) and len(maybes) != 0:
                good=0
            return good
        
        wordle_words_sort['outcome_g']=wordle_words_sort['word'].apply(match_knowl_logic)
        # print(maybes)
        # print(knowledge)
        # print(faults)
        # print(exact_yellows)
        # display(wordle_words_sort)
        wordle_words_filt1 = wordle_words_sort[wordle_words_sort['outcome_g']==1]
        return wordle_words_filt1['word'].iloc[0]


def user_input(reset, new_input, new_input2):
    global items
    if reset == 1:
        items = []
    actual_list = []
    actual_list.append(new_input)
    actual_list.append(new_input2)

    items.append(actual_list)

    return wordle_solver(items)

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    output = ""
    if request.method == "POST":
        word = request.form.get("word")
        result = request.form.get("result")
        if word == '' and result == '':
            output = user_input(1, word, result)
        else:
            output = user_input(0, word, result)

    return f"""
        <form method="post">
            Enter a word: <input type="text" name="word">
            Enter a result: <input type="text" name="result">
            <input type="submit" value="Submit">
        </form>
        <div style="margin-top:20px; padding:10px; border:1px solid #000;">
            <strong>Output:</strong> {output}
        </div>
    """

if __name__ == "__main__":
    app.run(debug=True)



    