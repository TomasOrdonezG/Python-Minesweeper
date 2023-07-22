import random, pygame, math, time, os
from datetime import date
from pygame import mixer

pygame.init()
mixer.init()

mixer.music.load('boom.wav')
mixer.music.set_volume(1)

#create screen/canvas
cnvl = 700
cnvh = cnvl
s = 25 # min 4, max 30
MINE_DENSITY = 20 / 100
canvas = pygame.display.set_mode((cnvl, cnvh))
pygame.display.set_caption("minesweeper")

FPS = 30
FramePerSec = pygame.time.Clock()

MINE = '9'
MINE_COUNT = 0
mines = 0

DEATH_SCREEN = False

# image mode
roman = True
NUMBERS = ''
if roman:
  NUMBERS = '_r'
img_folder = 'images' + NUMBERS
score_filename = 'scores' + NUMBERS + '.txt'

# Icon
programIcon = pygame.image.load('images' + NUMBERS + '/7.png')
pygame.display.set_icon(programIcon)

start = 0
end = 0

class Number:
  def __init__(self, value, row, col):
    self.value = value
    self.row = row
    self.col = col
    self.img = 0

  def get_img(self):
    # img
    self.img = pygame.image.load(img_folder + '/' + str(self.value) + '.png')
    self.img = pygame.transform.scale(self.img, (int(cnvl / s), int(cnvl / s)))

  def get_num(self, board):
    '''Finds the correct number corresponding to the cell'''
    n_cells = []

    if self.value != MINE:
      if self.row - 1 >= 0:
        if self.col - 1 >= 0:
          n_cells.append(board[self.row - 1][self.col - 1].value)
        if self.col + 1 <= len(board) - 1:
          n_cells.append(board[self.row - 1][self.col + 1].value)
        n_cells.append(board[self.row - 1][self.col].value)

      if self.row + 1 <= len(board) - 1:
        if self.col - 1 >= 0:
          n_cells.append(board[self.row + 1][self.col - 1].value)
        if self.col + 1 <= len(board) - 1:
          n_cells.append(board[self.row + 1][self.col + 1].value)
        n_cells.append(board[self.row + 1][self.col].value)

      if self.col - 1 >= 0:
        n_cells.append(board[self.row][self.col - 1].value)
      if self.col + 1 <= len(board) - 1:
        n_cells.append(board[self.row][self.col + 1].value)

      return str(n_cells.count(MINE))
    else:
      return MINE

  def display_num(self, board):
    posx = (cnvl / len(board[0])) * self.col
    posy = (cnvh / len(board)) * self.row

    if self.img != 0:
      canvas.blit(self.img, (posx, posy))

class Cover:
  def __init__(self, row, col):
    self.state = 1
    self.row = row
    self.col = col
    self.get_img()

  def get_img(self):
    if self.state == 1:
      self.img = pygame.image.load('images/cover.png')
    elif self.state == 2:
      self.img = pygame.image.load('images/flag.png')
    elif self.state == 3:
      self.img = pygame.image.load('images/transparent.png')
    
    size = int(cnvl / s)
    self.img = pygame.transform.scale(self.img, (size, size))
    
  def display(self, board):
    posx = (cnvl / len(board[0])) * self.col
    posy = (cnvh / len(board)) * self.row

    canvas.blit(self.img, (posx, posy))

  def click(self, board):
    global playing
    if self.state == 1:
      self.state = 3
      self.get_img()
      if board[self.row][self.col].value == MINE:
        playing = False

  def flag(self):
    global MINE_COUNT
    if self.state == 1:
      self.state = 2
      MINE_COUNT -= 1
    elif self.state == 2:
      self.state = 1
      MINE_COUNT += 1
    self.get_img()

def generate_empty_board():
  '''Creates a 2D list of empty strings with a defined length and width'''
  board = []
  for y in range(s):
    board.append([])
  for row_index in range(len(board)):
    for x in range(s):
      board[row_index].append(Number('0', row_index, x))
  return board

def mine_count(board):
  x_count = 0
  for row in board:
    for cell in row:
      if cell.value == MINE:
        x_count += 1
  return x_count

def generate_mines(board, amount, clicked_position):
  '''Places mines into the board'''
  while mine_count(board) < amount:
    randx = random.randint(0, s - 1)
    randy = random.randint(0, s - 1)
    if board[randy][randx].value != MINE:
      board[randy][randx].value = MINE
    
    board[clicked_position[0]][clicked_position[1]].value = '0'
    if board[clicked_position[0]][clicked_position[1]].get_num(board) != '0':
      neighbours = find_neighbours(board, clicked_position[0], clicked_position[1])
      for cell in neighbours:
        cell.value = '0'

def generate_numbers(board):
  for y, row in enumerate(board):
    for x in range(len(row)):
      board[y][x].value = board[y][x].get_num(board)

def display_board(board):
  for number_row in board:
    for number in number_row:
      number.display_num(board)

