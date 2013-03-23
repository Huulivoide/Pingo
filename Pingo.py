#!/usr/bin/python3
"""
Copyright (c) 2013, Jesse Jaara <jesse.jaara@gmail.com>
All rights reserved.

Redistribution and use in source and binary forms,
with or without modification, are permitted provided
that the following conditions are met:

* Redistributions of source code must retain the
above copyright notice, this list of conditions
and the following disclaimer.
* Redistributions in binary form must reproduce
the above copyright notice, this list of conditions
and the following disclaimer in the documentation
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS
AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
OF SUCH DAMAGE.
"""

##Error codes
#5: too small screen.

import random
import math
import time
import sys
import platform  # Needed to detect if we are running on OSX
import curses
from curses import panel

# We need a workaround for OSX, which doesn't like set_curs() function.
if platform.system() == 'Darwin':
    def show_cursor(value):
        return True
else:
    def show_cursor(value):
        curses.curs_set(value)

min_width = 54  # Determinated by header banner
min_height = 20

card_header = {
    9: 'P I N G O',
    16: '  P I N G O  ',
    25: 'P   I   N   G   O',
    36: '  P   I   N   G   O  ',
    49: '    P   I   N   G   O    '
}


class card:
    def __init__(self, size, level, y, x):
        self.size = size
        self.level = level
        self.numbers = []
        self.y = y
        self.x = x
        self.dimension = int(math.sqrt(self.size))

    def fill(self):
        rints = [i for i in                         # As in random ints
            range(1, int(self.size + ((self.size / 4) * self.level)))]
        random.shuffle(rints)
        for row in range(0, self.dimension):
            self.numbers.append([])
            for column in range(0, self.dimension):
                self.numbers[row].append(rints[(row*self.dimension+column)])

    def draw(self, wnumbers):
        for row in range(0, self.dimension):
            if row == 0:
                cwin.move(self.y, self.x)
                cwin.addstr('|' + ('----' * self.dimension)[:-1] + '|')
                cwin.move(cwin.getyx()[0] + 1, self.x)
                cwin.addstr('| ')
                cwin.attron(curses.A_BLINK)
                cwin.attron(curses.color_pair(1))
                cwin.addstr(card_header[self.size])
                cwin.refresh()
                cwin.attroff(curses.A_BLINK)
                cwin.attroff(curses.color_pair(1))
                cwin.addstr(' |')
                cwin.move(cwin.getyx()[0] + 1, self.x)
            cwin.addstr('|---' * self.dimension + '|')
            cwin.move(cwin.getyx()[0] + 1, self.x)
            for col in range(0, self.dimension):
                if self.numbers[row][col] in wnumbers:
                    color = 2       # Magenta on black
                else:
                    color = 3       # Green on black
                if self.numbers[row][col] >= 10:
                    cwin.addstr('| ')
                    cwin.attron(curses.color_pair(color))
                    cwin.addstr(str(self.numbers[row][col]))
                    cwin.attroff(curses.color_pair(color))
                else:
                    cwin.addstr('| ')
                    cwin.attron(curses.color_pair(color))
                    cwin.addstr(str(self.numbers[row][col]))
                    cwin.attroff(curses.color_pair(color))
                    cwin.addstr(' ')
            cwin.addstr('|')
            cwin.move(cwin.getyx()[0] + 1, self.x)
        cwin.addstr('|---' * self.dimension + '|')

    def check(self, wnumbers):
        vert = 0
        horz = 0
        topbot = 0

        for row in range(0, self.dimension):
            if set(self.numbers[row]).issubset(set(wnumbers)):
                horz += 1

        for col in range(0, self.dimension):
            column = []
            for row in self.numbers:
                column.append(row[col])
            if set(column).issubset(set(wnumbers)):
                vert += 1

        tb_array = []
        for i in range(0, self.dimension):
            tb_array.append(self.numbers[i][i])
        if set(tb_array).issubset(set(wnumbers)):
            topbot += 1

        tb_array = []
        for i in range(0, self.dimension):
            tb_array.append(self.numbers[self.dimension - 1 - i][i])
        if set(tb_array).issubset(set(wnumbers)):
            topbot += 1

        return (vert, horz, topbot)    # Number of vertical, horizontal and top
                                       # to bottom/left to right (MAX 2) bingos


def get_answer():
    mwin.move(mwin.getyx()[0] + 2, 1)
    mwin.addstr('q: quit', curses.color_pair(1))
    curses.echo()
    mwin.move(mwin.getyx()[0] + 1, 1)
    mwin.addstr(':> ')
    show_cursor(1)
    answer = mwin.getstr()
    show_cursor(0)
    curses.noecho()
    if str(answer, 'UTF-8') == 'q':
        curses.endwin()
        exit(0)
    else:
        return answer


