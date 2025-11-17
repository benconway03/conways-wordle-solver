from flask import Flask, request, render_template
import random
import os

def wordle_solver(answer_list=[]):

    letter_frequency = {
        "E": 10.037,
        "S": 9.854,
        "A": 9.597,
        "O": 7.017,
        "R": 6.347,
        "I": 5.898,
        "L": 5.089,
        "T": 4.991,
        "N": 4.683,
        "U": 3.941,
        "D": 3.682,
        "P": 3.28,
        "M": 3.25,
        "Y": 3.231,
        "C": 3.024,
        "H": 2.683,
        "G": 2.51,
        "B": 2.489,
        "K": 2.36,
        "F": 1.669,
        "W": 1.517,
        "V": 1.078,
        "Z": 0.677,
        "J": 0.46,
        "X": 0.439,
        "Q": 0.195,
    }

    def value_word2(word):
        word = word.upper()
        word_score = 0
        if len(word) != 5:
            raise ValueError("Word must be exactly 5 letters long")
        else:
            for letter in word:
                word_score += letter_frequency[letter]
        return word_score

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

    wordle_words_ranked = sorted(
        wordle_words,
        key=lambda w: (value_word(w), -value_word2(w), random.random())
    )

    if answer_list != [['', '']]:
        answer_list = [item for item in answer_list if item != ['', '']]

    if answer_list == [['', '']]:
        return wordle_words_ranked[0]
    
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
        
        wordle_words_filt = [w for w in wordle_words_ranked if match_knowl_logic(w) == 1]
        if len(wordle_words_filt) != 0:
            return wordle_words_filt[0]
        else:
            return "You've made an error"


def user_input(reset, word, result):
    global items
    if reset == 1:
        items = []
    try:
        items
    except NameError:
        items = []
    actual_list = []
    word_lower=word.lower()
    result_lower=result.lower()
    actual_list.append(word_lower)
    actual_list.append(result_lower)

    items.append(actual_list)

    return wordle_solver(items)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    output = None
    if request.method == "POST":
        word   = request.form.get("word", "")
        result = request.form.get("result", "")
        word_strip = word.strip()
        result_strip = result.strip()
        if len(word_strip) != 5 and len(word_strip) != 0:
            output = "The word should have 5 letters"
        elif len(result_strip) != 5 and len(result_strip) != 0:
            output = "The result should have 5 letters"
        elif len(result_strip) == 5 and len(word_strip) != 5:
            output = "The word should have 5 letters"
        elif len(result_strip) != 5 and len(word_strip) == 5:
            output = "The result should have 5 letters"
        elif any(ch not in "xygXYG" for ch in result_strip):
            output = "The result should only contain x, y or g"
        elif any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" for ch in word_strip):
            output = "The word should only contain characters in the alphabet"
        else:
            output = user_input(0 if (word_strip or result_strip) else 1, word_strip, result_strip) 
    return render_template("index.html", output=output)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


    