# ============================================
# IMPORTS & INITIALIZATION
# ============================================
import pygame
import os
import random
import csv
from pygame_button import Button
pygame.init()


# ============================================
# SCREEN CONFIGURATION
# ============================================
screen_width=800
screen_height=int(screen_width*0.8)
screen=pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Shooter Game")


# ============================================
# GAME CONSTANTS
# ============================================
gravity=0.75
SCROLL_THRESH=200
ROWS=16
COLS=150
TILE_SIZE=screen_height//ROWS
TILE_TYPES=21
screen_scroll=0
bg_scroll=0
level=1
start_game=False

# ============================================
# CLOCK & FPS
# ============================================
clock=pygame.time.Clock()
fps=60


# ============================================
# LOAD IMAGES
# ============================================
bullet_img=pygame.image.load("img/icons/bullet.png").convert_alpha()
Grenade_img=pygame.image.load("img/icons/grenade.png").convert_alpha()
health_box_img=pygame.image.load("img/icons/health_box.png").convert_alpha()
ammo_box_img=pygame.image.load("img/icons/ammo_box.png").convert_alpha()
grenade_box_img=pygame.image.load("img/icons/grenade_box.png").convert_alpha()
pine1_img=pygame.image.load("img/background/pine1.png").convert_alpha()
pine2_img=pygame.image.load("img/background/pine2.png").convert_alpha()

sky_img=pygame.image.load("img/background/sky_cloud.png").convert_alpha()
mountain_img=pygame.image.load("img/background/mountain.png").convert_alpha()

# Load tile images
img_list=[]
for x in range(TILE_TYPES):
    img=pygame.image.load(f'img/tile/{x}.png').convert_alpha()
    img=pygame.transform.scale(img,(TILE_SIZE,TILE_SIZE))
    img_list.append(img)

item_boxes={
    'Health':health_box_img,
    'Ammo':ammo_box_img,
    'Grenade':grenade_box_img
}


# ============================================
# COLORS & FONTS
# ============================================
BG=(144,201,120)
red=(255,0,0)
white=(255,255,255)
font=pygame.font.SysFont('Futura',30)


# ============================================
# PLAYER ACTION VARIABLES
# ============================================
moving_left=False
moving_right=False
shoot=False
grenade_thrown=False
grenade=False


# ============================================
# UTILITY FUNCTIONS
# ============================================
def draw_bg():
    screen.fill(BG)
    width=sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img,((x*width)-bg_scroll*0.5,0))
        screen.blit(mountain_img,((x*width)-bg_scroll*0.6,screen_height-mountain_img.get_height()-300))
        screen.blit(pine1_img,((x*width)-bg_scroll*0.7,screen_height-pine1_img.get_height()-150))
        screen.blit(pine2_img,((x*width)-bg_scroll*0.8,screen_height-pine2_img.get_height()))

    #pygame.draw.line(screen,red,(0,300),(screen_width,300),2)
    #pygame.draw.rect(screen,(50,205,50),(0,300,screen_width,screen_height-300))

def draw_text(text,font,text_col,x,y):
    img=font.render(text,True,text_col)
    screen.blit(img,(x,y))


# ============================================
# SPRITE CLASSES
# ============================================

class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        super().__init__()
        self.speed=10
        self.image=bullet_img
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)
        self.direction=direction
        self.width=self.image.get_width()
        self.height=self.image.get_height()
    def update(self):   
        self.rect.x+=(self.speed*self.direction)+screen_scroll
        #delete bullet if it goes off screen
        if self.rect.right<0 or self.rect.left>screen_width:
            self.kill()

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        if pygame.sprite.spritecollide(player,bullet_group,False):
            if player.alive:
                player.health-=5
                self.kill()

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy,bullet_group,False):
                if enemy.alive:
                    enemy.health-=25
                    self.kill()


