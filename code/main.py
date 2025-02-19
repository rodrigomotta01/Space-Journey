import pygame
from os.path import join
import random
import time
import math

#region Initialize
pygame.mixer.init()
pygame.init()

W_WIDTH, W_HEIGHT = 1920, 1080
screen = pygame.display.set_mode((W_WIDTH, W_HEIGHT))
pygame.display.set_caption("Space Journey")
clock = pygame.time.Clock()
game_started = 0
score = 0
score_display = 0
hearts_list = []
init_lifecounter = 2
life_counter = init_lifecounter
running = False
dt = 0
#endregion

#Classes
class Player(pygame.sprite.Sprite):
    
    def __init__(self, groups): #groups stand for groups of sprites
        super().__init__(groups)
        self.image = pygame.image.load(join("images", "player.png")).convert_alpha() #use .convert() or .convert_alpha() to make the performance better when importing images # image or surface
        self.rect = self.image.get_frect(center = (W_WIDTH / 2, W_HEIGHT / 2)) # not player.surf because it changed to self.image (class)
        self.direction = pygame.Vector2()
        self.speed = 500
        self.hit = False

        # cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400 #milissecs

        # mask 
        self.mask = pygame.mask.from_surface(self.image)

        # animation
        self.animation_time = 150
        self.originalimage = self.image
        self.animation_timer = 0

        #boost
        self.boost = AnimatedBoost(boost_frames, (self.rect.centerx, self.rect.bottom), all_sprites)

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration: #check if the time now minus the last time the
                self.can_shoot = True   #laser was used is equal/greater than the cooldown, so it can be used in the interval

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction =  self.direction.normalize() if self.direction else self.direction # do [else] keep (dont change)
        if player.rect.right >= W_WIDTH: 
            self.direction.x = min(self.direction.x, 0)  # Stop moving right
        elif player.rect.left <= 0:
            self.direction.x = max(self.direction.x, 0)  # Stop moving left
        if player.rect.bottom >= W_HEIGHT: 
            self.direction.y = min(self.direction.y, 0)  # Stop moving bottom
        elif player.rect.top <= 0:
            self.direction.y = max(self.direction.y, 0)  # Stop moving top
        
        #player pos update
        self.rect.center += self.direction * self.speed * dt
        
        #boost pos update
        self.boost.rect.center = (self.rect.centerx, self.rect.bottom + 15)

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot: #only executed when laser is used (once in a cooldown)
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks() #time since started
            laser_sound.play()
        
        self.laser_timer()

        if pygame.time.get_ticks() - self.animation_timer >= self.animation_time:
            self.image = self.originalimage

    def damage_mask(self):
        
        #damage mask
        mask = self.mask
        mask_surf = mask.to_surface()
        mask_surf.set_colorkey((0,0,0))
        self.image = mask_surf
        self.hit = True
        self.animation_timer = pygame.time.get_ticks()

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self. image = surf
        self.rect  = self.image.get_frect(midbottom = pos) #generate above the player

    def update(self, dt):
        self.rect.centery -= 500 * dt
        if self.rect.bottom < 0:
            self.kill() #delete the sprite after it surpasses the screen

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 5000
        self.direction = pygame.Vector2(random.uniform(-0.5, 0.5),1)
        self.speed = random.randint(600, 700)
        self.rotation_speed = random.randint(40,80)
        self.rotation = 0

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center) # corrects the strange movement resizing the rects

class AnimatedExplosion(pygame.sprite.Sprite): #animation
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
    
    def update(self, dt):
        self.frame_index += 30 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

class AnimatedBackground(pygame.sprite.Sprite): #animation
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(topleft = pos)
    
    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.frame_index = 0

class AnimatedBoost(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)

    def update(self,dt):
        self.frame_index += 30 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.frame_index = 0

class Hearts(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect()
    
class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, image, hoverimage, groups):
        super().__init__(groups)
        self.width = image.get_width()
        self.height = image.get_height()
        self.image = image
        self.origimage = image
        self.hoverimage = hoverimage
        self.rect = self.image.get_rect(center = (x,y))
        self.clicked = False
        
    def update(self, dt = None):
        action = False
        pos = pygame.mouse.get_pos()

        #check collision (hover)
        if self.rect.collidepoint(pos):
            
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

            self.image = self.origimage 
        if self.rect.collidepoint(pos):
            self.image = self.hoverimage
        
        return action

def collisions(life_counter):
    global game_started, score
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask) # overlap
    if collision_sprites:
        player.damage_mask()
        life_counter -= 1
        if hearts_list:
            hearts_list[-1].kill()
            hearts_list.pop()
            player_hit.play()

    if life_counter == 0:
        game_music.stop()
        game_over_effect.play()
        game_started = 2

    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()
            score += 25

    return life_counter

