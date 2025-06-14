from flask import Flask, request
import random


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

    wordle_words_ranked = sorted(
        wordle_words,
        key=lambda w:(value_word(w), random.random())
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

        return wordle_words_filt[0]


def user_input(reset, new_input, new_input2):
    global items
    if reset == 1:
        items = []
    actual_list = []
    actual_list.append(new_input)
    actual_list.append(new_input2)

    items.append(actual_list)

    return wordle_solver(items)

print(wordle_solver([['testt','xxxxx']]))