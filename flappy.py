'''
Flappy bird game using Python Neat module
'''

import neat, os, pygame, random, pickle

#window
W_WIDTH = 400
W_Height = 700
WIN = pygame.display.set_mode((W_WIDTH, W_Height))
pygame.display.set_caption("flappy.ai")

#font
pygame.font.init()
GameFont = pygame.font.SysFont('comicsans', round(W_Height/100*5))

#load images
bg = pygame.transform.smoothscale(pygame.image.load(os.path.join('sprites', 'bg.png')).convert_alpha(), (W_WIDTH, W_Height))
birdimg = [pygame.transform.smoothscale(pygame.image.load(os.path.join('sprites', 'bird' + str(x) + '.png')).convert_alpha(), (60, 60)) for x in range(1,6)]
pipe = pygame.transform.smoothscale(pygame.image.load(os.path.join('sprites', 'pipe.png')).convert_alpha(), (round(W_WIDTH/4), round(W_Height/1.5)))
ground = pygame.transform.smoothscale(pygame.image.load(os.path.join('sprites', 'ground.png')).convert_alpha(), (W_WIDTH, round(W_Height/5)))
grass = pygame.transform.smoothscale(pygame.image.load(os.path.join('sprites', 'grass.png')).convert_alpha(), (W_WIDTH, round(W_Height/5)))
treesimg = pygame.transform.smoothscale(pygame.image.load(os.path.join('sprites', 'trees.png')).convert_alpha(), (W_WIDTH, round(W_Height/5)))
clouds = [pygame.transform.smoothscale(pygame.image.load(os.path.join('sprites', 'cloud' + str(x) + '.png')).convert_alpha(), (W_WIDTH, W_Height)) for x in range(0,3)]

gen = 0
floor = W_Height-100

class Bird :
    UP_TILT = 25
    DOWN_TILT = 20
    ANIM_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y =y
        self.img = birdimg[0]
        self.tilt = 0
        self.vel = 0
        self.tick_count = 0
        self.img_count = 0
        self.height = self.y

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        # calculate displacement
        d = (self.vel * self.tick_count) + (0.5 * 3 * self.tick_count ** 2)

        # terminal velocity
        if d >= 16 :
            d = 16
        if d < 0 :
            d -= 2

        self.y += d

        # tilt bird
        if d < 0 or self.height + 50 > self.y :
            if self.tilt < self.UP_TILT :
                self.tilt = self.UP_TILT
        else:
            if self.tilt > -90:
                self.tilt -= self.DOWN_TILT

    def get_mask(self):
        # returns an 2d array representing the mask for the bird
        return pygame.mask.from_surface(self.img)

    def draw(self, win):

        # bird animation
        self.img_count += 1
        if self.img_count <= self.ANIM_TIME :
            self.img = birdimg[0]
        elif self.img_count <= self.ANIM_TIME*4 :
            self.img = birdimg[1]
        elif self.img_count <= self.ANIM_TIME*6 :
            self.img = birdimg[2]
        elif self.img_count <= self.ANIM_TIME*8 :
            self.img = birdimg[3]
        elif self.img_count <= self.ANIM_TIME*10 :
            self.img = birdimg[4]
            self.img_count = 0

        if self.tilt <= -80 :
            self.img = birdimg[1]
            self.img_count = self.ANIM_TIME * 4

        blit_rotate(win, self.img, (self.x, self.y), self.tilt)

class Pipe :
    VEL = 5
    TOP_PIPE = pygame.transform.flip(pipe, False, True)
    BOTTOM_PIPE = pipe
    WIDTH = TOP_PIPE.get_width()
    HEIGHT = TOP_PIPE.get_height()
    GAP = 200

    def __init__(self, x):

        # initialize pipe object
        self.x = x
        self.random = random.randrange(50, round(W_Height/2))
        self.top = self.random - self.HEIGHT
        self.bottom = self.random + self.GAP
        self.passed = False

    def move(self):
        self.x -= self.VEL

    def draw(self, win):

        # draw pipe
        win.blit(self.TOP_PIPE, (self.x, self.top))
        win.blit(self.BOTTOM_PIPE, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.TOP_PIPE)
        bottom_mask = pygame.mask.from_surface(self.BOTTOM_PIPE)
        top_offset = ((self.x - bird.x), (self.top - round(bird.y)))
        bottom_offset = ((self.x - bird.x), (self.bottom - round(bird.y)))

        #find points of collision
        t_point = bird_mask.overlap(top_mask, top_offset)
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)

        #check for collision
        if t_point or b_point :
            return True

        return False

class Ground :
    VEL = 6
    IMG = ground
    WIDTH = IMG.get_width()

    def __init__(self, y) :

        #initialize ground object
        self.x1 = 0
        self.x2 = self.WIDTH
        self.y = y

    def move(self) :
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        #move ground for scroll effect
        if self.x1 + self.WIDTH < 0 :
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win) :

        #draw ground
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

class Grass :
    VEL = 5
    IMG = grass
    WIDTH = IMG.get_width()

    def __init__(self, y) :

        #initialize grass object
        self.x1 = 0
        self.x2 = self.WIDTH
        self.y = y

    def move(self) :
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        #move grass for scroll effect
        if self.x1 + self.WIDTH < 0 :
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win) :

        #draw grass
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

class Trees :
    VEL = 5
    IMG = treesimg
    WIDTH = IMG.get_width()

    def __init__(self, y) :

        #initialize trees object
        self.x1 = 0
        self.x2 = self.WIDTH
        self.y = y

    def move(self) :
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        #move trees for scroll effect
        if self.x1 + self.WIDTH < 0 :
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win) :

        #draw trees
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

