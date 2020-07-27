import shelve
import time, random
import urwid


# I am not using all of these elements yet
palette = [
    ('titlebar', 'dark blue', ''),
    ('header', 'white,bold', ''),
    ('correct', 'dark green,bold', ''),
    ('wrong', 'dark red,bold', 'black'),
    ('reversed', 'standout', ''),
    ('flashcard', 'black,bold', 'white')
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
        random.shuffle(self.questions)
        self.title = title
        self.current_screen = urwid.Filler(urwid.Text(self.title))
        main.original_widget = self.current_screen
        self.ask_question()

    def check_answer(self, button, choice, answer, question):
        # I'm not sure why these args are this way.
        correct, your_answer = question
        header_text = "You selected: " + your_answer
        body = [urwid.Text(header_text)]
        if correct:
            result = urwid.AttrMap(urwid.Text("CORRECT"), 'correct')
            self.question_results['correct'].append(choice)
            body.append(result)
        else:
            result = urwid.AttrMap(urwid.Text("WRONG"), 'wrong')
            self.question_results['incorrect'].append(choice)
            body.append(result)
            for answer in choice['answers']:
                if answer[0]:
                    body.extend([urwid.Text('The correct answer was:'),urwid.AttrMap(urwid.Text(answer[1]),'correct')])
        ok_button = urwid.Button('OK')
        urwid.connect_signal(ok_button, 'click', self.ask_question)
        body.append(style_button(ok_button))
        self.current_screen = main.original_widget = urwid.Filler(urwid.Pile(body))

    def ask_question(self, button=None):
        """ Determines whether there are questions left and if so, asks them, removing them from the unasked questions in turn, and determines whether the question is multiple choice or not """
        if self.questions:
            question = self.questions.pop(0)
            asker = self.handle_multiple_choice if len(question['answers']) > 1 else self.show_flashcard
            asker(question)
        else:
            self.end_quiz()

    def handle_multiple_choice(self, q):
        body = [urwid.Text(q['question_text']), urwid.Divider()]
        winning_answer = ''
        random.shuffle(q['answers'])
        for answer in q['answers']:
            button = urwid.Button(answer[1])
            urwid.connect_signal(button, 'click', self.check_answer, answer, None, user_args=[answer, q])
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))
        main.original_widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))


    def show_flashcard(self, q):
        body = [style_flashcard(q['question_text']), urwid.Divider(top=2)]
        reveal_button = urwid.Button('REVEAL ANSWER')
        urwid.connect_signal(reveal_button, 'click', self.reveal_flashcard, q)
        body.append(style_button(reveal_button))
        main.original_widget = urwid.Filler(urwid.Pile(body))

    def reveal_flashcard(self, button, q):
        def mark_question(button, result):
            self.question_results[result].append(q)
            self.ask_question()
        body = [style_flashcard(q['answers'][0][1]), urwid.Divider(top=2)]
        correct_button = urwid.Button('MARK CORRECT')
        wrong_button = urwid.Button('MARK WRONG')
        urwid.connect_signal(correct_button, 'click', mark_question, 'correct')
        urwid.connect_signal(wrong_button, 'click', mark_question, 'incorrect')
        body.extend([style_button(correct_button), style_button(wrong_button)])
        main.original_widget = urwid.Filler(urwid.Pile(body))
    
    def end_quiz(self):
        num_correct = len(self.question_results['correct'])
        num_incorrect = len(self.question_results['incorrect'])
        total_questions = num_correct + num_incorrect
        percent = 0 if num_correct == 0 else round(num_correct / total_questions, 2) * 100
        body = [urwid.Text(f'You got {num_correct} out of {total_questions} correct.'), urwid.Text(f'You scored {percent}%.')]
        rerun_button = urwid.Button('RERUN WRONG ANSWERS')
        exit_button = urwid.Button('EXIT')
        urwid.connect_signal(exit_button, 'click', exit_program)
        urwid.connect_signal(rerun_button, 'click', self.reset_quiz)
        body.extend([style_button(exit_button), style_button(rerun_button)])
        main.original_widget = urwid.Filler(urwid.Pile(body))

    def reset_quiz(self, button):
        self.questions = self.question_results['incorrect'][:]
        self.question_results = {
            'correct': [],
            'incorrect': [],
        }
        self.ask_question()



def style_button(button, style=None):
    return urwid.AttrMap(button, style, focus_map='reversed')

def style_flashcard(text):
    card = [urwid.Divider(), urwid.Text(text), urwid.Divider()]
    return urwid.AttrMap(urwid.Padding(urwid.Pile(card), align='center', width=('relative',60)), 'flashcard')

def menu(title, choices, action):
    body = [urwid.Text(title), urwid.Divider()]
    for c in choices:
        button = urwid.Button(c)
        urwid.connect_signal(button, 'click', action, c)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def exit_program(button=None):
    raise urwid.ExitMainLoop()

def create_quiz(button, choice):
    global master_quiz
    master_quiz = Quiz(choice, all_quizzes[choice]['questions'])


# to be implemented someday. Would be nice to have historical data here
master_quiz = shelve.open('quiz')

all_quizzes = digest_quiz("./quizzes/sample.txt")
quiz_menu = menu('Select your quiz', all_quizzes.keys(), create_quiz)
master_quiz = ''
main = urwid.Padding(quiz_menu, left=2, right=2)
top = urwid.Overlay(main, urwid.SolidFill(u'\N{MEDIUM SHADE}'),
    align='center', width=('relative', 60),
    valign='middle', height=('relative', 60),
    min_width=20, min_height=9)

### It's difficult to debug urwid sometimes; here's a handy box to send your debug output to.
# debug_box = urwid.Text('Debugger')
# debugger = urwid.Frame(main, header=debug_box)
# top = debugger


urwid.MainLoop(top, palette=palette).run()


