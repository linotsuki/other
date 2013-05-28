import pygame, sys, time
from random import randrange
from pygame.locals import *

#this was really an exercise in learning Pygame. I still have the sprites we made for the graphics as well
#as some music. Pretty easy to extend the game from here. Documentation is low but it's so straight-forward
#that it shouldn't be hard to see what it's doing. Avoid Pygame... 


pygame.init()
pygame.mixer.init()

class Ball(pygame.sprite.Sprite):

	image = None

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		if Ball.image is None:
			Ball.image = pygame.image.load('ball.png').convert()
		self.image = Ball.image
		self.image.set_colorkey((255, 255, 255))
		self.rect = self.image.get_rect()
		self.rect.topleft = (randrange(388, 407, 18), 295)
		self.gen_serve()

	def move(self):
		self.rect.left += self.x_vel
		self.rect.top += self.y_vel

	def paddle_bounce(self, coord):
		self.x_vel = -self.x_vel
		self.rect.left = coord
	
	def wall_bounce(self, coord):
		self.y_vel = -self.y_velP
		self.rect.top = coord

	def change_speed(self, speed):
		self.y_vel += speed

	def gen_serve(self):
		if self.rect.left == 388:
			self.x_vel = -2
			self.y_vel = -1.0
		else:
			self.x_vel = 2
			self.y_vel = 1.0

class Paddle(pygame.sprite.Sprite):

	def __init__(self, image, x):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(image).convert()
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, 280)
		self.state = 'still'
		self.speed = 4
		self.speed_up = 0.75

	def move(self, direction):
		if direction is 'up':
			self.rect.top -= self.speed
		else:
			self.rect.top += self.speed

	def change_state(self, change):
		self.state = change

class Court(object):

	def __init__(self):
		self.image = pygame.image.load('court.png').convert()
		self.top_rect = pygame.Rect(0, 0, 800, 8)
		self.bot_rect = pygame.Rect(0, 593, 800, 8) 
		self.players, self.p1_place, self.p2_place = [0, 0], (345, 50), (440, 50)
		self.num_size = (14, 20)
		self.nums = [pygame.image.load(str(i) + '.png') for i in range(10)]
		for i in range(10): self.nums[i].set_colorkey((0, 128, 128))

		self.w_bounce_sound = pygame.mixer.Sound('beeep.ogg')
		self.p_bounce_sound = pygame.mixer.Sound('plop.ogg')
		self.point_sound = pygame.mixer.Sound('peeeeeep.ogg')
		self.main_loop = pygame.mixer.music.load('main_loop.wav')

	def inc_score(self, player):
		self.point_sound.play()
		pygame.time.delay(1000)
		if player is 0:
			self.players[0] += 1
		else:
			self.players[1] += 1

	def reset_score(self):
		self.players = [0, 0]

class Engine(object):

	def __init__(self):
		self.screen = pygame.display.set_mode((800, 600))
		self.court = Court()
		
		self.r_paddle = Paddle('paddle_r.png', self.screen.get_width() - 16)
		self.l_paddle = Paddle('paddle_l.png', 8)
		
		self.ball = Ball()

		self.sprites = pygame.sprite.RenderUpdates(self.r_paddle, self.l_paddle, self.ball)
		self.col_list = [self.court.top_rect, self.court.bot_rect, self.l_paddle.rect, self.r_paddle.rect]

		self.frame_rate = []

		self.fps = 360
		self.fps_clock = pygame.time.Clock()

	def key_handler(self, paddle, direction):
		if paddle is 'r':
			self.r_paddle.move(direction)
			self.r_paddle.change_state(direction)
		else:
			self.l_paddle.move(direction)
			self.l_paddle.change_state(direction)
		
	def paddle_hit(self, state, coord):
		self.court.point_sound.play()
		self.ball.paddle_bounce(coord)
		if state is 'up':
			self.ball.change_speed(-self.r_paddle.speed_up)
		elif state is 'down':
			self.ball.change_speed(self.r_paddle.speed_up)

	def score_handler(self, scorer, area):
		self.sprites.remove(self.ball)
		self.ball = Ball()
		self.sprites.add(self.ball)
		self.screen.blit(self.court.image, tuple(area[:2]), tuple(area))
		self.court.inc_score(scorer)
		self.screen.blit(self.court.nums[self.court.players[scorer]], tuple(area[:2]))
		return [tuple(area)]

	def average(self, numbers):
		#used to get framerate averages
		return sum(numbers) / float(len(numbers))

	def play(self):
		
		pygame.display.set_caption('Pong by S+C')
		pygame.mixer.music.play(-1)

		self.screen.blit(self.court.image, (0, 0))
		self.sprites.draw(self.screen)
		self.screen.blit(self.court.nums[self.court.players[0]], self.court.p1_place)
		self.screen.blit(self.court.nums[self.court.players[1]], self.court.p2_place)
		done = False

		while not done:

			#t1 = time.clock()
			self.sprites.clear(self.screen, self.court.image)
			dirty_rects = []

			for e in pygame.event.get():
				if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
					done = True


			# analyze keys pressed, paddle movement logic
			keys = pygame.key.get_pressed()
			if keys[K_RIGHT]:
				if not self.r_paddle.rect.colliderect(self.court.top_rect):
					self.key_handler('r', 'up')
			elif keys[K_LEFT]:
				if not self.r_paddle.rect.colliderect(self.court.bot_rect):
					self.key_handler('r', 'down')
			else:
				self.r_paddle.change_state('still')

			if keys[K_a]:
				if not self.l_paddle.rect.colliderect(self.court.top_rect):
					self.key_handler('l', 'up')
			elif keys[K_d]:
				if not self.l_paddle.rect.colliderect(self.court.bot_rect):
					self.key_handler('l', 'down')
			else:
				self.l_paddle.change_state('still')

			# ball logic 
			if self.ball.rect.collidelist(self.col_list) != -1:
				index = self.ball.rect.collidelist(self.col_list)
				if index == 0:
					self.court.w_bounce_sound.play()
					self.ball.wall_bounce(self.court.top_rect.bottom)
				elif index == 1:
					self.court.w_bounce_sound.play()
					self.ball.wall_bounce(self.court.bot_rect.top - self.ball.rect.height)
				elif index == 2:
					self.paddle_hit(self.l_paddle.state, self.l_paddle.rect.right)
				else:
					self.paddle_hit(self.r_paddle.state, self.r_paddle.rect.left - self.ball.rect.width)

			elif self.ball.rect.right >= 800:
				dirty_rects += self.score_handler(0, [e for e in self.court.p1_place] + [e for e in self.court.num_size])

			elif self.ball.rect.left <= 0:
				dirty_rects += self.score_handler(1, [e for e in self.court.p2_place] + [e for e in self.court.num_size])

			else:
				self.ball.move()

			
			if 9 in self.court.players:
				self.court.reset_score()
			
			pygame.display.update(self.sprites.draw(self.screen) + dirty_rects)
			#t2 = time.clock()
			#print t2 - t1
			self.frame_rate += [self.fps_clock.get_fps()]
			self.fps_clock.tick(self.fps)
		print self.average(self.frame_rate)
		pygame.quit()
		sys.exit()




if __name__ == '__main__':
	the_game = Engine()
	the_game.play()