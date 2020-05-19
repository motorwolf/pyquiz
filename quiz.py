import shelve
import time, random
import urwid


# I am not using this yet
palette = [
    ('titlebar', 'dark blue', ''),
    ('header', 'white,bold', ''),
    ('correct ', 'dark green,bold', ''),
    ('wrong', 'dark red,bold', ''),
    ('reversed', 'standout', ''),
    ]


def digest_quiz(file):
    """ This takes a quiz file and digests it into a quizzable format! A line prefixed by '=' indicates a new quiz. Any line following without a symbol will be treated as a new question, and lines that follow the new question will be treated as multiple choice, with correct answers indicated by + and wrong ones indicated by -. """ 
    
    quizzes = {}
    current_question = False
    current_quiz = ''
    answer_tokens = '+-='
    for line in open(file):
        line = line.rstrip()
        if not line:
            if current_question:
                quizzes[current_quiz]['questions'].append(current_question)
                current_question = False
            continue
        if line[0] == '=':
            if current_question:
                quizzes[current_quiz].append(current_question)
            current_quiz = line[1:]
            quizzes[current_quiz] = {
                "questions": [],
            }
        if line[0] not in answer_tokens:
            if current_question:
                # handler for multi-line questions
                current_question['question_text'] += f"\n {line}"
            else:
                current_question = {
                    'question_text': line,
                    'answers': [],
                }
        else:
            if line[0] == '-':
                current_question['answers'].append((False, line[1:]))
            if line[0] == '+':
                current_question['answers'].append((True, line[1:]))
    
    if current_question: 
        quizzes[current_quiz]['questions'].append(current_question)
    return quizzes


class Quiz:
    def __init__(self, title, questions):
        self.question_results = {
            'correct': [],
            'incorrect': [],
            }
        self.questions = questions[:]
        self.title = title
        self.current_screen = urwid.Filler(urwid.Text(self.title))
        main.original_widget = self.current_screen
        self.handle_multiple_choice(questions.pop(0))

    def check_answer(self, button, choice, answer, question):
        # I'm not sure why these args are this way.
        correct, your_answer = question
        header_text = "You selected: " + your_answer
        if correct:
            result = "CORRECT"
            self.question_results['correct'] = choice
        else:
            result = "WRONG"
            self.question_results['incorrect'] = choice
        ok_button = urwid.Button('OK')
        urwid.connect_signal(ok_button, 'click', self.ask_question)
        self.current_screen = main.original_widget = urwid.Filler(urwid.Pile([urwid.Text(header_text), urwid.Text(result),
            urwid.AttrMap(ok_button, None, focus_map='reversed')]))
        # how can we keep them on this 'page' until we confirm?

    def ask_question(self, button):
        """ Determines whether there are questions left and if so, asks them, removing them from the unasked questions in turn, and determines whether the question is multiple choice or not """
        if self.questions:
            self.handle_multiple_choice(self.questions.pop(0))
        else:
            exit_program()

    def handle_multiple_choice(self, q):
        body = [urwid.Text(q['question_text']), urwid.Divider()]
        winning_answer = ''
        random.shuffle(q['answers'])
        for answer in q['answers']:
            button = urwid.Button(answer[1])
            urwid.connect_signal(button, 'click', self.check_answer, answer, None, user_args=[answer, q])
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))
        main.original_widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))


    def handle_flashcard(self, q):
        """ Depricated. Please fix me soon """
        print(f"\n{q['question_text']}")
        your_input = input('\nPress any key to reveal answer. >>\n')
        print(f"{q['answers'][0][1]}")
        assess = input('Mark Correct? >> ').lower()
        if assess == '' or assess == 'y':
            print("\n=========CORRECT\n")
            return (True, q)
        else:
            print("\n=========OOPS\n")
            return (False, q)

    def run_quiz(self, button, choice):
        questions = master_quiz[choice]['questions'][:]
        ask_question()

def menu(title, choices, action):
    body = [urwid.Text(title), urwid.Divider()]
    for c in choices:
        button = urwid.Button(c)
        urwid.connect_signal(button, 'click', action, c)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def exit_program():
    raise urwid.ExitMainLoop()

def create_quiz(button, choice):
    global master_quiz
    master_quiz = Quiz(choice, all_quizzes[choice]['questions'])

# to be implemented someday. Would be nice to have historical data here
# master_quiz = shelve.open('quiz')

all_quizzes = digest_quiz("./quizzes/sample.txt")
quiz_menu = menu('Select your quiz', all_quizzes.keys(), create_quiz)
master_quiz = ''
main = urwid.Padding(quiz_menu, left=2, right=2)
top = urwid.Overlay(main, urwid.SolidFill(u'\N{MEDIUM SHADE}'),
    align='center', width=('relative', 60),
    valign='middle', height=('relative', 60),
    min_width=20, min_height=9)
urwid.MainLoop(top, palette=palette).run()