def menu_size():
    mwin.erase()        # Make sure the screen is clean
    mwin.border()
    mwin.move(1, 1)
    mwin.addstr('Choose card size:')
    for size in card_sizes:
        mwin.move(mwin.getyx()[0] + 1, 1)
        if size == 25:
            mwin.addstr(
                '   %d:\t%dx%d *' % (size, math.sqrt(size), math.sqrt(size)))
        else:
            mwin.addstr(
                '   %d:\t%dx%d' % (size, math.sqrt(size), math.sqrt(size)))
    answer = get_answer()
    try:
        int(answer)
    except ValueError:
        return (menu_size())
    if not int(answer) in card_sizes:
        return(menu_size())
    else:
        return float(answer)


def menu_level(size):
    max_level = 1
    while int(size + ((size / 4) * (max_level + 1))) < 100:
        max_level += 1
    mwin.erase()        # Make sure the screen is clean
    mwin.border()
    mwin.move(1, 1)
    mwin.addstr('Choose game level:')
    mwin.move(mwin.getyx()[0] + 1, 1)
    mwin.addstr('MIN:\t1')
    mwin.move(mwin.getyx()[0] + 1, 1)
    mwin.addstr('MAX:\t%d' % max_level)
    answer = get_answer()
    try:
        int(answer)
    except ValueError:
        return(menu_level(size))
    if not int(answer) in range(1, max_level + 1):
        return(menu_level(size))
    else:
        return float(answer)


def menu_cards(size):
    yc = 0  # How many fits to the Y-axis
    xc = 0  # How many fits to the X-axis
    card_cordinates = []  # List of card's starting points

    y_size = int(math.sqrt(size) * 2) + 4
    x_size = int(math.sqrt(size) * 4) + 2

    while True:         # Determinate how many fits to the Y-axis
        if (cwin.getmaxyx()[0] - 2) - (yc * y_size) >= y_size:
            yc += 1
        else:
            break

    while True:         # Determinate how many fits to the X-axis
        if (cwin.getmaxyx()[1] - 2) - (xc * x_size) >= x_size:
            xc += 1
        else:
            break
    count = yc * xc

    mwin.erase()        # Make sure the screen is clean
    mwin.border()
    mwin.move(1, 1)
    mwin.addstr('How many cards: ')
    mwin.move(mwin.getyx()[0] + 1, 1)
    mwin.addstr('MIN: 1')
    mwin.move(mwin.getyx()[0] + 1, 1)
    mwin.addstr('MAX: %d' % count)
    answer = get_answer()
    try:
        int(answer)
    except ValueError:
        return(menu_cards(size))
    if not int(answer) in range(1, count + 1):
        return(menu_cards(size))
    else:
        i = 0
        _x = 0
        y = 1
        while i < int(answer):
            while _x < xc and i < int(answer):
                card_cordinates.append([int(y), int((_x * x_size) + 1)])
                i += 1
                _x += 1
            _x = 0
            y += int(y_size)
        return(card_cordinates)


def draw_scores(win, results):       # Touple of 3
    win.erase()
    win.border()
    win.move(1, 1)
    win.addstr('Your scores:', curses.color_pair(1))
    win.move(win.getyx()[0] + 2, 1)
    win.addstr("'|' bingos: ", curses.color_pair(3))
    win.move(win.getyx()[0] + 1, 1)
    win.addstr("'-' bingos: ", curses.color_pair(3))
    win.move(win.getyx()[0] + 1, 1)
    win.addstr("'/' bingos: ", curses.color_pair(3))
    win.move(win.getyx()[0] - 2, 13)
    win.addstr(str(results[0]), curses.color_pair(2))
    win.move(win.getyx()[0] + 1, 13)
    win.addstr(str(results[1]), curses.color_pair(2))
    win.move(win.getyx()[0] + 1, 13)
    win.addstr(str(results[2]), curses.color_pair(2))
    win.refresh()


def display_scores(results):
    rpan.top()
    rpan.move(int((HEIGHT - 9) / 2), int((WIDTH - 30) / 2))
    rpan.show()
    draw_scores(rwin, results)
    rwin.move(rwin.getyx()[0] + 1, 1)
    rwin.addstr('n: new game | q: quit', curses.color_pair(1))
    rwin.move(rwin.getyx()[0] + 1, 1)
    curses.echo()
    rwin.addstr(':> ')
    curses.noecho()
    rwin.refresh()
    show_cursor(1)
    answer = rwin.getstr()
    if str(answer, 'UTF-8') == 'q':
        curses.endwin()
        exit(0)
    elif str(answer, 'UTF-8') == 'n':
        rpan.hide()
        run_game()
    else:
        return(display_scores(results))