class Cloud0 :
    VEL = 2
    IMG = clouds[0]
    WIDTH = IMG.get_width()

    def __init__(self) :

        #initialize cloud0 object
        self.x1 = 0
        self.x2 = self.WIDTH
        self.y = 0

    def move(self) :
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        #move cloud0 for scroll effect
        if self.x1 + self.WIDTH < 0 :
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win) :

        #draw cloud0
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

class Cloud1 :
    VEL = 3
    IMG = clouds[1]
    WIDTH = IMG.get_width()

    def __init__(self) :

        #initialize cloud1 object
        self.x1 = 0
        self.x2 = self.WIDTH
        self.y = 0

    def move(self) :
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        #move cloud1 for scroll effect
        if self.x1 + self.WIDTH < 0 :
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win) :

        #draw cloud1
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

class Cloud2 :
    VEL = 2
    IMG = clouds[2]
    WIDTH = IMG.get_width()

    def __init__(self) :

        #initialize cloud2 object
        self.x1 = 0
        self.x2 = self.WIDTH
        self.y = 0

    def move(self) :
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        #move cloud2 for scroll effect
        if self.x1 + self.WIDTH < 0 :
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win) :

        #draw cloud2
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def blit_rotate(win, img, topleft, tilt) :
    rotated_img = pygame.transform.rotate(img, tilt)
    new_rect = rotated_img.get_rect(center = img.get_rect(topleft = topleft).center)
    win.blit(rotated_img, new_rect.topleft)

def draw_window(win, birds, ground, grass, trees,cloud0, cloud1, cloud2, pipes, score, gen) :
    alive = 0
    win.blit(bg, (0, 0))
    cloud0.draw(win)
    cloud1.draw(win)
    cloud2.draw(win)
    trees.draw(win)
    grass.draw(win)

    for bird in birds :
        if os.path.isfile('./model'): #draw only one bird if model is present
            bird.draw(win)
            alive += 1
            break
        else :
            bird.draw(win)
            alive += 1

    for pipe in pipes :
        pipe.draw(win)
    ground.draw(win)

    # labels
    score_label = GameFont.render("Score : " + str(score), 1, (255, 50, 0))
    gen_label = GameFont.render("Gen : " + str(gen), 1, (72, 250, 174))
    alive_label = GameFont.render("Alive : " + str(alive), 1, (72, 255, 174))
    win.blit(score_label, (W_WIDTH - score_label.get_width() - 15, 10))
    win.blit(gen_label, (10, 10))
    win.blit(alive_label, (10, 50))

    pygame.display.update()

def eval_genome(genomes, config) :
    global WIN, gen, floor
    win = WIN
    gen += 1
    nets = []
    ge = []
    birds = []

    for genome_id, genome in genomes :
        genome.fitness = 0 # start genome with fitness level of 0
        if os.path.isfile('./model') : #load neural network from model if present
            with open('model', 'rb') as f :
                net = pickle.load(f)
        else :
            net = neat.nn.FeedForwardNetwork.create(genome, config)  # create neural network for each genome
        nets.append(net)
        ge.append(genome)
        birds.append(Bird(round(W_WIDTH/3), round(W_Height/2.5)))

    cloud0 = Cloud0()
    cloud1 = Cloud1()
    cloud2 = Cloud2()
    trees = Trees(floor - 140)
    grass = Grass(floor - 50)
    ground = Ground(floor)
    pipes = [Pipe(W_WIDTH)]
    score = 0
    running = True

    #initialize clock
    clock = pygame.time.Clock()

    while running and len(birds) > 0 :

        #game framerate
        clock.tick(30)

        # quit pygame if clicked on [X]
        for event in pygame.event.get() :
            if event.type == pygame.QUIT :
                running = False
                pygame.quit()
                quit()
                break

        pipe_index = 0
        rem = []
        add_pipe = False

        if len(birds) > 0 and len(pipes) >= 1 and birds[0].x > ( pipes[0].x + pipes[0].WIDTH) :
            pipe_index = 1

        for x, bird in enumerate(birds) :

            # give each bird a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1
            bird.move()
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_index].top) , abs(bird.y - pipes[pipe_index].bottom)))

            #check the output of the neural network
            if output[0] > 0.5 :
                bird.jump()

        cloud0.move()
        cloud1.move()
        cloud2.move()
        trees.move()
        grass.move()
        ground.move()

        for pipe in pipes :
            pipe.move()

            # check for collision
            for x, bird in enumerate(birds) :
                if pipe.collide(bird) :
                    ge[x].fitness -= 1
                    nets.pop(x)
                    ge.pop(x)
                    birds.pop(x)

                # check if bird has passed the pipe
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            #check if pipe has crossed the window
            if (pipe.x + pipe.WIDTH) < 0 :
                rem.append(pipe)

        #add new pipes
        if add_pipe :
            score += 1
            for genome in ge :
                genome.fitness += 5
            pipes.append(Pipe(W_WIDTH+50))

        #remove pipes from the rem list
        for pipe in rem :
            pipes.remove(pipe)

        #remove bird if it hits the ceiling or the floor
        for x, bird in enumerate(birds) :
            if (bird.y + bird.img.get_height()) + 10 >= floor or bird.y < 0 :
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        draw_window(win, birds, ground, grass, trees,cloud0, cloud1, cloud2, pipes, score, gen)

        #break if target score is achieved
        if score >= 50 :
            pickle.dump(nets[0], open('model', 'wb'))
            break

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # generate the population
    people = neat.Population(config)

    # print stats on terminal
    people.add_reporter(neat.StdOutReporter(True))
    people.add_reporter(neat.StatisticsReporter())

    # run for atmost 50 generations
    best = people.run(eval_genome, 50)

    print("Best Genome is : \n"+str(best))

if __name__ == '__main__' :

    #find config path
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