def display_score():
    global score, score_display
    time_score = (pygame.time.get_ticks() - start_time) // 100 # // stands for integer division
    score_display = time_score + score
    text_surf = font.render(("score " + str(score_display)), True, '#ffffff') #returns surface
    text_rect = text_surf.get_frect(midbottom = (W_WIDTH / 2, W_HEIGHT - 50))
    screen.blit(text_surf, text_rect)
    pygame.draw.rect(screen, '#ffffff', text_rect.inflate(30,20).move(0,-5), 5, 10)
    # inflate for the padding of the rectangle and the text

def reset_game(all_sprites, meteor_sprites, laser_sprites, game_music):
    global player,init_lifecounter, life_counter, score, start_time
    life_counter = init_lifecounter
    all_sprites.empty()
    meteor_sprites.empty()
    laser_sprites.empty()
    update_hearts()
    player = Player(all_sprites)
    score = 0
    start_time = pygame.time.get_ticks()
    game_music.play(loops=-1)

def update_hearts():
    global hearts_list, life_counter
    for i in range(life_counter):
        hearts = Hearts(all_sprites, heart_surf)
        hearts.rect.topleft = (10 + i * 50, 10)
        hearts_list.append(hearts)

#region Imports
#sprite import
meteor_surf = pygame.image.load(join("images", "meteor.png")).convert_alpha() #join to work in both windows and linux
laser_surf = pygame.image.load(join("images", "laser.png")).convert_alpha() #convert alpha to get more perfomance
font = pygame.font.Font(join('images', 'MegamaxJonathanToo.ttf' ), 40)
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]
boost_frames = [pygame.image.load(join('images', 'boost', f'{i}.png')).convert_alpha() for i in range(1, 11)]
heart_surf = pygame.image.load(join("images", "heart.png")).convert_alpha()
bg = pygame.image.load(join("images", "bg.png")).convert_alpha()
bg = pygame.transform.scale(bg, (W_WIDTH, W_HEIGHT))
pygame.display.set_icon(bg)
menubg_frames = [pygame.transform.scale(pygame.image.load(join('images', 'menubackground', f'{i}.png')).convert_alpha(), (W_WIDTH, W_HEIGHT))
                 for i in range(37)]
bt_start_surf = pygame.image.load(join('images', 'buttons', 'btst.png')).convert_alpha()
bt_starthover_surf = pygame.image.load(join('images', 'buttons', 'btst2.png')).convert_alpha()
bt_credits_surf = pygame.image.load(join('images', 'buttons', 'btcred.png')).convert_alpha()
bt_creditshover_surf = pygame.image.load(join('images', 'buttons', 'btcred2.png')).convert_alpha()
bt_exit_surf = pygame.image.load(join('images', 'buttons', 'btexit.png')).convert_alpha()
bt_exithover_surf = pygame.image.load(join('images', 'buttons', 'btexit2.png')).convert_alpha()
logo_surf = pygame.image.load(join('images', 'logo.png')).convert_alpha()
gameover_surf = pygame.image.load(join('images', 'gameover.png')).convert_alpha()
bt_credscreen1_surf = pygame.image.load(join('images', 'cred1.png')).convert_alpha()
bt_credscreen2_surf = pygame.image.load(join('images', 'cred2.png')).convert_alpha()
bt_back_surf = pygame.image.load(join('images', 'buttons', 'btback1.png')).convert_alpha()
bt_backhover_surf = pygame.image.load(join('images', 'buttons', 'btback2.png')).convert_alpha()
bt_yes_surf = pygame.image.load(join('images', 'buttons', 'btyes1.png')).convert_alpha()
bt_yeshover_surf = pygame.image.load(join('images', 'buttons', 'btyes2.png')).convert_alpha()
bt_no_surf = pygame.image.load(join('images', 'buttons', 'btno1.png')).convert_alpha()
bt_nohover_surf = pygame.image.load(join('images', 'buttons', 'btno2.png')).convert_alpha()

#region audio import
laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.025)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
explosion_sound.set_volume(0.025)
damage_sound = pygame.mixer.Sound(join('audio', 'damage.ogg'))
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
player_hit = pygame.mixer.Sound(join('audio', 'hit.mp3'))
player_hit.set_volume(0.1)
game_over_effect = pygame.mixer.Sound(join('audio', 'game_over_effect.wav'))
game_over_effect.set_volume(0.2)
#endregion

#region Sprites group initialize
all_sprites = pygame.sprite.Group()
menu_sprites = pygame.sprite.Group()
credits_sprites = pygame.sprite.Group()
gameover_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
player = Player(all_sprites) #order of creation matters, player after = player on top
# player = instead of just player() because we need the funcion return value to manipulate the player sprite 
update_hearts()
#endregion

#region Menu Instances
menubackground = AnimatedBackground(menubg_frames, (0,0), menu_sprites)
bt_start = Button(W_WIDTH/2, W_HEIGHT/2 + 10, bt_start_surf, bt_starthover_surf, menu_sprites)
bt_credits = Button(W_WIDTH/2, W_HEIGHT/2 + 85, bt_credits_surf, bt_creditshover_surf, menu_sprites)
bt_exit = Button(W_WIDTH/2, W_HEIGHT/2 + 160, bt_exit_surf, bt_exithover_surf, menu_sprites)
logo = Button(W_WIDTH/2, W_HEIGHT/2 - 150, logo_surf, logo_surf, menu_sprites)
#endregion