def new_game():
    size = menu_size()
    level = menu_level(size)
    cards = menu_cards(size)
    return (size, level, cards)


def init_header():
    hwin.erase()
    hwin.border()
    hwin.move(1, 1)
    hwin.addstr(' ' * int((WIDTH - 53) / 2))
    hwin.addstr('Welcome to play ')
    hwin.attron(curses.A_BLINK)
    hwin.attron(curses.color_pair(1))
    hwin.addstr(card_header[9])
    hwin.attroff(curses.A_BLINK)
    hwin.attroff(curses.color_pair(1))
    hwin.addstr(' where luck is all you need')
    hwin.move(3, 1)
    hwin.addstr("Today's lucky numbers are: ")
    hwin.refresh()


def results(cards, numbers):      # cards = array of cards
    x = 0
    y = 0
    z = 0
    for card in cards:
        _y, _x, _z = card.check(numbers)
        y += _y
        x += _x
        z += _z
    return (y, x, z)


def run_game():
    cwin.erase()
    cwin.border()
    cwin.refresh()
    init_header()
    size, level, cards = new_game()

    myCards = []
    for yx in cards:
        new_card = card(size, level, yx[0], yx[1])
        new_card.fill()
        myCards.append(new_card)

    wnumbers = [i for i in range(1, int(size + ((size / 4) * level)))]
    random.shuffle(wnumbers)

    i = 0
    drawn = []
    position = []
    line_buffer = ''
    while i < myCards[0].size:
        drawn.append(wnumbers[i])

        if hwin.getyx()[0] == 4 and hwin.getyx()[1] > (WIDTH - 5):
            hwin.move(3, 28)
            hwin.addstr(' ' * (WIDTH - 30))   # Clean the 1st wnumber row
            hwin.move(3, 28)
            hwin.addstr(line_buffer)          # write the buffer back on line 1
            line_buffer = ''
            hwin.move(4, 28)
            hwin.addstr(' ' * (WIDTH - 30))   # Clean the 2nd wnumber row
            hwin.move(4, 28)

        if hwin.getyx()[1] > (WIDTH - 5):
            hwin.move(4, 28)

        if hwin.getyx()[0] == 4:
            if hwin.getyx()[1] == 28:
                line_buffer += str(wnumbers[i])
            else:
                line_buffer += (', ' + str(wnumbers[i]))

        if hwin.getyx()[1] == 28:
            hwin.addstr(str(wnumbers[i]))
        else:
            hwin.addstr(', ' + str(wnumbers[i]))

        i += 1
        position = hwin.getyx()
        hwin.move(4, 1)
        hwin.attron(curses.color_pair(1))
        hwin.addstr('[%d/%d]' % (i, size))
        hwin.attroff(curses.color_pair(1))
        draw_scores(mwin, results(myCards, drawn))
        hwin.move(position[0], position[1])
        hwin.refresh()
        for myCard in myCards:
            myCard.draw(drawn)
        cwin.refresh()
        time.sleep(1)
    display_scores(results(myCards, drawn))


def __main__(screen):
    global hwin, cwin, mwin, HEIGHT, WIDTH, card_sizes, rwin, rpan
    HEIGHT, WIDTH = screen.getmaxyx()
    if HEIGHT < min_height or WIDTH < min_width:
        curses.endwin()
        sys.stderr.write(
            'Your terminal is too small to run this application.\n' +
            'If you are on a unix console (not in X11 terminal application,)' +
            'you could try to see if there is smaller consolefont awaiable ' +
            'and use setfont command to use it.\n')
        exit(5)             # Too small screen

    hwin = screen.subwin(6, WIDTH, 0, 0)          # Header and winning numbers
    cwin = screen.subwin(HEIGHT - 6, WIDTH - 21, 6, 0)  # Players cards
    mwin = screen.subwin(14, 21, 6, WIDTH - 21)         # Menu and results

    rwin = screen.subwin(9, 30, 0, 0)   # Panel showing results and asking for
    rpan = panel.new_panel(rwin)        # if user want a new game

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    card_sizes = []
    for size in (3, 4, 5, 6, 7):
        if (((size * 2) + 5) <= cwin.getmaxyx()[0] and
                ((size * 3) + 3) <= cwin.getmaxyx()[1]):
            card_sizes.append(size ** 2)

    run_game()


curses.wrapper(__main__)