def create_cover():
  board = []
  for y in range(s):
    board.append([])
  for row_index in range(len(board)):
    for x in range(s):
      board[row_index].append(Cover(row_index, x))
  return board

def display_cover(cover_list, board):
  for cover_list in cover_list:
    for cover in cover_list:
      cover.display(board)

def generate_images(board):
  for row in board:
    for num in row:
      num.get_img()

def find_neighbours(alist, x, y):
  '''Will return a list of the neighbouring cells of a given item in a 2D list'''
  neighbours = []
  rows = len(alist)
  cols = len(alist[0])
  for i in range(x - 1, x + 2):  # (x - 1, x, x + 1)
    for j in range(y - 1, y + 2):  # (y - 1, y, y + 1
      if i == x and j == y:
        continue  # Skip when i == x and j == y
      if i < 0 or i >= rows or j < 0 or j >= cols:
        continue  # Skip if location if outside the 2D list
      neighbours.append(alist[i][j])
  return neighbours

def sweep_area(yi, xi, board, cover_list, recurse):
  neighbours = find_neighbours(board, yi, xi)

  if board[yi][xi].value == '0':

    swept = 0
    for neighbour in neighbours:
      if cover_list[neighbour.row][neighbour.col].state == 3:
        swept += 1
    if swept == 8:
      swept = True
    else:
      swept = False

    for neighbour in neighbours:
      if cover_list[neighbour.row][neighbour.col].state == 1: 
        cover_list[neighbour.row][neighbour.col].click(board)
        if neighbour.value == '0' and not swept and recurse:
          sweep_area(neighbour.row, neighbour.col, board, cover_list, recurse)

def sweep_solved(board, yi, xi, cover_list):
  value = board[yi][xi].value
  neighbours = find_neighbours(cover_list, yi, xi)
  
  # Saves the flagged neighbours
  flagged = []
  for neighbour in neighbours:
    if neighbour.state == 2:
      flagged.append(neighbour)

  if int(value) == len(flagged) and value != '0' and cover_list[yi][xi].state == 3:
    for neighbour in neighbours:
      square_size = cnvl / s
      cell_num = board[neighbour.row][neighbour.col]
      yi = (square_size * cell_num.row) + (square_size / 2)
      xi = (square_size * cell_num.col) + (square_size / 2)

      left_click_tile(xi, yi, board, cover_list, True, False)

def left_click_tile(mousex, mousey, board, cover_list, recurse, direct_click):
  square_size = cnvl / s
  xi = math.floor(mousex / square_size)
  yi = math.floor(mousey / square_size)

  if cover_list[yi][xi].state != 2:

    # Click empty
    sweep_area(yi, xi, board, cover_list, recurse)

    # Click numbers and sweep
    if cover_list[yi][xi].state == 3 and direct_click:
      sweep_solved(board, yi, xi, cover_list)

    cover_list[yi][xi].click(board)

  return [yi, xi]

def right_click_tile(mousex, mousey, cover_list):
  square_size = cnvl / s
  xi = math.floor(mousex / square_size)
  yi = math.floor(mousey / square_size)

  cover_list[yi][xi].flag()

def update_high_score(elapsed_time):
  filename = score_filename
  with open(filename, 'r') as file:
    list_of_lines = file.readlines()
    if list_of_lines:
      last_hs = list_of_lines[-1].split(' / ') 
      last_hs = float(last_hs[0])
    else:
      last_hs = ''

  with open(filename, 'a') as file:
    today = date.today()
    d = today.strftime("%B %d, %Y")
    if not isinstance(last_hs, str):
      if last_hs > elapsed_time:
        file.write(str(elapsed_time) + ' / ' + d + '\n')
    else:
      file.write(str(elapsed_time) + ' / ' + d + '\n')

cat = pygame.image.load('silly/1.png')
def display_result(win, frames):
  global end, cat
  with open(score_filename, 'r') as file:
    lol = file.readlines()
    if lol:
      hs = lol[-1].split(' / ')
      hs = hs[0]
    else:
      hs = 'x'

  font = pygame.font.SysFont('microsoftnewtailue', 20)
  if not win:
    # lose
    if frames == 1:
      mixer.music.play()
      cat = pygame.image.load('silly/' + random.choice(os.listdir("silly")))
    cat = pygame.transform.scale(cat, (cnvl, cnvh))
    canvas.blit(cat, (0, 0))
    font = pygame.font.SysFont('microsoftnewtailue', 50)

    copy = font.render("you lose lol", 1, (100, 225, 10))
    canvas.blit(copy, (cnvl / 2 - 100, cnvh / 2 - 100))
  else:
    if frames == 1:
      end = time.time()
 
    elapsed_time = end - start
    if frames == 1:
      update_high_score(round(elapsed_time, 3))
    
    '''text'''
    copy = font.render("you win lol", 1, (100, 225, 10))
    canvas.blit(copy, (cnvl / 2, cnvh / 2))

    '''text'''
    copy = font.render(f"Time taken: {round(elapsed_time, 2)}s", 1, (100, 225, 10))
    canvas.blit(copy, (cnvl / 2, cnvh / 2 - 100))
    '''text'''
    copy = font.render(f"High score: {hs}s", 1, (100, 225, 10))
    canvas.blit(copy, (20, 20))
  
  '''text'''
  font = pygame.font.SysFont('microsoftnewtailue', 20)
  copy = font.render("click any key to play again", 1, (100, 225, 10))
  canvas.blit(copy, (cnvl / 2 - 100, cnvh / 2 + 100))

