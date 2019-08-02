
def digest_quiz(file):
    quizzes = {}
    for line in open(file):
        current_quiz = ''
        current_question = ''
        answer_tokens = '+-'
        quiz_counter = 1
        question_counter = 1
        if line[0] == '=':
            current_quiz = line[1:]
        else:
            current_quiz = f'quiz_{quiz_counter}'
            counter += 1        
        quizzes[current_quiz] = list()
        if not line:
            continue
        if line[0] not in answer_tokens:
            current_question = {
                'question': line,
                'choice': False,
            }
            quizzes[current_quiz].append({
                multiple_choice: False,
                answers: list()
            )
            question_counter += 1
            continue
        else:
            if line[0] == '-':
                quizzes[current_quiz][]



digest_quiz("./sample.txt")
