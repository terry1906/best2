import pygame
import numpy as np
import random

# Инициализация PyGame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 300, 350  # Увеличиваем высоту для кнопки рестарта
LINE_WIDTH = 5
BOARD_ROWS, BOARD_COLS = 3, 3
SQUARE_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = SQUARE_SIZE // 4

# Цвета
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)
BUTTON_COLOR = (200, 50, 50)
BUTTON_TEXT_COLOR = (255, 255, 255)

# Шрифт
font = pygame.font.Font(None, 40)

# Инициализация окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Крестики-нолики')
screen.fill(BG_COLOR)

# Игровое поле
board = np.zeros((BOARD_ROWS, BOARD_COLS))

# Q-таблица
Q_table = {}


def board_to_state(board):
    """Преобразует доску в строку: -1 -> '2', 0 -> '0', 1 -> '1'"""
    return ''.join('2' if x == -1 else '0' if x == 0 else '1' for x in board.flatten())


def get_available_actions(state):
    """Преобразует строку состояния обратно в массив и возвращает доступные действия"""
    board = np.array([int(x) if x != '2' else -1 for x in state]).reshape((BOARD_ROWS, BOARD_COLS))
    return [(row, col) for row in range(BOARD_ROWS) for col in range(BOARD_COLS) if board[row, col] == 0]


def get_Q(state, action):
    """Получает значение Q для состояния и действия"""
    return Q_table.get((state, action), 0)  # Если значения нет, возвращаем 0


def update_Q(state, action, reward, next_state, alpha=0.1, gamma=0.9):
    """Обновляет Q-значение"""
    max_next_Q = max([get_Q(next_state, a) for a in get_available_actions(next_state)], default=0)
    current_Q = get_Q(state, action)
    Q_table[(state, action)] = current_Q + alpha * (reward + gamma * max_next_Q - current_Q)


def choose_action(state, epsilon=0.2):
    """Выбирает действие на основе Q-таблицы или случайное"""
    available_actions = get_available_actions(state)
    if not available_actions:  # Если нет доступных действий
        return None

    # Попытка блокировать противника
    if random.uniform(0, 1) > epsilon:  # Агрессивная эксплуатация
        opponent = -1  # Противник
        block_move = block_opponent(board, opponent)
        if block_move:
            return block_move

    if random.uniform(0, 1) < epsilon:  # Случайное действие (exploration)
        return random.choice(available_actions)

    return max(available_actions, key=lambda a: get_Q(state, a))


def get_reward(winner, player, is_defense=False):
    """Возвращает вознаграждение, добавляемое за блокировку или победу"""
    if winner == player:
        return 1  # Победа
    elif winner == 0:
        return 0.5  # Ничья
    elif winner == -player:
        if is_defense:
            return 0.7  # Дополнительная награда за блокировку
        return -1  # Поражение
    else:
        return 0  # Игра продолжается


def train_AI(episodes=100000):
    """Обучает AI, играя множество партий"""
    for _ in range(episodes):
        board = np.zeros((BOARD_ROWS, BOARD_COLS))
        player = 1
        state = board_to_state(board)
        while True:
            action = choose_action(state)
            if action is None:  # Если действий больше нет (игра завершена)
                break
            board[action[0], action[1]] = player
            next_state = board_to_state(board)
            winner = check_winner()
            reward = get_reward(winner, player)
            update_Q(state, action, reward, next_state)
            if winner is not None:  # Если игра завершена
                break
            state = next_state
            player *= -1


# Функция для блокировки победы противника
def block_opponent(board, player):
    """Пытается заблокировать победу противника, если это возможно"""
    opponent = -player
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row, col] == 0:  # Если клетка свободна
                board[row, col] = opponent
                if check_winner() == opponent:  # Если противник может выиграть
                    board[row, col] = player  # Блокируем ход
                    return (row, col)
                board[row, col] = 0
    return None


# Графика
def draw_lines():
    for row in range(1, BOARD_ROWS):
        pygame.draw.line(screen, LINE_COLOR, (0, row * SQUARE_SIZE), (WIDTH, row * SQUARE_SIZE), LINE_WIDTH)
    for col in range(1, BOARD_COLS):
        pygame.draw.line(screen, LINE_COLOR, (col * SQUARE_SIZE, 0), (col * SQUARE_SIZE, BOARD_ROWS * SQUARE_SIZE),
                         LINE_WIDTH)


def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row, col] == 1:  # X
                pygame.draw.line(screen, CROSS_COLOR,
                                 (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE),
                                 (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                                 CROSS_WIDTH)
                pygame.draw.line(screen, CROSS_COLOR,
                                 (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                                 (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE), CROSS_WIDTH)
            elif board[row, col] == -1:  # O
                pygame.draw.circle(screen, CIRCLE_COLOR,
                                   (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2),
                                   CIRCLE_RADIUS, CIRCLE_WIDTH)


def draw_restart_button():
    pygame.draw.rect(screen, BUTTON_COLOR, (50, 310, 200, 40))
    text = font.render('Рестарт', True, BUTTON_TEXT_COLOR)
    screen.blit(text, (100, 315))


def restart_game():
    global board, player, game_over
    board = np.zeros((BOARD_ROWS, BOARD_COLS))
    player = 1
    game_over = False
    screen.fill(BG_COLOR)
    draw_lines()
    draw_restart_button()


# Победитель
def check_winner():
    for row in range(BOARD_ROWS):
        if abs(np.sum(board[row, :])) == 3:
            return board[row, 0]
    for col in range(BOARD_COLS):
        if abs(np.sum(board[:, col])) == 3:
            return board[0, col]
    if abs(np.sum(np.diag(board))) == 3:
        return board[0, 0]
    if abs(np.sum(np.diag(np.fliplr(board)))) == 3:
        return board[0, BOARD_COLS - 1]
    if is_full():
        return 0
    return None


def is_full():
    return not (board == 0).any()


def mark_square(row, col, player):
    """Ставим крестик или нолик на поле"""
    board[row, col] = player


# Основной цикл
train_AI()  # Обучение AI
draw_lines()
draw_restart_button()

player = 1
game_over = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouseX = event.pos[0]
            mouseY = event.pos[1]
            if 50 <= mouseX <= 250 and 310 <= mouseY <= 350:
                restart_game()
            if not game_over and mouseY < SQUARE_SIZE * BOARD_ROWS:
                clicked_row = mouseY // SQUARE_SIZE
                clicked_col = mouseX // SQUARE_SIZE
                if board[clicked_row, clicked_col] == 0:
                    mark_square(clicked_row, clicked_col, player)
                    winner = check_winner()
                    if winner is not None:
                        game_over = True
                        if winner == 0:
                            print("Ничья!")
                        else:
                            print(f"Победил {'Крестик' if winner == 1 else 'Нолик'}!")
                    player *= -1

        if not game_over and player == -1:  # AI ходит
            state = board_to_state(board)
            action = choose_action(state, epsilon=0.1)
            mark_square(action[0], action[1], player)
            winner = check_winner()
            if winner is not None:
                game_over = True
                if winner == -1:
                    print("Победил AI!")
                elif winner == 0:
                    print("Ничья!")
            player *= -1

        screen.fill(BG_COLOR)
        draw_lines()
        draw_figures()
        draw_restart_button()
        pygame.display.update()