#region Credits Instances
menubackground = AnimatedBackground(menubg_frames, (0,0), credits_sprites)
credscreen1 = Button(W_WIDTH/2, W_HEIGHT/2 - 275, bt_credscreen1_surf, bt_credscreen1_surf, credits_sprites)
credscreen2 = Button(W_WIDTH/2, W_HEIGHT/2 - 25, bt_credscreen2_surf, bt_credscreen2_surf, credits_sprites)
bt_back = Button(W_WIDTH/2, W_HEIGHT - 275, bt_back_surf, bt_backhover_surf, credits_sprites)
fontcredits_surf1 = font.render("CREDITS", 1, "white")
fontcredits_surf2 = font.render("Game Base Developer", 1, "white")
fontcredits_surf3 = font.render("Main Developer", 1, "white")
#endregion

#region Game Over Instances
menubackground = AnimatedBackground(menubg_frames, (0,0), gameover_sprites)
fontgameover_surf1 = font.render("Try Again?", 1, "white")
bt_yes = Button(W_WIDTH/2 - 125, W_HEIGHT/2 + 150, bt_yes_surf, bt_yeshover_surf, gameover_sprites)
bt_no = Button(W_WIDTH/2 + 125, W_HEIGHT/2 + 150, bt_no_surf, bt_nohover_surf, gameover_sprites)
gameoverlogo = Button(W_WIDTH/2, W_HEIGHT/2 - 150, gameover_surf, gameover_surf, gameover_sprites)
#endregion

#custom events - meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 200) #event triggered, interval (in milissecs)

#region GAME LOOP
while running == False:
    if game_started == 0:
        pygame.mouse.set_visible(True)
        dt = clock.tick(144) / 1000
        
        #action handler
        if bt_start.update():
            game_started = 1
            running = True
        if bt_credits.update():
            game_started = 4
        if bt_exit.update():
            pygame.quit()

        #render
        menu_sprites.update(dt)
        menu_sprites.draw(screen)
        
        #event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        pygame.display.update()

    if game_started == 4:
        pygame.mouse.set_visible(True)
        dt = clock.tick(144) / 1000
        
        #action handler
        if bt_back.update():
            game_started = 0

        #render
        credits_sprites.update(dt)
        credits_sprites.draw(screen)
        screen.blit(fontcredits_surf1, fontcredits_surf1.get_frect(center = (W_WIDTH / 2, 50)))
        screen.blit(fontcredits_surf2, fontcredits_surf2.get_frect(center = (W_WIDTH / 2, W_HEIGHT/2 - 210)))
        screen.blit(fontcredits_surf3, fontcredits_surf3.get_frect(center = (W_WIDTH / 2, W_HEIGHT/2 + 60)))
        
        #event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    pygame.quit()
        
        pygame.display.update()

#region running initialize

game_music.play(loops = -1) #loops forever
scroll = 0
bg_height = bg.get_height()
tiles = math.ceil(W_HEIGHT / bg_height) + 1 # So it doesn't get the wrong number of tiles and + 1 as a buffer if the image doesn't fill the screen
start_time = pygame.time.get_ticks()

#endregion

while running:
    pygame.mouse.set_visible(False)
    game_music.set_volume(0.1)
    if game_started == 1:
        dt = clock.tick(144) / 1000 # delta time (time to generate 1 frame, ex: 1/60 fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == meteor_event:
                x, y = random.randint (100, W_WIDTH-100), random.randint (-200,-150) #created before it appears on screen
                Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))
            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    running = False

        #region background loop
        #draw background // moving upwards -> background going down
        for i in range (tiles):
            y_height = (i * bg_height + scroll) - bg_height
            screen.blit(bg, (0, y_height))

        #scroll control
        scroll += 450 * dt
        if scroll >= bg_height: 
            scroll = 0
        #endregion

        #draw and update the game
        all_sprites.update(dt)
        all_sprites.draw(screen)
        life_counter = collisions(life_counter)
        display_score()
        
        pygame.display.update()

    elif game_started == 2:
        pygame.mouse.set_visible(True)
        dt = clock.tick(144) / 1000
        
        #action handler
        if bt_yes.update():
            reset_game(all_sprites, meteor_sprites, laser_sprites, game_music)
            game_started = 1
            running = True 
        if bt_no.update():
            running = False
            
        #render
        gameover_sprites.update(dt)
        gameover_sprites.draw(screen)
        screen.blit(fontgameover_surf1, fontgameover_surf1.get_frect(center = (W_WIDTH / 2, W_HEIGHT / 2 + 30)))

        #event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        pygame.display.update()

pygame.quit()
#endregion