import pygame
import os
import random
pygame.init()

screen_width=800
screen_height=int(screen_width*0.8)
screen=pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Shooter Game")
#fps
clock=pygame.time.Clock()
fps=60
#bullets
bullet_img=pygame.image.load("img/icons/bullet.png").convert_alpha()
#grenades
Grenade_img=pygame.image.load("img/icons/grenade.png").convert_alpha()
#boxes images
health_box_img=pygame.image.load("img/icons/health_box.png").convert_alpha()
ammo_box_img=pygame.image.load("img/icons/ammo_box.png").convert_alpha()
grenade_box_img=pygame.image.load("img/icons/grenade_box.png").convert_alpha()
item_boxes={
    'Health':health_box_img,
    'Ammo':ammo_box_img,
    'Grenade':grenade_box_img
}
#colors
BG=(144,201,120)
red=(255,0,0)
white=(255,255,255)
font=pygame.font.SysFont('Futura',30)
#player variables actions
moving_left=False
moving_right=False
shoot=False
grenade_thrown=False
grenade=False
def draw_bg():
    screen.fill(BG)
    #pygame.draw.line(screen,red,(0,300),(screen_width,300),2)
    pygame.draw.rect(screen,(50,205,50),(0,300,screen_width,screen_height-300))
def draw_text(text,font,text_col,x,y):
    img=font.render(text,True,text_col)
    screen.blit(img,(x,y))
#game variables
gravity=0.75
TILE_SIZE=40
class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        super().__init__()
        self.speed=10
        self.image=bullet_img
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)
        self.direction=direction
    def update(self):   
        self.rect.x+=self.speed*self.direction
        #delete bullet if it goes off screen
        if self.rect.right<0 or self.rect.left>screen_width:
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

#groups
bullet_group=pygame.sprite.Group()
grenade_group=pygame.sprite.Group()
explosion_group=pygame.sprite.Group()
enemy_group=pygame.sprite.Group()
item_box_group=pygame.sprite.Group()

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

    def update(self):
        self.vel_y+=gravity
        dx=self.direction*self.speed
        dy=self.vel_y
        if 300<self.rect.bottom+dy:
            dy=300 - self.rect.bottom
            self.speed=0
        if self.rect.left+dx<0 or self.rect.right+dx>screen_width:
            self.direction*=-1
            dx=self.direction*self.speed
        self.rect.x+=dx
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
        self.vision=pygame.Rect(0,0,150,20)
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
    def move(self,moving_left,moving_right):
        dx=0
        dy=0
        if moving_left:
            dx=-self.speed
            self.flip=True
            self.direction=-1
            self.direction=-1
        if moving_right:
            dx=self.speed
            self.flip=False
            self.direction=1

        if self.jump and self.in_aire==False:
            self.vel_y=-11
            self.jump=False
            self.in_aire=True
        #apply gravity
        self.vel_y+=gravity
        if self.vel_y>10:
            self.vel_y=10
        dy+=self.vel_y
        if moving_right:
            dx=self.speed
            self.flip=False
            self.direction=1

        if self.jump and self.in_aire==False:
            self.vel_y=-11
            self.jump=False
            self.in_aire=True
        #apply gravity
        self.vel_y+=gravity
        if self.vel_y>10:
            self.vel_y=10
        dy+=self.vel_y
        self.rect.x+=dx
        self.rect.y+=dy
        if self.rect.bottom>300:
            self.rect.bottom=300
            self.vel_y=0
            self.in_aire=False
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
            pygame.draw.rect(screen,(255,255,255),self.vision)

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


player=soldier('player',200,200,1.65,5,20,200,5)
health_bar=Health_Bar(10,10,player.health,player.health)
enemy=soldier('enemy',400,200,1.65,2,20,100,0)
enemy2=soldier('enemy',600,200,1.65,2,20,100,0)
enemy_group.add(enemy)
enemy_group.add(enemy2)
# temp
item_boxe3=ItemBox('Health',100,260)
item_boxe1=ItemBox('Ammo',300,260)
item_boxe2=ItemBox('Grenade',400,260)

item_box_group.add(item_boxe1)
item_box_group.add(item_boxe2)
item_box_group.add(item_boxe3)
run=True
while run:
    clock.tick(fps)
    draw_bg()
    health_bar.draw(player.health)
    draw_text(f"AMMO :",font,white,10,35)
    for x in range(player.ammo):
        screen.blit(bullet_img,(90+(x*10),40))
        draw_text(f"GRENADE :",font,white,10,65)
    for x in range(player.grenades):
        screen.blit(Grenade_img,(140+(x*10),70))
    player.draw()
    player.update()
    for enemy in enemy_group:
        enemy.update()
        enemy.ai()
        enemy.draw()
    bullet_group.update()
    bullet_group.draw(screen)
    item_box_group.update()
    item_box_group.draw(screen)
    grenade_group.update()
    grenade_group.draw(screen)
    player.move(moving_left,moving_right)
    explosion_group.update()
    explosion_group.draw(screen)
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
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False
        #keyboard press
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

        #keyboard release
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