def mine_count(board):
  count = 0 
  for row in board:
    for cell in row:
      if cell.value == MINE:
        count += 1
  return count

def check_win(board, list_of_cover, mines):
  count = 0
  # count empty cells
  for row_index in range(len(board)):
    for col_index in range(len(board[row_index])):
      if board[row_index][col_index].value != MINE and list_of_cover[row_index][col_index].state == 3:
        count += 1

  if count == s ** 2 - mines:
    return True
  else: 
    return False

def display_info(pos):
  global MINE_COUNT

  with open(score_filename, 'r') as file:
    lol = file.readlines()
    if lol:
      hs = lol[-1].split(' / ')
      hs = hs[0]
    else:
      hs = 'n/a'

  font = pygame.font.SysFont('microsoftnewtailue', 20)
  x, y = pos[0], pos[1]

  # BOX
  pygame.draw.rect(canvas, (255, 255, 255), (x - 10, y - 85, 110, 95))

  end = time.time()
  time_elapsed = round(end - start, 3)
  copy = font.render(f'{time_elapsed}s', 1, (176, 11, 105))
  canvas.blit(copy, (x, y - 50))

  copy = font.render(f'{hs}s', 1, (176, 11, 105))
  canvas.blit(copy, (x, y - 25))

  copy = font.render(str(MINE_COUNT) + ' Mines', 1, (176, 11, 105))
  canvas.blit(copy, (x, y - 75))

def display_mines(cover_list, board, frames):
  display_cover(cover_list, board)
  # Display mines
  if frames == 1:
    for row in board:
      for cell in row:
        cell.display_num(board)

def main():
  global playing, keep_playing, start, MINE_COUNT, mines
  number_of_mines = s ** 2 * MINE_DENSITY
  '''get trolled lmfao loser no bitches, gets no pussy or dick L how can you not
  sorry that was very mean i love you so much you gorgeos human being. you amaze me everyday and i will write it with every language i know
  mmy love, my darling, my sweet, my honey, my baby, my sweetie, my best friend, my boyfriend, mi novio, wo de nanpengyou, mon amour, watashino kanojo tu est tellement special!
  you make me feel so safe and happy, i feel so authentic and real with you and sometimes you feel too unreal im worried you'll leave, i guess it feels you are
  the person of my dreams and i feel like im floating around you.
  love you, biaozi <3333333333333'''
  generated = False
  first_click = False
  MINE_COUNT = 0
  win = False
  frames_after_result = 0
  move_info =  False

  board = generate_empty_board()
  cover_list = create_cover()

  info_pos = (0, 0)

  running = True
  while running:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
        keep_playing = False

      if event.type == pygame.KEYDOWN and not playing:
        running = False

      if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
        running = False

      # Timer
      if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
        move_info = True
        info_pos = pygame.mouse.get_pos()

      if event.type == pygame.KEYUP and event.key == pygame.K_e:
        move_info = False

      if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
        first_click = True
        mousex, mousey = pygame.mouse.get_pos()
        if generated:
          recurse = True
        else:
          recurse = False
        clicked_position = left_click_tile(mousex, mousey, board, cover_list, recurse, True)

      if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3) or (event.type == pygame.KEYDOWN and event.key == pygame.K_w):
        mousex, mousey = pygame.mouse.get_pos()
        right_click_tile(mousex, mousey, cover_list)

    if not generated and first_click:
      generated = True
      generate_mines(board, number_of_mines, clicked_position)
      generate_numbers(board)
      generate_images(board)
      start = time.time()
      if cover_list[clicked_position[0]][clicked_position[1]].state != 2:
        for neighbour in find_neighbours(board, clicked_position[0], clicked_position[1]):
          if neighbour.value == '0':
            sweep_area(neighbour.row, neighbour.col, board, cover_list, True)
      mines = mine_count(board)
      MINE_COUNT = mine_count(board)

    # BG Colour
    canvas.fill((0, 0, 0))
    if playing:
      # Display board
      display_board(board)
      display_cover(cover_list, board)

      #counter
      if first_click and move_info:
        info_pos = pygame.mouse.get_pos()
        display_info(info_pos)

      win = check_win(board, cover_list, mines)
      if win:
        playing = False
    else:
      frames_after_result += 1
      if DEATH_SCREEN:
        display_result(win, frames_after_result)
      else:
        display_mines(cover_list, board, frames_after_result)
        running = False
    #Update display
    pygame.display.update()
    FramePerSec.tick(FPS)

keep_playing = True
if __name__ == '__main__':
  while keep_playing:
    playing = True
    main()