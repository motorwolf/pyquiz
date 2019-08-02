
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
                'answer': '',
            }
            question_counter += 1
            continue
        else:
            if line[0] == '-':
                current_question['answer'] = (line[1:], False)
            if line[0] == '+':
                current_question['answer'] = (line[1:], True)
    return quizzes



print(digest_quiz("./sample.txt"))