class ItemBox(pygame.sprite.Sprite):
    def __init__(self,item_type,x,y):
        super().__init__()
        self.item_type=item_type
        self.image=item_boxes[self.item_type]
        self.rect=self.image.get_rect()
        self.rect.midtop=(x+TILE_SIZE//2,y+TILE_SIZE-self.image.get_height())
    def update(self):
        self.rect.x+=screen_scroll
        if pygame.sprite.collide_rect(self,player):
            if self.item_type=='Health':
                if player.health+25<=player.max_health:
                    player.health+=25
                else:
                    player.health=player.max_health
            if self.item_type=='Ammo':
                player.ammo+=15
            if self.item_type=='Grenade':
                player.grenades+=3
            self.kill()

# ============================================
# SPRITE GROUPS
# ============================================
'''start_boutton= Button(
    x=screen_width//2-130,
    y=screen_height//2-150,
    width=100,
    height=50,
    image="img/start_btn.png"
)
exit_boutton= Button(
    x=screen_width//2-110,
    y=screen_height//2-50,
    width=100,
    height=50,
    image="img/exit_btn.png"
)'''

bullet_group=pygame.sprite.Group()
grenade_group=pygame.sprite.Group()
explosion_group=pygame.sprite.Group()
enemy_group=pygame.sprite.Group()
item_box_group=pygame.sprite.Group()
decoration_group=pygame.sprite.Group()
water_group=pygame.sprite.Group()
exit_group=pygame.sprite.Group()


# ============================================
# GRENADE CLASS
# ============================================
class Grenade(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        super().__init__()
        self.timer=100
        self.vel_y=-11
        self.speed=7
        self.image=Grenade_img
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)
        self.direction=direction
        self.width=self.image.get_width()
        self.height=self.image.get_height()


    def update(self):
        self.vel_y+=gravity
        dx=self.direction*self.speed
        dy=self.vel_y
        for tile in world.obstacle_list:
            #x chechking collsion
            if tile[1].colliderect(self.rect.x+dx,self.rect.y,self.width,self.height):
                self.direction*=-1
                dx=self.direction*self.speed
            # Y checking
            if tile[1].colliderect(self.rect.x,self.rect.y+dy,self.width,self.height):
                self.speed=0
                if self.vel_y<0:
                    self.vel_y=0
                    dy=tile[1].bottom-self.rect.top

                elif self.vel_y>=0:
                    dy=tile[1].top-self.rect.bottom
                    self.vel_y=0
            
        self.rect.x+=dx+screen_scroll
        self.rect.y+=dy
        self.timer-=1
        if self.timer<=0:
            self.kill()
            explosion=Explosion(self.rect.x,self.rect.y,0.5)
            explosion_group.add(explosion)
            if abs(self.rect.centerx-player.rect.centerx)<TILE_SIZE * 2 and \
            abs(self.rect.centerx-player.rect.centerx)<TILE_SIZE * 2:
                player.health-=50
            for enemy in enemy_group:
                if abs(self.rect.centerx-enemy.rect.centerx)<TILE_SIZE * 2 and \
                        abs(self.rect.centerx-enemy.rect.centerx)<TILE_SIZE * 2:
                            enemy.health-=50
                    



# ============================================
# SOLDIER (PLAYER/ENEMY) CLASS
# ============================================
class soldier(pygame.sprite.Sprite):
    def __init__(self,char_type,x,y,scale,speed,ammo,health,grenades):
        super().__init__()
        self.grenades=grenades
        self.health=health
        self.max_health=health
        self.alive=True
        self.scale=scale
        self.speed=speed
        self.ammo=ammo
        self.start_ammo=ammo
        self.jump=False
        self.in_aire=True
        self.vel_y=0
        self.animation_list=[]
        self.frameIndex=0
        self.char_type=char_type
        self.direction=1
        self.flip=False
        self.action=0
        self.shoot_cooldown=0
        self.update_time=pygame.time.get_ticks()

        # ia variables
        self.move_counter=0
        self.idling=False
        self.idling_counter=0
        self.vision=pygame.Rect((0,0,150,20))
        animation_types=['Idle','Run','Jump','Death']

         #load idle images
        for animation in animation_types:
            temp_list=[]
            number_of_frames=len(os.listdir(f"img/{self.char_type}/{animation}"))
            for i in range(number_of_frames):
                img=pygame.image.load(f"img/{self.char_type}/{animation}/{i}.png").convert_alpha()
                img=pygame.transform.scale(img,(img.get_width()*scale,img.get_height()*scale))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        temp_list=[]

        self.animation_list.append(temp_list)
        self.image=self.animation_list[self.action][self.frameIndex]
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)
        self.width=self.image.get_width()
        self.height=self.image.get_height()

    def move(self,moving_left,moving_right):
        screen_scroll=0
        dx=0
        dy=0

        if self.jump and self.in_aire==False:
            self.vel_y=-13
            self.jump=False
            self.in_aire=True

        #apply gravity
        self.vel_y+=gravity
        if self.vel_y>15:
            self.vel_y=20


        if moving_left:
            dx=-self.speed
            self.flip=True
            self.direction=-1

        if moving_right:
            dx=self.speed
            self.flip=False
            self.direction=1


        dy+=self.vel_y
        for tile in world.obstacle_list:

            #check collision in x direction
            if tile[1].colliderect(self.rect.x+dx,self.rect.y,self.width,self.height):
                dx=0
                if  self.char_type=='enemy':
                    self.direction*=-1
                    self.move_counter=0
            #check y direcion
            if tile[1].colliderect(self.rect.x,self.rect.y+dy,self.width,self.height):

                if self.vel_y<0:
                    self.vel_y=0
                    dy=tile[1].bottom-self.rect.top

                elif self.vel_y>=0:
                    dy=tile[1].top-self.rect.bottom
                    self.in_aire=False
                    self.vel_y=0
        #update rect position
        self.rect.x+=dx
        self.rect.y+=dy
        #update scroll
        if self.char_type=='player':
            if screen_width-SCROLL_THRESH<self.rect.right or self.rect.left<SCROLL_THRESH:
                self.rect.x-=dx
                screen_scroll=-dx
        return screen_scroll
    def shoot(self):
        if self.shoot_cooldown==0 and self.ammo>0:
            self.shoot_cooldown=20
            self.ammo-=1
            bullet=Bullet(self.rect.centerx + self.rect.size[0]*0.6*self.direction,self.rect.centery,self.direction)
            bullet_group.add(bullet)

    def check_alive(self):
        if self.health<=0:
            self.alive=False
            self.speed=0
            self.health=0
            self.update_action(3)
    def dig(self):
        for tile in world.obstacle_list:
            dig_rect = pygame.Rect(self.rect.x+TILE_SIZE*self.direction, self.rect.y, self.width, self.height//2)
            pygame.draw.rect(screen, (255,0,0), dig_rect, 2)  # Debug: visualize dig area
            if tile[1].colliderect(dig_rect):
                world.obstacle_list.remove(tile)
                world.draw()
                break
    def update_animation(self):
        animation_cooldown=100
        self.image=self.animation_list[self.action][self.frameIndex]
        if pygame.time.get_ticks()-self.update_time>animation_cooldown:
            self.update_time=pygame.time.get_ticks()
            self.frameIndex+=1
            if self.frameIndex>=len(self.animation_list[self.action]):
                if self.action==3:
                    self.frameIndex=len(self.animation_list[self.action])-1
                else:
                    self.frameIndex=0
    def update_action(self,new_action):
        if new_action!=self.action:
            self.action=new_action
            self.frameIndex=0
            self.update_time=pygame.time.get_ticks()
    def draw(self):
        screen.blit((pygame.transform.flip(self.image,self.flip,False)), self.rect)
    def forward(self):
        self.rect.x+=5
    def update(self):
        self.update_animation()
        self.check_alive()
        if 0<self.shoot_cooldown:
            self.shoot_cooldown-=1
    def ai(self):
        if self.alive and player.alive:
            if random.randint(1,200)==1 and self.idling==False:
                self.update_action(0)
                self.idling=True
                self.idling_counter=50
            if self.vision.colliderect(player.rect):
                self.update_action(0)

                #shoot
                self.shoot()
            else:
                if self.idling==False:
                    if self.direction==1:
                        ai_moving_right=True
                    else:
                        ai_moving_right=False
                    ai_moving_left=not ai_moving_right
                    self.move(ai_moving_left,ai_moving_right)
                    self.update_action(1)
                    self.move_counter+=1
                    self.vision.center=(self.rect.centerx+(75*self.direction),self.rect.centery)
                    if self.move_counter> TILE_SIZE:
                        self.direction*=-1
                        self.move_counter*=-1
                else:
                    self.idling_counter-=1
                    if self.idling_counter<=0:
                        self.idling=False
        self.rect.x+=screen_scroll
# ============================================
# HEALTH BAR CLASS
# ============================================
class Health_Bar():
    def __init__(self,x,y,health,max_health):
        self.x=x
        self.y=y
        self.health=health
        self.max_health=max_health
    def draw(self,health):
        self.health=health
        ratio=self.health/self.max_health
        pygame.draw.rect(screen,(0,0,0),(self.x-1,self.y-1,152,22))
        pygame.draw.rect(screen,red,(self.x,self.y,150,20))
        pygame.draw.rect(screen,(0,255,0),(self.x,self.y,150*ratio,20))

# ============================================
# WORLD & MAP CLASS
# ============================================
class World():
    def __init__(self):
        self.obstacle_list=[]
    def process_data(self,data):
        for y,row in enumerate(data):
            for x,tile in enumerate(row):
                if 0<=tile:
                    img=img_list[tile]
                    img_rect=img.get_rect()
                    img_rect.x=x*TILE_SIZE
                    img_rect.y=y*TILE_SIZE
                    tile_data=(img,img_rect)
                    if tile<=8:
                        self.obstacle_list.append(tile_data)
                    elif 9==tile or tile==10:
                        water=Water(img,x*TILE_SIZE,y*TILE_SIZE)
                        water_group.add(water)
                    elif 11<=tile and tile<=14:
                        decoration=Decoration(img,x*TILE_SIZE,y*TILE_SIZE)
                        decoration_group.add(decoration)
                        #decoratrion
                    elif tile==15:
                        player=soldier('player',x*TILE_SIZE,y*TILE_SIZE,1.65,6,20,200,5)
                        health_bar=Health_Bar(10,10,player.health,player.health)
                    elif tile==16:
                        enemy=soldier('enemy',x*TILE_SIZE,y*TILE_SIZE,1.65,2,100,100,0)
                        enemy_group.add(enemy)
                    elif tile==17:
                        item_boxe1=ItemBox('Ammo',x*TILE_SIZE,y*TILE_SIZE)
                        item_box_group.add(item_boxe1)

                    elif tile==18:
                        item_boxe2=ItemBox('Grenade',x*TILE_SIZE,y*TILE_SIZE)
                        item_box_group.add(item_boxe2)
                    elif tile==19:
                        item_boxe3=ItemBox('Health',x*TILE_SIZE,y*TILE_SIZE)
                        item_box_group.add(item_boxe3)
                    elif tile==20:#exit
                        exit=Exit(img,x*TILE_SIZE,y*TILE_SIZE)
                        exit_group.add(exit)
        return player, health_bar
    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0]+=screen_scroll
            screen.blit(tile[0],tile[1])

