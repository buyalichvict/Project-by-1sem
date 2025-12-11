import pygame
import sys
import random
import math

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [
    (204, 0, 0),  # Красный
    (0, 153, 51),  # Зеленый
    (51, 51, 255),  # Синий
    (255, 200, 0),  # Желтый
    (204, 51, 255),  # Фиолетовый
]

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Лягушка")
clock = pygame.time.Clock()

background = pygame.image.load('jungle-1.jpg').convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Загрузка изображений
def load_images():
    frog_img = pygame.image.load('frog-5.png').convert_alpha()
    frog_img = pygame.transform.rotate(frog_img, 270)

    ball_imgs = []
    for color in COLORS:
        ball = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(ball, color, (15, 15), 15)
        ball_imgs.append(ball)

    return frog_img, ball_imgs


frog_img, ball_imgs = load_images()


class PathBall:
    def __init__(self, color_index, progress=0):
        self.color_index = color_index
        self.radius = 15
        self.progress = progress  # Прогресс по пути (0-1)
        self.speed = 0.0005  # Скорость движения по пути
        self.x = 0
        self.y = 0

    def update(self):
        # Двигаем шар вперед по пути
        self.progress += self.speed

        # Если шар дошел до конца пути, игра заканчивается
        if self.progress >= 1:
            return True  # Сигнал о конце игры
        return False

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        screen.blit(ball_imgs[self.color_index], (self.x - self.radius, self.y - self.radius))


class ShotBall:
    def __init__(self, x, y, color_index, angle):
        self.x = x
        self.y = y
        self.color_index = color_index
        self.radius = 15
        self.speed = 10
        self.angle = angle
        self.active = True

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # Проверяем, не улетел ли шар за экран
        if (self.x < -50 or self.x > WIDTH + 50 or
                self.y < -50 or self.y > HEIGHT + 50):
            self.active = False

    def draw(self):
        screen.blit(ball_imgs[self.color_index], (self.x - self.radius, self.y - self.radius))

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)


class Frog:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.next_ball_color = random.randint(0, len(COLORS) - 1)

    def update(self, mouse_pos):
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        self.angle = math.atan2(dy, dx)

    def draw(self):
        rotated_frog = pygame.transform.rotate(frog_img, -math.degrees(self.angle))
        rect = rotated_frog.get_rect(center=(self.x, self.y))
        screen.blit(rotated_frog, rect)
        screen.blit(ball_imgs[self.next_ball_color], (self.x + 30, self.y - 15))

    def shoot(self):
        ball = ShotBall(self.x, self.y, self.next_ball_color, self.angle)
        self.next_ball_color = random.randint(0, len(COLORS) - 1)
        return ball


class Path:
    def __init__(self):
        # траектория
        self.points = [
            (50, 200),
            (150, 100),
            (250, 100),
            (350, 200),
            (450, 150),
            (550, 250),
            (650, 200),
            (750, 300)
        ]
        self.total_length = self.calculate_total_length()

    def calculate_total_length(self):
         # Вычисляем общую длину пути
        total = 0
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            total += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return total

    def draw(self):
        # Рисуем путь
        for i in range(len(self.points) - 1):
            pygame.draw.line(screen, (80, 80, 120), self.points[i], self.points[i + 1], 4)

    def get_position(self, progress):

        if progress <= 0:
            return self.points[0]
        if progress >= 1:
            return self.points[-1]

        # Вычисляем пройденное расстояние
        target_distance = progress * self.total_length
        distance = 0

        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            segment_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            if distance + segment_length >= target_distance:
                # Находим нужный сегмент
                segment_progress = (target_distance - distance) / segment_length
                x = x1 + (x2 - x1) * segment_progress
                y = y1 + (y2 - y1) * segment_progress
                return (x, y)

            distance += segment_length

        return self.points[-1]


