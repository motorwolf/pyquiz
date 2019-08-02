import shelve

master_quiz = shelve.open('quiz')

def digest_quiz(file):
    quizzes = {}
    current_question = ''
    current_quiz = 'quiz1'
    answer_tokens = '+-'
    quiz_counter = 1
    question_counter = 1
    quizzes[current_quiz] = list()
    for line in open(file):
        line = line.rstrip()
        if line == "END":
            quizzes[current_quiz].append(current_question)
            break
        if line[0] == '=':
            current_quiz = line[1:]
            quizzes[current_quiz] = list()
        if not line:
            continue
        if line[0] not in answer_tokens:
            if current_question:
                if len(current_question['answer']) < 1:
                    current_question['choice'] = True
                quizzes[current_quiz].append(current_question)
            current_question = {
                'question': line,
                'choice': False,
                'answer': list(),
            }
            question_counter += 1
            continue
        else:
            if line[0] == '-':
                current_question['answer'].append((line[1:], False))
            if line[0] == '+':
                current_question['answer'].append((line[1:], True))
    return quizzes

master_quiz = digest_quiz("./sample.txt")

def run_quiz():
    name_dict = {}
    for index,quiz in enumerate(master_quiz.keys(),1):
        name_dict[index] = quiz
        print(f'{index}. {quiz}')
    selected_quiz = input('Which quiz do you want to run?')
    selected_quiz = name_dict.get(selected_quiz,None)
    if not selected_quiz:
        print("Something went wrong. Try again.")
    return selected_quiz

def ask_questions(quiz):
    for question in master_quiz[quiz]:
        if question['choices']:
            handle_multiple_choice(question)
        else:
            handle_flashcard(question)

def handle_multiple_choice(q):
    answer_dict = {}
    print(q['question'])
    #TODO: randomize the answer output
    for answer,index in enumerate(q['answer'],1):
        answer_dict[index] = answer
        print(answer[0])
    your_answer = 0
    while not your_answer:
        your_answer = int(input('What is your choice?'))
        if your_answer >= len(q['answer']) or your_answer < 0:
            print("That is not a valid choice")
            your_answer = 0

def handle_flashcard(q):
    print(q['question'])
    print('Press return to reveal answer.')
    your_input = input('Ready?>>')
    print(q['answer'])
    return

print(master_quiz)