# ============================================
# DECORATION & ENVIRONMENT CLASSES
# ============================================
class Decoration(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
        super().__init__()
        self.image=img
        self.rect=self.image.get_rect()
        self.rect.midtop=(x+TILE_SIZE//2,y+(TILE_SIZE-self.image.get_height()))
    def update(self):
        self.rect.x+=screen_scroll
class Water(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
        super().__init__()
        self.image=img
        self.rect=self.image.get_rect()
        self.rect.midtop=(x+TILE_SIZE//2,y+(TILE_SIZE-self.image.get_height()))
    def update(self):
        self.rect.x+=screen_scroll
class Exit(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
        super().__init__()
        self.image=img
        self.rect=self.image.get_rect()
        self.rect.midtop=(x+TILE_SIZE//2,y+(TILE_SIZE-self.image.get_height()))
    def update(self):
        self.rect.x+=screen_scroll
# ============================================
# EXPLOSION CLASS
# ============================================
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x,y,scale):
        super().__init__()
        self.images=[]
        for i in range(1,6):
            img=pygame.image.load(f'img/explosion/exp{i}.png').convert_alpha()
            img=pygame.transform.scale(img,(int(img.get_width()*scale),int(img.get_height()*scale)))
            self.images.append(img)
        self.frame_index=0
        self.image=self.images[self.frame_index]
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)
        self.counter=0
    def update(self):
        Explostion_Speed=4
        self.counter+=1
        #update explosion animation
        if Explostion_Speed<=self.counter:
            self.counter=0
            self.frame_index+=1
            if self.frame_index>=len(self.images):
                self.kill()
            else:
                self.image=self.images[self.frame_index]



# ============================================
# GAME INITIALIZATION
# ============================================
run=True

# Create empty map
world_data=[]
for row in range(ROWS):
    r=[-1]*COLS
    world_data.append(r)

# Load level data from CSV
with open(f'level{level}_data.csv',newline='') as csvfile:
    reader=csv.reader(csvfile,delimiter=',')
    for x,row in enumerate(reader):
        for y,tile in enumerate(row):
            world_data[x][y]=int(tile)

# Initialize world and player
world=World()
player,health_bar=world.process_data(world_data)


# ============================================
# MAIN GAME LOOP
# ============================================
while run:
    clock.tick(fps)
    if start_game!=False:
        #draw menu
        screen.fill(BG)
#        start_boutton.draw(screen)
#        exit_boutton.draw(screen)
    else:
        # Update background
        draw_bg()
        
        # Load and draw map
        world.draw()
        health_bar.draw(player.health)
        
        # Draw UI (ammo and grenades)
        draw_text(f"AMMO :",font,white,10,35)
        for x in range(player.ammo):
            screen.blit(bullet_img,(90+(x*10),40))
            draw_text(f"GRENADE :",font,white,10,65)
        for x in range(player.grenades):
            screen.blit(Grenade_img,(140+(x*10),70))
        
        # Draw and update player
        player.draw()
        player.update()
        screen_scroll=player.move(moving_left,moving_right)
        bg_scroll-=screen_scroll
        # Update and draw enemies
        for enemy in enemy_group:
            enemy.update()
            enemy.ai()
            enemy.draw()
        
        # Update sprite groups
        bullet_group.update()
        explosion_group.update()
        item_box_group.update()
        grenade_group.update()
        # Update decoration-like groups so their positions react to screen_scroll
        decoration_group.update()
        water_group.update()
        exit_group.update()
        
        # Draw sprite groups
        exit_group.draw(screen)
        water_group.draw(screen)
        decoration_group.draw(screen)
        bullet_group.draw(screen)
        item_box_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        
        # Player movement and actions

        if player.alive:
            if shoot:
                player.shoot()
            elif grenade and grenade_thrown==False and player.grenades>0:
                grenade=Grenade(player.rect.centerx + player.rect.size[0]*0.6*player.direction,player.rect.top,player.direction)
                grenade_group.add(grenade)
                grenade_thrown=True
                player.grenades-=1
            if player.in_aire:
                player.update_action(2)
            elif moving_left or moving_right:
                player.update_action(1)
            else:
                player.update_action(0)
    
    # Event handling
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False
        
        # Keyboard press
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_q:
                moving_left=True
            if event.key==pygame.K_d:
                moving_right=True
            if event.key==pygame.K_e:
                shoot=True
            if event.key==pygame.K_a and player.alive:
                grenade=True
            if event.key==pygame.K_z and player.alive:
                player.jump=True
                
            if event.key==pygame.K_f and player.alive:
                player.dig()
        
        # Keyboard release
        if event.type==pygame.KEYUP:
            if event.key==pygame.K_q:
                moving_left=False
            if event.key==pygame.K_e:
                shoot=False
            if event.key==pygame.K_d:
                moving_right=False
            if event.key==pygame.K_ESCAPE:
                run=False
            if event.key==pygame.K_a:
                grenade=False
                grenade_thrown=False
    
    pygame.display.update()

pygame.quit()