class Game:


    def __init__(self):
        self.frog = Frog(WIDTH // 2, HEIGHT - 50)
        self.path = Path()
        self.path_balls = []  # Шары на пути
        self.shot_balls = []  # Выстреленные шары
        self.score = 0
        self.game_over = False
        self.font = pygame.font.SysFont(None, 40)
        self.small_font = pygame.font.SysFont(None, 24)
        self.text_color = (0, 0, 0)
        self.result = ""
        # Создаем начальную цепочку шаров
        self.create_initial_balls()

    def create_initial_balls(self):
        # Создаем начальную цепочку шаров на пути
        num_balls = 13
        spacing = 0.07  # Расстояние между шарами

        for i in range(num_balls):
            progress = i * spacing / 2
            color_index = random.randint(0, len(COLORS) - 1)
            ball = PathBall(color_index, progress)
            x, y = self.path.get_position(progress)
            ball.set_position(x, y)
            self.path_balls.append(ball)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                if event.button == 1:  # Левая кнопка мыши
                    self.shot_balls.append(self.frog.shoot())
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q and self.game_over:
                    # Перезапуск игры
                    self.__init__()



    def check_collision(self, ball1, ball2):
        # Проверяем столкновение двух шаров
        dx = ball1.x - ball2.x
        dy = ball1.y - ball2.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < ball1.radius + ball2.radius

    def insert_ball_into_chain(self, index, shot_ball):
        # Вставляем выстреленный шар в цепочку
        # Создаем новый шар для пути
        new_path_ball = PathBall(shot_ball.color_index, self.path_balls[index].progress)

        # Вставляем шар в цепочку
        self.path_balls.insert(index + 1, new_path_ball)

        # Сдвигаем все последующие шары вперед
        spacing = 0.05
        for i in range(index + 1, len(self.path_balls)):
            self.path_balls[i].progress += spacing

    def check_all_matches(self):
        # Проверяем все совпадения в цепочке
        i = 0
        while i < len(self.path_balls):
            color = self.path_balls[i].color_index
            matches = [i]

            # Проверяем совпадения слева
            j = i - 1
            while j >= 0 and self.path_balls[j].color_index == color:
                matches.append(j)
                j -= 1

            # Проверяем совпадения справа
            j = i + 1
            while j < len(self.path_balls) and self.path_balls[j].color_index == color:
                matches.append(j)
                j += 1

            # Если найдены 3 или более совпадения, удаляем их
            if len(matches) >= 3:
                # Увеличиваем счет
                self.score += len(matches) * 10

                # Удаляем шары
                for idx in sorted(matches, reverse=True):
                    self.path_balls.pop(idx)

                # После удаления продолжаем с начала цепочки
                i = 0
            else:
                i += 1

        if len(self.path_balls) == 0:
            self.result = "Победа!"
            self.text_color = (0, 204, 255)
            self.game_over = True

    def update(self):
        if self.game_over:
            return

        # Обновляем позицию лягушки
        mouse_pos = pygame.mouse.get_pos()
        self.frog.update(mouse_pos)

        # Обновляем выстреленные шары
        for ball in self.shot_balls[:]:
            ball.move()

            # Проверяем столкновение с шарами на пути
            for i, path_ball in enumerate(self.path_balls):
                if self.check_collision(ball, path_ball):
                    # Вставляем шар в цепочку
                    self.insert_ball_into_chain(i, ball)
                    self.shot_balls.remove(ball)
                    break

            # Удаляем неактивные шары
            if not ball.active:
                self.shot_balls.remove(ball)

        # Обновляем шары на пути
        for ball in self.path_balls:
            # Обновляем позицию на основе прогресса
            x, y = self.path.get_position(ball.progress)
            ball.set_position(x, y)

            # Проверяем, дошел ли шар до конца
            if ball.update():
                self.result = "Фиаско!"
                self.text_color = (255, 102, 0)
                self.game_over = True

        # Проверяем совпадения после всех обновлений
        self.check_all_matches()

    def draw(self):



        # Очищаем экран
        screen.fill((20, 20, 40))
        screen.blit(background, (0, 0))
        # Рисуем путь
        self.path.draw()

        # Рисуем шары на пути
        for ball in self.path_balls:
            ball.draw()

        # Рисуем выстреленные шары
        for ball in self.shot_balls:
            ball.draw()

        # Рисуем лягушку
        self.frog.draw()

        # Рисуем счет
        score_text = self.font.render(f"Счет: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Рисуем количество шаров на пути
        balls_count = self.small_font.render(f"Шаров на пути: {len(self.path_balls)}", True, (200, 200, 200))
        screen.blit(balls_count, (10, 50))

        # Если игра окончена, выводим сообщение
        if self.game_over:
            game_over_text = self.font.render(self.result, True, self.text_color)
            restart_text = self.small_font.render("Нажмите Q для перезапуска", True, WHITE)

            screen.blit(game_over_text,
                        (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(restart_text,
                        (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))


# Создаем и запускаем игру
game = Game()

# Главный игровой цикл
while True:
    game.handle_events()
    game.update()
    game.draw()

    pygame.display.flip()
    clock.tick(FPS)