import pygame
import sys

# 初始化pygame
pygame.init()
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭")
clock = pygame.time.Clock()

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 30, 30)
BLUE = (40, 120, 220)
GRAY = (180,180,180)
GREEN = (30,180,60)

# 方向常量 (dr, dc)
UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)
dir_text = {UP:"↑", DOWN:"↓", LEFT:"←", RIGHT:"→"}

# 箭头类
class Arrow:
    def __init__(self, row, col, direction):
        self.row = row
        self.col = col
        self.direction = direction
        self.alive = True
        self.shake_timer = 0

    def copy(self):
        return Arrow(self.row, self.col, self.direction)

# 路径检测：判断箭头是否可以飞出
def can_fly_out(arrow, level, rows, cols):
    dr, dc = arrow.direction
    r = arrow.row + dr
    c = arrow.col + dc
    while 0 <= r < rows and 0 <= c < cols:
        for other in level:
            if other.alive and other is not arrow and other.row == r and other.col == c:
                return False
        r += dr
        c += dc
    return True

# 关卡数据 3个基础关卡，人工验证可通关
levels = [
    # 关卡1
    [Arrow(0,0,RIGHT), Arrow(1,2,UP), Arrow(2,4,DOWN)],
    # 关卡2
    [Arrow(0,1,DOWN), Arrow(1,3,LEFT), Arrow(3,0,RIGHT)],
    # 关卡3
    [Arrow(0,0,RIGHT), Arrow(1,1,DOWN), Arrow(2,3,UP), Arrow(3,2,LEFT)]
]

# 游戏状态
STATE_START = 0
STATE_GAME = 1
STATE_WIN = 2
STATE_LOSE = 3
game_state = STATE_START
current_level_idx = 0
max_mistake = 3
mistake_count = 0
cell_size = 120
board_rows = 4
board_cols = 5
current_level = []

def reset_level():
    global current_level, mistake_count
    mistake_count = 0
    current_level = [obj.copy() for obj in levels[current_level_idx]]

reset_level()

# 绘制开始界面
def draw_start():
    screen.fill(WHITE)
    font = pygame.font.SysFont("simhei",48)
    title = font.render("一箭又一箭",True,BLACK)
    tip = font.render("点击开始游戏",True,BLUE)
    screen.blit(title,(WIDTH//2 - 120,200))
    pygame.draw.rect(screen,GRAY,(280,400,240,80))
    screen.blit(tip,(300,415))

# 绘制游戏界面
def draw_game():
    screen.fill(WHITE)
    font_small = pygame.font.SysFont("simhei",24)
    font_big = pygame.font.SysFont("simhei",36)
    # 顶部文字信息
    text1 = font_small.render(f"当前关卡：{current_level_idx+1}",True,BLACK)
    alive_arrow = sum(1 for a in current_level if a.alive)
    text2 = font_small.render(f"剩余箭头：{alive_arrow}",True,BLACK)
    text3 = font_small.render(f"剩余失误次数：{max_mistake - mistake_count}",True,RED)
    screen.blit(text1,(20,10))
    screen.blit(text1,(20,10))
    screen.blit(text2,(20,40))
    screen.blit(text3,(20,70))
    # 重新开始按钮
    pygame.draw.rect(screen,GRAY,(620,20,140,60))
    btn_text = font_small.render("重新开始",True,BLACK)
    screen.blit(btn_text,(630,35))

    # 绘制棋盘网格
    offset_x, offset_y = 80, 120
    for r in range(board_rows):
        for c in range(board_cols):
            rect = pygame.Rect(offset_x + c*cell_size, offset_y + r*cell_size, cell_size-2, cell_size-2)
            pygame.draw.rect(screen,GRAY,rect,2)

    # 绘制箭头
    for arrow in current_level:
        if not arrow.alive:
            continue
        x = offset_x + arrow.col * cell_size + cell_size//2
        y = offset_y + arrow.row * cell_size + cell_size//2
        if arrow.shake_timer > 0:
            arrow.shake_timer -= 1
            color = RED
        else:
            color = BLACK
        text = font_big.render(dir_text[arrow.direction],True,color)
        screen.blit(text,(x-20,y-20))

# 通关界面
def draw_win():
    screen.fill(WHITE)
    font = pygame.font.SysFont("simhei",48)
    text = font.render("恭喜通关！",True,GREEN)
    tip = font.render("点击进入下一关",True,BLUE)
    screen.blit(text,(250,300))
    screen.blit(tip,(220,400))

# 失败界面
def draw_lose():
    screen.fill(WHITE)
    font = pygame.font.SysFont("simhei",48)
    text = font.render("游戏失败",True,RED)
    tip = font.render("点击重新开始本关",True,BLUE)
    screen.blit(text,(250,300))
    screen.blit(tip,(200,400))

# 鼠标点击逻辑
def handle_click(pos):
    global game_state, current_level_idx, mistake_count
    mx, my = pos
    if game_state == STATE_START:
        if 280<mx<520 and 400<my<480:
            game_state = STATE_GAME
            reset_level()
        return
    elif game_state == STATE_WIN:
        current_level_idx +=1
        if current_level_idx >= len(levels):
            current_level_idx = 0
        reset_level()
        game_state = STATE_GAME
        return
    elif game_state == STATE_LOSE:
        reset_level()
        game_state = STATE_GAME
        return
    elif game_state == STATE_GAME:
        # 重新开始按钮
        if 620<mx<760 and 20<my<80:
            reset_level()
            return
        offset_x, offset_y =80,120
        # 判断点击箭头
        for arrow in current_level:
            if not arrow.alive:
                continue
            ax = offset_x + arrow.col * cell_size
            ay = offset_y + arrow.row * cell_size
            if ax < mx < ax+cell_size and ay < my < ay+cell_size:
                if can_fly_out(arrow, current_level, board_rows, board_cols):
                    arrow.alive = False
                    # 判断全部清空
                    if all(not a.alive for a in current_level):
                        game_state = STATE_WIN
                else:
                    mistake_count +=1
                    arrow.shake_timer = 20
                    if mistake_count >= max_mistake:
                        game_state = STATE_LOSE

# 主循环
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            handle_click(pygame.mouse.get_pos())
    if game_state == STATE_START:
        draw_start()
    elif game_state == STATE_GAME:
        draw_game()
    elif game_state == STATE_WIN:
        draw_win()
    elif game_state == STATE_LOSE:
        draw_lose()
    pygame.display.flip()
    clock.tick(60)
