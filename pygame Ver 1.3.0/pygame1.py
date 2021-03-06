#BattleFleets ver 1.3.0
#Nathan Welsh
#Start Date:  /  /17
#  End Date:  /  /18
#                                       TO DO:
#
#    Create labels: Title, players territory                          :Done 
#    Username Input                                                   :Done
#    create AI grid, position, show users fleets to them               :DONE
#
#    check event func: add statements to display sunk fleet image
#    when all ships are sunk									   	  :Done 24/01/18
#
#    Add validation for the AI so it:
#               Knows not to re-select the same square				  :Done 29/12/17 
#               Knows that ships are located both vert				  :Done 01/01/18
#               and horiz and can be guessed by attacking either side :Done 22/01/18
#               of the fleet.
#
#    Add highscore calculator 										  :Done 24/01/2018
#    Stick highscore into textfile                                                                        :Done 26/01/2018
#
#    Leaderboard?... optional                                       :Done
#
#    Show different screens when all fleets sunk 		    :Done 02/02/2018
#
#    Add clock Speed                                                :Done 04/01/2018
#    Add sounds                                                     :Done 08/02/2018
#    
#

import pygame

import random
from random import randint
from random import randrange
from random import choice

import sys
import time
import os


# initialise pygame
# IMPORTANT
pygame.init()
#initialise sound module
pygame.mixer.init()

#load sounds
titleSound = pygame.mixer.Sound('titleSound.wav')
gamePlay_sound = pygame.mixer.Sound('gamePlay.wav')
playerWin_sound = pygame.mixer.Sound('playerWin.wav')
playerLoose_sound = pygame.mixer.Sound('playerLoose.wav')

############################### Global Vars ###########################

                            ### Interface Params ###
(screen_width,screen_height) = (1280,600)


# Capitalise params for ship so they easily
# Distinguishable from display params

#width and screen_height of each box
WIDTH = 40
HEIGHT =40

#spacing between grid boxes
MARGIN = 5

#define colours
GREEN = (66,244,92)
PINK = (255,0,60)
WHITE = (255,255,255)
RED = (255,0,0)
BLACK = (0,0,0)
BLUE = (0,38,255)
YELLOW = (221,255,0)
#defined in a method
colour = None

# C refers to constant, these variables
# are used for offsets so do not get
# important names

#C: this is the x offset for the grids
C = 100

#C2 = y offset
C2 = 175

#enemy board offset params
Ce =(screen_width-(8* (MARGIN+HEIGHT)+MARGIN +C))
Ce2 = C2

### Instruction box globals ###
width = 120
height = 80

score = 0
first_loop = True
clicked = 0

### user sunk counter###
user_sunk = 0


#AI object
ship_ai = None
enemy_sunk_ships = 0

                               ### Global arrays ###
#chosen = []
num_to_generate = [4,3,3,2]
ships_found = []

#time1 = 0
time1 = round(time.clock())
time2 = 0
                            ### Sprite Vars ###

spriteGroup = pygame.sprite.OrderedUpdates()

#setup clock speed/FPS to improve performance
clock = pygame.time.Clock()


#----------------------------------sprite class------------------------------#

class newSprite(pygame.sprite.Sprite):
     def __init__(self, filename):
         pygame.sprite.Sprite.__init__(self)
         self.images = []
         self.images.append(loadImage(filename))

         self.image = pygame.Surface.copy(self.images[0])
         #self.currentImage = 0
         self.rect = self.image.get_rect()
         #self.rect.topleft = (0, 0)

     def addImage(self, filename):
         '''
         Allows For sprite image to be added
         '''
         self.images.append(loadImage(filename))
     
     def move(self, xpos, ypos, centre=False):
        '''
        Allows for the sprite to be positioned on the interface
        centre is false to make sure sprite is not snapped in place
        '''

        if centre:
            #only true if otherwise toggled
            self.rect.center = [xpos, ypos]
        else:
            #positions from the topleft
            self.rect.topleft = [xpos, ypos]
     

     def changeImage(self, index):
         'This subroutine allows for sprite images to updated and will be used when ships are sunk '
         self.image = pygame.Surface.copy(self.images[index])
         #update the image
         oldcenter = self.rect.center
         self.rect = self.image.get_rect()

         #keep same dimentions untill otherwise specified
         self.rect.center = oldcenter
         #updateDisplay()
         self.currentImage = index

class ai_ship_guess:
    """
        Class defining the methods AI uses to destroy the opponant
        knowledge base is a list which stores the AI's previous
        guesses as well as the result of that guess so that the
        other subroutines can predict the next location accordingly.

        Planeconstant stores the plane of orientation of the ships once
        found.

        Edgesfound contains the boundries of the fleet being analysed.
        used so the algorithm can change direction and find ship in
        other direction.

        decide method determines whether the AI knows the orientation of
        a ship or if it must still find it

        guestimate will try to work out the orientation of a fleet by
        guessing nearby and updating the knowledge base accordingly

        deduce is used when the orientation is known and will accuratly target
        the next ship

        
    """
    #Class attributes
    knowledge_base = []

    #Methods
    def __init__( self, ini_x_pos, ini_y_pos ):
        #Instance attributes
        self.orientation = None
        ai_ship_guess.knowledge_base.append([ ini_x_pos, ini_y_pos, 1 ])
        self.root = [ ini_x_pos, ini_y_pos ]
        self.planeconstant = 0
        self.planevariables = {-1:-1,len(enemy_board[0]):-1}
        self.edges_found = []
        
        ###print("Root:\t\t", self.root)
        ###print("KB:\t\t", ai_ship_guess.knowledge_base)
        ###print()

    def update_planevars(self):
        #Called once and thereafter when orientation found, finds relevant plane variables from the KB
        for point in ai_ship_guess.knowledge_base:
            if self.orientation == "h" and point[0] == self.planeconstant:
                self.planevariables[ point[1] ] = point[2]
            elif self.orientation == "v" and point[1] == self.planeconstant:
                self.planevariables[ point[0] ] = point[2]

    def decide(self):
        if not self.orientation:
            ai_resp = self.guestimate()
        elif len(self.edges_found) >= 2:
            #Respond -1 to indicate ship must be sunk
            ai_resp = -1
        else:
            self.update_planevars()
            ai_resp = self.deduce()

        return ai_resp

    def guestimate(self):
        "Deduction - only called when assesing orientation"
        outwith_range = True
        next_guess = []

        #assses orientation by checking all criteria
        while next_guess in [ point[:2] for point in ai_ship_guess.knowledge_base ] or outwith_range:
            #One run guaranteed, equivalent to until loop
            #As no single unit ships exist, this will always eventually find a test
            outwith_range = False

            #orientation not known ro random descicion
            #for direction must be made
            modifier = random.choice([-1,1])
            if random.choice([True,False]):
                next_guess = [ self.root[0], ( self.root[1] + modifier ) ]
                if not( 0<=(self.root[1]+modifier)<len(enemy_board[0]) ):
                    outwith_range = True

                    #continue as we do not want to exit loop yet
                    continue
                guess_orient = "h"
                guess_constant = self.root[0]
                guess_variable = ( self.root[1] + modifier )
                
            else:
                next_guess = [ (self.root[0] + modifier), self.root[1] ]
                if not( 0<=(self.root[0]+modifier)<len(enemy_board[0]) ):
                    outwith_range = True
                    continue
                guess_orient = "v"
                guess_constant = self.root[1]
                guess_variable = ( self.root[0] + modifier )

            ###print("Possibility:",guess_orient,"mod", modifier, "guess", next_guess)

        result = enemy_board[next_guess[0]][next_guess[1]]
        ai_ship_guess.knowledge_base.append([ next_guess[0], next_guess[1], result ])

        ##print ("\nSelected result:\t", next_guess,"-->", ["Negative","Positive"][result])
        ##print ("Knowledge base:\t\t", ai_ship_guess.knowledge_base)

        if result == 0:
            if guess_orient == "h" and ( ([ self.root[0], ( self.root[1] - modifier ), 0 ] in ai_ship_guess.knowledge_base) or ( not (0<=(self.root[1]-modifier)<len(enemy_board[0])) ) ):
                self.orientation = "v"
                self.planeconstant = self.root[1]
                self.planevariables[self.root[0]] = 1
                ##print ("Deduced orientation\t", self.orientation, "\nConst\t\t\t", self.planeconstant, "\nVariables\t\t", self.planevariables)
            elif guess_orient == "v" and ( ([ (self.root[0] - modifier), self.root[1] , 0 ] in ai_ship_guess.knowledge_base) or ( not (0<=(self.root[0]-modifier)<len(enemy_board[0])) ) ):
                self.orientation = "h"
                self.planeconstant = self.root[0]
                self.planevariables[self.root[1]] = 1
                ##print ("Deduced orientation\t", self.orientation, "\nConst\t\t\t", self.planeconstant, "\nVariables\t\t", self.planevariables)
        elif result == 1:
            self.orientation = guess_orient
            self.planeconstant = guess_constant
            self.planevariables[ guess_variable ] = 1
            if self.orientation == "h":
                self.planevariables[ self.root[1] ] = 1
                ##print ("Deduced orientation\t", self.orientation, "\nConst\t\t\t", self.planeconstant, "\nVariables\t\t", self.planevariables)
            elif self.orientation == "v":
                self.planevariables[ self.root[0] ] = 1
                ##print ("Deduced orientation\t", self.orientation, "\nConst\t\t\t", self.planeconstant, "\nVariables\t\t", self.planevariables)


        return next_guess[0], next_guess[1]

    def deduce(self):
        "Deduction - called when orientation is found"
        check_direction = random.choice([-1,1])

        #Start at any hit point in the dictionary
        #Guarenteed point due to deduce calling conditions within decide
        for key in self.planevariables.keys():
            if self.planevariables[key] == 1:
                progression_point = key
                break

        #encountered_edges = []
        next_guess_var = None

        ###print()

        while next_guess_var == None:
            progression_point += check_direction
            ##print ("\nFound Edges:\t\t", self.edges_found, "\nPP:\t\t\t", progression_point,"\nDirection:\t\t", check_direction) #"\nEncountered_edges:\t", encountered_edges, "\nFound Edges:\t\t", self.edges_found, "\nPP:\t\t\t", progression_point,"\nDirection:\t\t", check_direction

            #if self.planevariables.has_key(progression_point):
            if progression_point in self.planevariables.keys():
                
                ##print ("Value:\t\t\t", self.planevariables[progression_point], "- Exists in KB")
                if self.planevariables[progression_point] == 0 or self.planevariables[progression_point] == -1 :
                    
                    # 0 signifies empty sea ie. edge of ship; -1
                    # means outside board ONLY WITHIN THE BOUNDS OF
                    # AI ANALYSIS encountered_edges.append(check_direction)
                    
                    #the values 0 1 are different from update_interface() as they refer to
                    #fleet health.
                    
                    if not ( check_direction in self.edges_found ):
                        self.edges_found.append(check_direction)
                    ##print ("\n!- Direction change -!\nFound Edges:\t\t", self.edges_found)#Encountered_edges:\t", encountered_edges,
                                                                                          #"\nFound Edges:\t\t", self.edges_found
                    if len(self.edges_found) == 2:
                        
                        #This prevents infinite looping
                        #Respond -1 to indicate ship must be sunk
                        return -1
                    check_direction = -1 * check_direction

            elif not ( 0 <= progression_point < len(enemy_board) ):
                ##print ("!- Out point at", progression_point, "-!")
                self.planevariables[progression_point] = -1
                #encountered_edges += 1
                if not ( check_direction in self.edges_found ):
                    self.edges_found.append(check_direction)
                ##print ("\n!- Direction change -!\nFound Edges:\t\t", self.edges_found) #Encountered_edges:\t", encountered_edges, "\nFound Edges:\t\t", self.edges_found
                if len(self.edges_found) == 2:
                    #This prevents infinite looping
                    #Respond -1 to indicate ship must be sunk
                    return -1
                check_direction = -1 * check_direction

            else:
                ##print ("Variable:\t\t", progression_point, "- Not in KB, submit")
                next_guess_var = progression_point

        if self.orientation == "h":
            next_guess = [self.planeconstant, progression_point]
        elif self.orientation == "v":
            next_guess = [progression_point, self.planeconstant]

        ##print ("\nGuess:\t\t\t", next_guess)

        #add results to knowledge base for future use
        result = enemy_board[next_guess[0]][next_guess[1]]
        ai_ship_guess.knowledge_base.append([ next_guess[0], next_guess[1], result ])

        self.planevariables[progression_point] = result

        ##print ("Result:\t\t\t", next_guess,"-->", ["Negative","Positive"][result])
        ##print ("\nKnowledge base:\t\t", ai_ship_guess.knowledge_base)
        ##print ("Variable set:\t\t", self.planevariables)

        if result == 0:
            self.edges_found.append(check_direction)
        elif result == 1 and (progression_point+check_direction) in self.planevariables.keys():#self.planevariables.has_key(progression_point + check_direction):
            if self.planevariables[(progression_point + check_direction)] == 0 or self.planevariables[(progression_point + check_direction)] == -1:
                #encountered_edges += 1
                if not ( check_direction in self.edges_found ):
                    self.edges_found.append(check_direction)
                ##print ("\n!- Next in ship plane is edge -!\nFound Edges:\t\t", self.edges_found) #Encountered_edges:\t", encountered_edges, "\nFound Edges:\t\t", self.edges_found
                #if len(self.edges_found) == 2:
                #    #This prevents infinite looping
                #    #Respond -1 to indicate ship must be sunk
                #    return -1

        return next_guess[0], next_guess[1]

#----------------------------------subroutines-------------------------------#


                  ### read/write textfile vars ###
                            
def get_highscore(name):
        '''
        # This sub searches through the specified textfile
        # then finds the username and coresponding higscore
        # IF username not found then it creates one and allowcates
        # score of 0.
        # data is formatted like so:   username:highscore
        '''
        #print('name IN:',name)
    #will raise error if not exist
        try:
          with open('username.txt','r') as file:
              for line in file:

                string_devider = ":"
                for search in range(0, len(line)):

                    # index of : will change every line and file
                    # line not an array so this method is more
                    # efficient as .split() cannot be used

                    if line[search] == string_devider:

                        #gets from up to:
                        if line[:search] == name:
                          #print('found',line[:search])
                          highscore = int(line[search+1:])
                          return highscore

                    else: pass #not found that iteration

         #Not found so add username and score in new line
          with open('./username.txt','a') as file: #append not truncate
                  #print('name OUT:',name)
                  file.write('\n'+name+':'+'0')
                  highscore = 0
                  return highscore

        #does not exist so
        #create textfile and add username
        except IOError:
             file = open('./username.txt','w')
             file.write('\n'+name+':'+'0')
             file.close()

             #return 0 as new user
             return 0


#these are used for saving highscore
def get_largest(list, start):
    
    '''
    helper method to find the largest 
    number in list starting from 
    a specific index
    '''

    #say the number of the index is the largest
    large = start
    for i in range(start +1, len(list)):
        if int(list[i])>int(list[large]):
            #largeer num found, update index
            large = i
            ##print('large',list[large])
    return large 

def selection_sort(list,list2):
    '''
    sorts using the selection sort algorhithm
    '''
    #iterate for num items in list
    for item in range(len(list)):
    #call get largest function which 
    #finds the largest value in the list 
        largest = get_largest(list,item)
        if largest != item:
        #swap current element with 
        #largest if any            
            list[largest],list[item]=list[item],list[largest]
            list2[largest],list2[item] = list2[item],list2[largest]
            
    return list,list2



def save_highscore(name,score):
    string_devider = ":"
    with open('username.txt','r+') as file:

        data = file.readlines()
        list = data
        ##print(data)
        details = []
        for row in range(len(data)):
        
          if row == 0:
                #print('e_row rilter')
                pass
          else:
              details.append( list[row] )
              
          
              for i in range(len(list[row])):
                
                if list[row][i] == string_devider and list[row][i]:

                  string_dev_pos = i              
                  db_name = list[row][:string_dev_pos]
                  
                  if db_name == name:
                    details.remove( list[row] )
                    details.append('\n'+str(name)+':'+str(score))
     
        #now sort the list of names
        score_list = []
        name_list = []
        for i in details:

            #removes blank entities
            if ':' not in i:
                #print(': not found pass')
                pass
            else:
                 #print(i)
                #quickly parse data to be sent
                #to sub in correct format
                
                 d = i.strip('\n').split(':')
                 try:
                     #print('IN FILE:',d)
                     name_list.append(d[0])
                     score_list.append(d[1])
                 except IndexError:
                     pass
                     #print('PASS AT:',d)
             
        #print('IN SORT',name_list,score_list)

        #sort arrays
        #reset data array so it can store
        #new sorted data
        data = []
        score_list,name_list = selection_sort(score_list,name_list)
        
        ##print('OUT SORT',name_list,score_list)
        if len(score_list) == len(name_list):
            print('LIST EQUALITY')
        else:
            print('S',len(score_list),'n',len(name_list))
            
        for i in range(len(name_list)):
            #created sorted array
            data.append(str(name_list[i])+':'+str(score_list[i]))
            #print('appended',data[i])
      
    with open('username.txt','w') as file:

        #write to file
      for line in range(len(data)):
        #print('OUT FILE:',data[line])
        file.write('\n'+data[line])
                   
def display_leaderboard(name):
    #clear screen
    bk_img = pygame.image.load("new_background.bmp").convert_alpha() 
    screen.blit(bk_img,(0,0))

    #not update screen as will update with leaderboard
    leaderboard_b = pygame.image.load('leaderboard.png').convert_alpha()
    screen.blit(leaderboard_b,(0,0))
    
    font_size = 24
    #throwaway x coords as it centers
    location = [0,180]
    message = "<---------- Leaderboard ---------->"
    make_message(message,WHITE,font_size,location,centre=True)
    
    font_size -=4
    with open('username.txt','r') as file:
        counter = 0
        for line in file:

            #show top 10 highscores
            if counter<10:

                string_devider = ":"
                for search in range(0, len(line)):

                    # index of : will change every line and file
                    # line not an array so this method is more
                    # efficient as .split() cannot be used

                    if line[search] == string_devider:
                        s_d_pos  = search 
                        if line[:s_d_pos] == name:
                            N_COLOR = YELLOW
                        else:
                            N_COLOR = WHITE
                            
                        lboard_name = line[:search]
                        highscore = int(line[search+1:])

                        #display place
                        location = [450,200+(counter*20) ]
                        message = str(counter+1)+str('.')
                        make_message(message,N_COLOR,font_size,location)

                        #display name
                        location = [500,location[1]]
                        message = str(lboard_name)
                        make_message(message,N_COLOR,font_size,location )

                        #display score
                        location = [800,location[1]]
                        message = str(highscore)
                        make_message(message,N_COLOR,font_size,location)
                        counter+=1
                        
    #show leaderboard at once
    pygame.display.flip()
    location = [0,420]
    
    while True:
        for event in pygame.event.get():

            #hover event
            try:
                if event.pos[0] in range(596,778) and event.pos[1] in range(420,440):
                    make_message('<Back>',YELLOW,24,location,centre=True)
                else:
                    make_message('<Back>',WHITE,24,location,centre=True)
            except AttributeError:
                make_message('<Back>',WHITE,24,location,centre=True)
                pass               
                
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

            #click event
            elif event.type == pygame.MOUSEBUTTONDOWN:
                press_instructions(event)
                #print(event.pos)
                
                if event.pos[0] in range(596,778) and event.pos[1] in range(420,440):
                    #play again
                    #pygame.draw.rect(screen,(colour),([463,150,355,360]))
                    return True
                else: pass
				
            else: pass  

                   ###Sprite Routines ###

def makeSprite(filename):
    #allows for new sprite to be created

    #creates a sprite instance
    thisSprite = newSprite(filename)
    return thisSprite

def showSprite(sprite):
    #allows for sprites to be
    #coalated for easier handling
    spriteGroup.add(sprite)

def moveSprite(sprite, x, y, centre=False):
    ''' This sub allows for positioning of sprites'''
    sprite.move(x, y, centre)
    updateDisplay()

def loadImage(fileName, useColorKey=False):
    '''
        Is called from Sprite class and allows for
        images to be used as sprites. This is not used
        for other images as this scales images to a
        given size.
    '''

    if os.path.isfile(fileName):

        if fileName == "./instructions.bmp":
             #Instructoins are larger
             image = pygame.image.load(fileName)
             image = image.convert_alpha()

             image = pygame.transform.scale(image,(80,80))
             # Return the image
             return image
        else:
             image = pygame.image.load(fileName)
             image = image.convert_alpha()

            #scale image
             image = pygame.transform.scale(image,(WIDTH,HEIGHT))
             # Return the image
             return image
    else:
        #if image file not found then raise error
        raise Exception("Error loading image: " + fileName + " - Check filename and path?")


                  #### Interface subs ####

def updateDisplay():
    #any changes made to the game
    #are visually updated here
     spriteRects = spriteGroup.draw(screen)

     #.flip() is more efficient than .update()
     pygame.display.flip()

def screen_size(width,screen_height):
    '''
    pygame.display.set_mode(), allows
    us to create our basic display
    '''
    screen = pygame.display.set_mode((screen_width,screen_height))
    pygame.display.flip()
    return screen

def prefrences(screen):
    '''
    this sub. makes the background colour white,
    '''
    #sets background colour
    #global colour
    #colour = (160,160,160)
    bk_img = pygame.image.load("new_background.bmp").convert_alpha() 
    screen.blit(bk_img,(0,0))
    #screen.fill(colour)
    pygame.display.flip()
    return

def set_title(title):
    '''
    this subroutine, sets the screen title
    '''
    pygame.display.set_caption(title)
    pygame.display.flip()
    return


def make_message(message,colour,text_size,location,centre=False):
    'This Subroutine takes text and converts'
    'it to an object which can be blit onto screen'

    font = pygame.font.SysFont("OCR A Extended",text_size)
    screen_text = font.render(message,True,colour)
    
    if centre == False:
        
        screen.blit(screen_text, location)
        pygame.display.flip()
        return screen_text
    else:
        location = [(screen_width//2 - 0.5*(screen_text.get_rect().width)),location[1]]
        screen.blit(screen_text, location)
        pygame.display.flip()
        return screen_text
                ########## Sea Grid Subs ##########

def make_sea_grid(screen):
    '''
    This subroutine creates the sea board
    '''
    sea_board = []
    for row in range (8):
        sea_board.append([])
        for col in range(8):
            sea_board[row].append(0)
    return sea_board

def new_validate( board, orient, x_pos, y_pos, length, sign ):
    'This is the second attempt to create a validaion for'
    'The proposed seaboard as the first did not work correctly'

     # validation for horizontal
    if orient == 0:
        
        #Make sure fleet in boards dimentions
        if 0 <= x_pos+(sign*length) < len(board[0]):
            ###print("FITS IN BOARD")
            pass
        else:
            #fleet is outwith board
            ###print("DOES NOT FIT IN BOARD")
            return False

        #Clear of other boats?
        for offset in range(length):
            #Check above area
            try:
                up = board[y_pos-1][x_pos+(offset*sign)]
            except IndexError:
                #okay to recieve index error as it means
                #must be at edge of grid where no other fleets can be
                ###print("EDGE OF GRID ABOVE -PASS")
                pass
            else:
                if up == 1:
                    #fleet above attempted location
                    ###print("CONFLICT ABOVE BOAT")
                    return False

            #Check on
            if board[y_pos][x_pos+(offset*sign)] == 1:
                #fleet above attempted location
                ###print("CONFLICT ON BOAT")
                return False

            #Check below area
            try:
                dn = board[y_pos+1][x_pos+(offset*sign)]
            except IndexError:
                ###print("EDGE OF GRID BELOW -PASS")
                pass
            else:
                if dn == 1:
                    #fleet below attempted location
                    ###print("CONFLICT BELOW BOAT")
                    return False

        #Check either side of the fleet
        try:
            lft = board[y_pos][(x_pos+(-1*sign))]
        except IndexError:
            pass
        else:
            if lft == 1:
                #Theres a fleet left of attemped location
                ###print("CONFLICT AT LEFT")
                return False

        try:
            rgt = board[y_pos][(x_pos+(length*sign))]
        except IndexError:
            
            #not on board so
            #ships at edge
            ###print("current pos +1 outwith board \nso ship is on an edge\npass")
            pass
        
        else:
            if rgt == 1:
                #Theres a fleet right of attempted location
                ###print("CONFLICT AT RIGHT")
                return False

    else:
        # Validation for vertical

        #In range?
        if 0 <= y_pos+(sign*length) < len(board):
            pass
        else:
            #fleet is outwith board
            ###print("OUTWITH BOARD")
            return False


        #Make sure fleet is clear of other fleets?
        for offset in range(length):
            #Check left
            try:
                lf = board[y_pos+(offset*sign)][x_pos-1]
            except IndexError:
                pass
            else:
                if lf == 1:
                    #Theres a fleet left of selected location
                    ###print("CONFLICT LEFT OF BOAT")
                    return False

            #Check on
            if board[y_pos+(offset*sign)][x_pos] == 1:
                #Theres a fleet at selected location
                ###print("CONFLICT ON BOAT")
                return False

            #Check right
            try:
                rt = board[y_pos+(offset*sign)][x_pos+1]
            except IndexError:
                pass
            else:
                if rt == 1:
                    #Theres a fleet right of selected location
                    ###print("CONFLICT RIGHT OF BOAT")
                    return False

        #Check either end of the fleet
        try:
            top = board[(y_pos+(-1*sign))][x_pos]
        except IndexError:

            # Allowed to pass as if Index error
            # then ship postioned at edge of board
            pass


        else:
            if top == 1:
                #Theres a fleet at one end of attempted position
                ###print("CONFLICT AT END")
                return False

        try:
            btm = board[(y_pos+(length*sign))][x_pos]
        except IndexError:
            pass
        else:
            if btm == 1:
                #Theres a fleet at the other end of attempted position
                ###print("CONFLICT AT END")
                return False
    ###print('VALIDATION PASSED')
    return True

def generate_fleets(board,fleet=[2,3,3,4]): #define fleet as passed in as it improves efficiency
    """     Generates fleet on board, default standard fleet
            The fleet array specifies the length of the fleets
            to be generated. The fleets will then be placed
            vertically or horizontally depending on a random selection.
    """
    current_fleet = 0
    ###print('\n\n\\t\tgenerating...\n\n')
    while True: #repeats untill 4 fleets placed

        ###print("\n")
        ###print('\n\n')
        orient = randint(0,1) #0= horizontal 1= vertical
        if orient == 1:
            ###print("Vertical")
            pass
        else:
            ###print("Horizontal")
            pass

        #generate x position
        x_pos = randrange(0,len(board[0]))
        ###print('X',x_pos)

        #generate y position
        y_pos = randrange(0,len(board))
        ###print('Y',y_pos)

        #Generate position for direction(left or right)
        sign = choice([-1,1])
        ###print("Sign:",sign)

                #length of fleet selected
        length = fleet[current_fleet]
        ###print("Length",length)

                #if fleet passes validation criteria

        #for i in board: ###print(i)

        if new_validate( board, orient, x_pos, y_pos, length, sign ):

            if orient == 0: #add fleets horizontally

                #for every box/fleet in length var
                for box in range(length):

                    #add to sea board
                    board[y_pos][(x_pos+(box*sign))] = 1
            else:
                #Add fleets vertically
                for box in range(length):
                    board[(y_pos+(box*sign))][x_pos] = 1

            if current_fleet + 1 == len(fleet):
                #If at end of fleet
                break
            else:
                current_fleet += 1
    #for i in board:
        ###print(i)
        
    return board

       

        
def check_user_event(mouse_pos):

    '''
        this is called when event is triggered to
       check to see if battle fleet has been clicked
    '''
    
    # global used so
    # global vars can
    # be edited
    global user_sunk
    global sea_board
    global score
    global clicked

    #gets the users mouse event position
    position_mouse = mouse_pos

    #compare every area of sea to where selected by player
    try:
        'When offsetting value it is important to -C and -C2'
        'As this is the only way to to get the user click in'
        'the correct place other wise symantical errors will'
        'be present and program wont function properly'

        #gets tile clicked on by user
        col = (position_mouse[0] -C)  // ((WIDTH + MARGIN))
            
        row = (position_mouse[1] -C2) // ((HEIGHT + MARGIN))                       
            
        #if tile contains fleet undiscovered
        if sea_board[row][col] == 1:

            #add choice to an array so user
            #cant select same area again

            sea_board[row][col] = 2
            
            user_sunk +=1
            
            calculate_score(1)

            temp_count = 0
            for sink_coord in check_sink( 0, row, col ):
                sea_board[sink_coord[0]][sink_coord[1]] = 3

                # will update multiple times
                # allows for larger deviation in scores
                # agaisnt time
                calculate_score(2)
                temp_count +=1
                
            if temp_count !=0:
                clicked = 0
                return               

        
        elif sea_board[row][col] == 2 or sea_board[row][col] == "M":
             raise IndexError

        elif sea_board[row][col] ==0:
            #chosen.append([col,row,sea_board[col][row],False])

            #has missed ship
            sea_board[row][col] = "M"
            
        else:
            
            pass
            
    

    #''' exceuted if user does not select a tile of grid'''
    except IndexError:
        pass
        ######print('Error not selected grid')
    clicked +=1
    #print(clicked)
    return

def check_sink( team, row, col ):
    '''
        Maps out and checks the dimentions of the
        fleet and makes sure that there are no ships
        to be sunk. It does this in a similar
        way to the AI
        
        IF there is a sunk fleet it changes the value
        of the fleet so update interface can show the
        correct sunk fleet image and so user knows to
        seek out other fleet. 
    '''
    
    # when team is 0 takes 1st index
    work_board = [ sea_board, enemy_board ][team]
    orient = ""
    ship_constant = -2
    ship_plane = []
    
    #discovers orientation
    try:
        lf = work_board[row][(col-1)]
    except IndexError:
        lf = 0 
        
    try:
        rt = work_board[row][(col+1)]
    except IndexError:
        rt = 0
        
    try:
        up = work_board[(row-1)][col]
    except IndexError:
        up = 0
    
    try:
        dn = work_board[(row+1)][col]
    except IndexError:
        dn = 0
        
    #sets up constant and progression 
    #depending on orient 
    if lf in [1,2] or rt in [1,2]:
        orient = "h"
        ship_constant = row
        progression_point = col
        ship_plane = work_board[row]
    else:
        orient = "v"
        ship_constant = col
        progression_point = row
        ship_plane = [ rw[col] for rw in work_board ]
        
    check_direction = 1
    edgz = []
    edgepos = []
    twos_pos = []
    
    ##print ("ROW:", row)
    ##print ("COL:", col)
    ##print ("ORIENT:", orient)
    ##print ("SHIPROW:", ship_plane)
        
    while True:
        ##print ("PREPROGRESS:", progression_point)
        progression_point += check_direction
        ##print ("PROGRESS:", progression_point)
        try:
            ##print ("VALUE:", ship_plane[progression_point])
            if ship_plane[progression_point] == 0 or ship_plane[progression_point] == "M":
                raise IndexError
                    
            #return nothing as not all hit yet
            elif ship_plane[progression_point] == 1:
                return []
                
            # record position of 2
            elif ship_plane[progression_point] == 2:
                if not progression_point in twos_pos:
                    twos_pos.append( progression_point )
                
        except IndexError:
            #bounce and go other direction
            #as found edge of ship
            if not ( check_direction in edgz ):
                edgz.append(check_direction)
                edgepos.append(progression_point)
                
            check_direction *= -1
            
            #if everything between 
            #edges is a 2
            if len(edgz) == 2:
                break
            
           
    sink_arr = []
    edge_arr = []
    
    #adds coords to sink_arr to be 
    #returned and sunk
    for hit_pos in twos_pos:
        if orient == "h":
            sink_arr.append([ ship_constant, hit_pos ])
        else:
            sink_arr.append([ hit_pos, ship_constant ])
    
    #return to ai so it can 
    #start looking elsewhere
    for edge in edgepos:
        if orient == "h":
            edge_arr.append([ ship_constant, edge ])
        else:
            edge_arr.append([ edge, ship_constant ])
            
    if team == 0:
        return sink_arr
    else:
        return sink_arr, edge_arr
    
        ########## AI Subs/Section ###########

def ai_guess():
    '''
        Generates coords, makes sure they
        fit on board and have not been selected
        before then passes the guess to the AI
    '''
    global ship_ai
    
    if ship_ai:
        ai_turn = ship_ai.decide()
        if ai_turn != -1:
            return ai_turn
        else:
            ship_ai = None

    #triggers while loop    
    picked_value = 2

    #if picked before
    while picked_value in [ "M", 2, 3 ]:

        'regenerate coords untill meets criteria' 
        
        x_pos = random.randrange(0,len(enemy_board[0]))
        y_pos = random.randrange(0,len(enemy_board[0]))
        picked_value = enemy_board[x_pos][y_pos]

        if picked_value == 1:
            ship_ai = ai_ship_guess(x_pos,y_pos)
        elif picked_value != 0:
            
            #Add something here to prevent infinite looping in case of board full
            #fix added in main loop 01/02/2018
            
            if enemy_sunk_ships == 12:
                return -2,-2
            
    return x_pos, y_pos
    
def check_ai_event(row, col):

    global enemy_board
    global enemy_sunk_ships

    
    if enemy_board[row][col] in [ "M", 2, 3 ]:
        pass
        ##print used in testing to solve AI reselecting used tile bug
        ##print ("DAFUQ:", row, ",", col, ":", enemy_board[row][col])

    elif enemy_board[row][col] == 1:
        enemy_board[row][col] = 2
        enemy_sunk_ships += 1
        
        try:
            sinks, edgez = check_sink( 1, row, col )
            for sink_coord in sinks:
                ##print ("3 at", row, ",", col)
                enemy_board[sink_coord[0]][sink_coord[1]] = 3
                
            for edge_coord in edgez:
                ai_ship_guess.knowledge_base.append([ edge_coord[0], edge_coord[1], 0 ])
        except ValueError:
            #error is raised as 
            #array is empty
            pass
            
                
    elif enemy_board[row][col] == 0:
        enemy_board[row][col] = "M"
        
    else:
        pass
    
def update_kb():
    'updates the AI knowledge base'
    row_pos = 0
    for row in enemy_board:
        col_pos = 0
        for value in row:
            
            #if selected coordinate point not already in the Knowledge base
            if ( value == "M" or value == 3 ) and not ( [ row_pos, col_pos ] in [ point[:2] for point in ai_ship_guess.knowledge_base ] ):
                ai_ship_guess.knowledge_base.append([ row_pos, col_pos, 0 ])
            col_pos += 1
        row_pos += 1

def update_interface():

    '''
    This subroutine updates the interface by
    changing any sprites if necessary
    '''

    for row in range(8):
        for col in range(8):

            sprite.changeImage(0)

            if sea_board[row][col] == 2:
                    #light show ship
                sprite.changeImage(3)

            elif sea_board[row][col] == 3:
                    #black
                sprite.changeImage(4)

                #m for miss
            elif sea_board[row][col] == "M":
                sprite.changeImage(1)

            else:
               #show water
               pass


                #move sprite before updating interface
            moveSprite( sprite ,((MARGIN + WIDTH) *col  + MARGIN +C), ((MARGIN + HEIGHT) * row + MARGIN +C2 ) )

                #update interface by showing updated sprite
            showSprite(sprite)

            ### Update AI INTERFACE Section ###

    for row in range(8):
        for col in range(8):

            sprite.changeImage(0)

            if enemy_board[row][col] ==1:
                sprite.changeImage(2)
            elif enemy_board[row][col] ==2:
                 sprite.changeImage(3)
            elif enemy_board[row][col] ==3:
                 sprite.changeImage(4)
            elif enemy_board[row][col] =="M":
                 sprite.changeImage(1)

                #move sprite before updating interface
            moveSprite( sprite ,((MARGIN + WIDTH) *col  + MARGIN +Ce), ((MARGIN + HEIGHT) * row + MARGIN +Ce2 ) )
                #update interface by showing updated sprite
            showSprite(sprite)

def instructions():

        'sets up instructions button' 
    
        location_x,location_y = (screen_width-145), (screen_height-45)
        #instruction_button = newSprite('./instructions.bmp')
        make_message("<HELP!>",WHITE,30,[location_x,location_y])
        #moveSprite(instruction_button,location_x,location_y)
        #showSprite(instruction_button)
        return #instruction_button

def load_instructions_interface():
    #load instructions and back button
    
    screen.blit(pygame.image.load('./instructions.png').convert_alpha(), (0,0) )

    #hide help button as already in help
    location = [(screen_width-145), (screen_height-45)]
    pygame.draw.rect(screen,BLACK,([location[0],location[1],150,50]))
    
    location = [(screen_width//2-50), (screen_height-45)]
    loop = True
    while loop:
        for event in pygame.event.get():

            #loop = press_instructions(event)
            
            if event.type == pygame.MOUSEMOTION and (event.pos[0] in range(screen_width//2-50,screen_width//2+50) ) and (event.pos[1] in range(screen_height-40,screen_height-10) ):
                COLOUR = YELLOW
            else:
                COLOUR = WHITE
                
            #displays hover as highlighted or non highlighted state
            pygame.draw.rect(screen,BLACK,([location[0],location[1],150,50]))   
            make_message("<Back>",COLOUR,24,location,centre=True)

            
            if event.type == pygame.MOUSEBUTTONDOWN and ( event.pos[0] in range(screen_width//2-50,screen_width//2+50) ) and ( event.pos[1] in range(screen_height-40,screen_height-10) ):
                
                #load previous screen
                back_g =  pygame.image.load('new_background.bmp').convert_alpha()
                screen.blit(back_g,(0,0))
                

                #checks game state
                try:
                    if len(name)>2:

                        #check if during play
                        if enemy_sunk_ships <12 and user_sunk<12:
                            
                            #--- restore session --- #
                            
                            instructions()
                            #load in highscore
                            update_highscore_display( get_highscore( name ) )

                            #user starts with no score
                            update_score_display(score)
                            
                            screen.blit( pygame.image.load('board_bk.png').convert_alpha(),(0,0))
                            update_interface() 
                            #Display enemy territory label 
                            location = [(MARGIN + WIDTH)+C-30 ,C2-HEIGHT//2 -MARGIN ]
                            make_message("Enemy Territory",(YELLOW),25,location)

                            #display username on interface
                            #location = [( ( screen_width//2 ) + ( ( screen_width//2-100 ) //6 ) -( len(name)*2) -100 ) ,( screen_height//screen_height+100 )]
                            location = [(screen_width//2) + (screen_width//4)-135,Ce2-HEIGHT//2 -MARGIN]
                            make_message(name+"'s Territory",(YELLOW),22,location)
                            
                            # --- session restored ---# 
                            
                        elif user_sunk == 12:
                            #check user win
                            update_interface()
                            instructions()
                            
                            #load in highscore
                            update_highscore_display( get_highscore( name ) )

                            #user starts with no score
                            update_score_display(score)
                            return player_win()
                        else:
                            #user loss
                            update_inerface()
                            instructions()
                            return player_loose()
                        
                    #if not press do nothing
                    else: pass

                #error as name not defined
                #user must be on start sceen
                except NameError:
                    #returns true for get_input()
                    #data handling
                    return True
                
                #break loop if no conditions occur
                #safeguard to stop loop
                loop =  False
            
            

def press_instructions(event):
        'checks if instructions has been pressed'

        #if mouse move then check for highlight
        #better practice than previous
        #try: .. Except:.. method
        if event.type == pygame.MOUSEMOTION:
                if event.pos[0] >= (screen_width-145) and event.pos[1] >= (screen_height-45):
                    COLOR = YELLOW
                else:
                    COLOR = WHITE
            
                pygame.draw.rect(screen,BLACK,([screen_width-150,screen_height-50,150,50]))
                make_message("<HELP!>",COLOR,30,[screen_width-145,screen_height-45])
                
        if event.type == pygame.MOUSEBUTTONDOWN:

            #if pressed then show  instructions interface
            if event.pos[0]  >= (screen_width-145) and event.pos[1] >= (screen_height-45):
                    #print('LOADING INTERFACE...')
                    return load_instructions_interface()
        

         
             ############## User Inut & Validation ####################

def get_input(name= []):
    """
        Allows for user input livetime char by char
        filters out illegal chars and allows for user
        to delete chars as they are typed if they choose
        to. 
    """
    global titleSound
    bk_img = pygame.image.load("new_background.bmp").convert_alpha() 
    screen.blit(bk_img,(0,0))
    pygame.display.flip()

    titleSound.play(-1)

    #bottom lhs corner
    location = [100,550]

    #sets location of error message
    ERR_COLOR = (0,0,0)
    constant1 = 600
    contant2 = 25
    error_location = [ 100,550 , constant1,contant2]
    error_text_location = [ 100,575, constant1,contant2]

    #sets location of text
    make_message("Please Enter A Username:",(WHITE),15,location)
    if len(name)>=15:
         make_message("ERROR: Cannot be more than 15 characters!",(RED),15,error_text_location)
    #registers each key

    #stroke individually so must be an array

    name = []
    while True:
            for event in pygame.event.get():
                    if press_instructions(event):                        
                        return get_input()
                    
                    if event.type == pygame.QUIT:
                            pygame.quit()
                            
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                         #press_instructions(event)
                         pass
                    elif event.type != pygame.KEYDOWN: pass
                    #if not key press

                    else:
                            #print("GOT KEY",chr(event.key))
                            try:
                                 #filters out non compatibles
                                 ##print (event.key)
                                 if event.key in range(97,123) or event.key in range(48,58) or event.key in [8,13,32]:
                                    key =  chr(event.key)
                                 else: 
                                    key = ""
                                        
                            except ValueError as wrongKey:
                                 key = ''
							
                            if key == '\x08': #backspasce
                                    name = name[0:-1]
                                    pygame.draw.rect(screen,(ERR_COLOR),(error_location))
                                    key = ''

                            elif key == '\r':
                            #enter key often associated
                            #with submit data
                            #so therefore break loop
                               
                                if len(name)>2:
                                    name = "".join(name)
                                    #remove enter name message to make
                                    #room for uname and hscore
                                    pygame.draw.rect(screen,(ERR_COLOR),([100,550,600,25]))    
                                    titleSound.stop()
                                    return name.title()
                                
                                else: pass                   


                            elif len(name) > 15:
                                                                            
                                    # this is a messy cover up for the fact 
                                    # pygame cannot remove drawn rects
                                    pygame.draw.rect(screen,(ERR_COLOR),([100,550,400,25]))
                                    #make_message("Cannot be more than 15 characters!",(255,0,0),15,(error_text_location))
                                    return get_input(name)                          
                                    

                            elif key == ' ':
                                #underscore to replace space
                                #so can be handled in textfile
                                    name.append('_')

                            else:
                                    name.append(key)
                            try:
                                 if name[0] == str("_"):
                                      name = name[1:]
                            except IndexError:
                                 pass
                              
                            try:
                                    #try to displa inputted ke on interface
                                    pygame.draw.rect(screen,(ERR_COLOR),(error_location))
                                    name_string =  "".join(name)
                                    make_message("Please Enter A Username:  "+name_string.title(),(WHITE),15,location)

                                    #time.sleep(2)
                            except TypeError:
                                    #ocuurs when name array is empty
                                    make_message("Please Enter A Username:  ",(WHITE),15,location)
                                    #time.sleep(2)

    #should not be triggered but
    #good form to include
    name = "".join(name)
    return name

########################## END FROM MAIN LOOP SUBS ######################

#event loop, stops window from closing

def main_loop():
    """
        The Heart of the game:
            Runs contniously untill player or AI wins or
            untill user quits. Handles user and AI go as
            well as checks to see if instructions have
            been pressed. 
    """
    running = True
    press_quit = True

    gamePlay_sound.play(-1)
    
    while running == True and user_sunk !=sum(num_to_generate) and enemy_sunk_ships !=sum(num_to_generate) and clock.tick(30):
        for event in pygame.event.get():

            press_instructions(event) 
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                #########print()
                #########print("MOUSE CLICK")
                '''
                Checks if position of fleet on map has been clicked by mouse.
                returns true if mouse touches fleet
                '''

                #if selected coord on board
                if event.pos[0] in range(102,461) and event.pos[1] in range(180,535):
        
                
                    ' PLAYER TURN '                    
                    
                    ##print(event.pos)
                    col = (event.pos[0] -C)  // ((WIDTH + MARGIN))
                    row = (event.pos[1] -C2) // ((HEIGHT + MARGIN))

                    #quick check to make sure user click board
                    try:
                        if sea_board[row][col] in [0,1]:
                            check_user_event(event.pos)
                            #press_instructions(event.pos)

                            ' END PLAYER TURN '
                            
                            update_interface()
                            
                            ' COMPUTER TURN '
                            
                            #Call AI_process when user has selected tile on board
                            if user_sunk < sum(num_to_generate):
                                update_kb()
                                #set selection of vars
                                aiturn = ai_guess()
                                check_ai_event(aiturn[0],aiturn[1])

                                #for row in enemy_board: ###print(row)
                                
                                                          
                                ' END COMPUTER TURN '
                                
                                update_interface()

                    except IndexError:
                        pass

            elif event.type == pygame.QUIT:
                #break loop
                running = False
                press_quit = running
                return press_quit
                    
            else: pass

        update_interface()

    return press_quit





                        ### END OF GAME SUBS ###

def player_win():
    """
        If player win the display screen
        show game stats and save highscore
        if necessary.
    """
    
    global name
    global time2
    time2 = round(time.clock())
   
    #clear screen#
    #pygame.draw.rect(screen,(colour),([0,0,screen_width//,screen_height+100]))
    #pygame.display.flip()
    font_size = 20

    #cover for stats
    bk_img = pygame.image.load("show_stats.png").convert_alpha()
    screen.blit(bk_img,(0,0,))
    
	#you win
    location = [(screen_width//2 ),screen_height//4]
    make_message("YOU WIN!",GREEN,40,location,centre=True)
    
    highscore = get_highscore(name)
    if score> highscore:
        display_highscore = score
    else:
        display_highscore = highscore
    
    #message stats
    location = [screen_width//2-150,screen_height//3]
    make_message("----- <Game Stats> ------",WHITE,font_size,location)
    
    location = [screen_width//2-150,screen_height//3 +20]
    make_message("Score:                "+str(score),WHITE,font_size,location)
    
    location = [screen_width//2-150,screen_height//3 +40]
    make_message("Highscore:            "+str(display_highscore),WHITE,font_size,location)
    
    location = [screen_width//2-150,screen_height//3 +60]
    #print(time2,time1)
    make_message("Elapsed Time:         "+str(int(round(time2-time1,0)))+str("s"),WHITE,font_size,location)
	
    #var messages
    location = None
	
	#play again button
	
    #bk_img = pygame.image.load("play_again.bmp").convert_alpha() 
    #screen.blit(bk_img,(540,screen_height//2+100))

    font_size = 18
    if score> get_highscore(name):
            message = "You beat your highscore!"
            message2 = ""

            save_highscore(name,score)
            
            location = [(screen_width//2)-170,screen_height//2]
    elif (score > (get_highscore(name)*0.9)):
            
            message = "You almost beat your"
            message2 = "highscore why not try again!"
    else: 
            
            message = "Play again to try beat your"
            message2 = "highscore!"
    
    if location:
            make_message(message,WHITE,font_size,location,centre=True)
    else:
            location = [( (screen_width//2) -150 ),  ( (screen_height//3) +100)]
            make_message(message,WHITE,font_size,location,centre=True)

            location2 = [( (screen_width//2) -150 ),  ( (screen_height//3) +120)]
            make_message(message2,WHITE,font_size,location2,centre=True)     
            
    return end_game_menu()

def end_game_menu():
    global name
    global time2
    
    font_size = 22
    message1 = "<Play Again>"
    location1 = [473,410] 
    make_message(message1,WHITE,font_size,location1)

    message2 = "<Leaderboard>"
    location2 = [644,410] 
    make_message(message2,WHITE,font_size,location2)

    message3 = "<Sign Out>"
    location3 = [473,470] 
    make_message(message3,WHITE,font_size,location3)

    message4 = "<Quit>"
    location4 = [644,470] 
    make_message(message4,WHITE,font_size,location4)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                if event.pos[0] >= (screen_width-145) and event.pos[1] >= (screen_height-45):
                    COLOR = YELLOW
                else:
                    COLOR = WHITE
            
                pygame.draw.rect(screen,BLACK,([screen_width-150,screen_height-50,150,50]))
                make_message("<HELP!>",COLOR,30,[screen_width-145,screen_height-45])
            
                if event.pos[0] in range(location1[0],(location1[0]+140) ) and event.pos[1] in range(location1[1],(location1[1]+20)):              
                    make_message(message1,YELLOW,font_size,location1)
                else:
                    make_message(message1,WHITE,font_size,location1)
                    
                if event.pos[0] in range(location2[0], (location2[0]+200) ) and event.pos[1] in range(location2[1],location2[1]+20):
                    make_message(message2,YELLOW,font_size,location2)
                else:
                    make_message(message2,WHITE,font_size,location2)
                    
                if event.pos[0] in range(location3[0],(location3[0]+150) ) and event.pos[1] in range(location3[1],location3[1]+20):
                    make_message(message3,YELLOW,font_size,location3)
                else:
                   make_message(message3,WHITE,font_size,location3)
                    
                if event.pos[0] in range(location4[0], (location4[0]+100) ) and event.pos[1] in range(location4[1],location4[1]+20):
                    make_message(message4,YELLOW,font_size,location4)
                else:
                    make_message(message4,WHITE,font_size,location4)
            
            
            if event.type == pygame.QUIT:
                pygame.quit()
                return False 
            elif event.type == pygame.MOUSEBUTTONDOWN:
                ##print(event.pos) 
                press_instructions(event)
                ##print(event.pos)
                if event.pos[0] in range(location1[0],location1[0]+150) and event.pos[1] in range(location1[1],location1[1]+20):
                    #play again
                    #pygame.draw.rect(screen,(colour),([463,150,355,360]))
                    return True
                
                elif event.pos[0] in range(location2[0], (location2[0]+200) ) and event.pos[1] in range(location2[1],location2[1]+20):
                    #lview eadeboard
                    
                    display_leaderboard(name)
                    
                    bk_img = pygame.image.load("new_background.bmp").convert_alpha() 
                    screen.blit(bk_img,(0,0))
                    if user_sunk == sum(num_to_generate):
                        return player_win()
                    else:
                        return player_loose()
                    
                elif event.pos[0] in range(location3[0],location3[0]+150) and event.pos[1] in range(location3[1],location3[1]+20):
                    #switch user
                    name = get_input()
                    return True
                elif event.pos[0] in range(location4[0],location4[0]+100) and event.pos[1] in range(location4[1],location4[1]+20):
                    pygame.quit()
                    return False
                else: pass
				
            else: pass

def player_loose():
    """
        If player looses the display screen
        show game stats and save highscore
        if necessary.
    """
    global name
    global time2
    time2 = round(time.clock())
    #clear screen#
    #pygame.draw.rect(screen,(colour),([0,0,screen_width//,-screen_height+100]))
    pygame.display.flip()

    bk_img = pygame.image.load("show_stats.png").convert_alpha()
    screen.blit(bk_img,(0,0))
    
	#you win 
    location = [screen_width//2-150,screen_height//4]
    make_message("DEFEATED!",RED,40,location,centre=True)
    
    #message stats
    font_size = 20
    
    location = [screen_width//2-150,screen_height//3]
    make_message("----- <Game Stats> -----",WHITE,font_size,location)
    
    location = [screen_width//2-150,screen_height//3 +20]
    make_message("Score:                "+str(score),WHITE,font_size,location)
    
    location = location = [screen_width//2-150,screen_height//3 +40]
    make_message("Highscore:            "+str(get_highscore(name)),WHITE,font_size,location)
    
    location = location = [screen_width//2-150,screen_height//3 +60]
    make_message("Elapsed Time:         "+str(int(round(time2-time1,0)))+str("s"),WHITE,font_size,location)
	
    #var messages
    location = None
	
    #play again button
	
    #bk_img = pygame.image.load("play_again.bmp").convert_alpha() 
    #screen.blit(bk_img,(540,screen_height//2+100))

    font_size = 18    
    if score> get_highscore(name):
            message = "You beat your highscore!"
            message2 = "You also lost so it will"
            message3 = "not be saved this time!"
            message4 = " "

            #save_highscore(name,score)
            #location = [(screen_width//2)-170,screen_height//2]
            
    elif (score > (get_highscore(name)*0.9)):
            
            message = "That wasnt too bad..."
            message2 = "but you've done better"
            message3 = None
            message4 = None
    else: 
            
            message = "OUCH hard luck!"
            message2 = "You only lost to a robot."
            message3 = "You will clearly not survive "
            message4 = "the future. Good luck. "
    
    if location:
            make_message(message,WHITE,font_size,location,centre=True)
    else:
            location = [( (screen_width//2) -150 ),  ( (screen_height//3) +100)]
            make_message(message,WHITE,font_size,location,centre=True)

            location2 = [( (screen_width//2) -150 ),  ( (screen_height//3) +120)]
            make_message(message2,WHITE,font_size,location2,centre=True)

            if message3 and message4:
                location3 = [( (screen_width//2) -150 ),  ( (screen_height//3) +140)]
                make_message(message3,WHITE,font_size,location3,centre=True)

                location4 = [( (screen_width//2) -150 ),  ( (screen_height//3) +160)]
                make_message(message4,WHITE,font_size,location4,centre=True)
    return end_game_menu()

    

def calculate_score(scen=0):
    '''calculates score based on
       num guesses to sink ship.
       if player takes too many guesses
       then deduct points. Stops spam.
    '''
    
    global score
    #print(clicked)
    #time.clock is float we want whole num
    #Time = round(time.clock(),0)
    if score <250:
        if clicked <=4:
            if scen == 2:
                score+= (500*scen)
            else:
                score += 50*scen
        elif clicked <=5:
            score += (45*scen)
        elif clicked <=6:
            score += (30*scen)
        elif clicked <=7:
            score += (20*scen)
        elif clicked <=6:
            score += (10*scen)
        elif clicked <=9:
            score += (5*scen)
        #loose points if too many hits
        elif clicked > 9 and score >100 and scen !=2:
            score += (-100*scen)
        else:
            score += (2*scen)
            
    elif score <1200:
        if clicked <=4:
            if scen ==2:
                score += (400*scen)
            else:
                score+= (60*scen)
        elif clicked <=5:
            score += (50*scen)
        elif clicked <=6:
            score += (40*scen)
        elif clicked <=8:
            score += (30*scen)
        elif clicked >=9 and scen !=2:
            score += (-200*scen)
        else:
            score += 20
            
    elif score in range(1200,2500):
        if clicked <=4:
            if scen ==3:
                score += (300*scen)
            else:
                score+= (70*scen)
        elif clicked <=5:
            score += (60*scen)
        elif clicked <=7:
            score += (50*scen)
        elif clicked >7 and scen !=2:
            score += (-250*scen)
        else:
            score += 20
    else:
        if clicked <=3:
            if scen ==2:
                score += (800*scen)
            else:
                score+= (100*scen)
        elif clicked <=6:
            score += (80*scen)
        elif clicked >6 and scen !=2:
            score += (-300*scen)
        else:
            score += 20
            
    if enemy_sunk_ships <2 and scen ==2 and clicked <=5:
        bonus = 250
        
    elif enemy_sunk_ships <6 and scen ==2 and clicked<=7:
        bonus = 100
    elif enemy_sunk_ships <10 and scen ==2 and clicked <=7:
        bonus = 25
    else:
        bonus = 0
    
    score += bonus

    #show new score on screen live
    update_score_display(score)

    #update highscore live
    if score > get_highscore(name):
        update_highscore_display(score)
    
    

def update_highscore_display(score):
    
    #remove old highscore
    location = [100,550]
    pygame.draw.rect(screen,(BLACK),([location[0],location[1],200,20]))
    pygame.display.flip()

    #display highscore on interface
    make_message("Highscore: "+str(score),(WHITE),20,location)


def update_score_display(score):

    #remove old score
    location = [100,575]
    pygame.draw.rect(screen,(BLACK),([location[0],location[1],200,30]))
    pygame.display.flip()

    #display score on interface
    make_message("Score: "+str(score), (WHITE),20,location)
    
    
def runGame():

    """
        Allows for the user to play multiple times
        in a row as well as change username.

        everytime looped: resets 'session' variables
        and interface 
    """

    #all these arrays are global
    #as they have values being
    #changed
    global sea_board
    global enemy_board
    global user_sunk
    global enemy_sunk_ships
    global ai_ship_guess
    global first_loop   
    global score
    global time1
    
    run = True
    while run == True:

         #reset vars
        score = 0
        
        if first_loop != True:
            bk_img = pygame.image.load("new_background.bmp").convert_alpha() 
            screen.blit(bk_img,(0,0))
            
            pygame.display.flip()
            
        else:
            
            first_loop = False
            

        ### Add labels ###
        

        board_back = pygame.image.load('board_bk.png').convert_alpha()
        screen.blit(board_back,(0,0))

        #load instructions button
        instructions()
        
        #Display enemy territory label 
        location = [(MARGIN + WIDTH)+C-30 ,C2-HEIGHT//2 -MARGIN ]
        make_message("Enemy Territory",(YELLOW),25,location)

        #display username on interface
        #location = [( ( screen_width//2 ) + ( ( screen_width//2-100 ) //6 ) -( len(name)*2) -100 ) ,( screen_height//screen_height+100 )]
        location = [(screen_width//2) + (screen_width//4)-135,Ce2-HEIGHT//2 -MARGIN]
        make_message(name+"'s Territory",(YELLOW),22,location)
        
        #load in highscore
        update_highscore_display( get_highscore( name ) )

        #user starts with no score
        update_score_display(score)
        
        ai_ship_guess.knowledge_base = []
        user_sunk = 0
        enemy_sunk_ships = 0

        time1 = round(time.clock(),0)
        #print('time1',time1)
        counter_init = 0
        
        # Creates interactive sea grid #
        sea_board = make_sea_grid(screen)
        sea_board = generate_fleets(sea_board,num_to_generate)
        
        # Creates enemy sea grid #
        enemy_board = make_sea_grid(screen)
        enemy_board = generate_fleets(enemy_board,num_to_generate)

        #places sea_board onto display
        while counter_init<=1 and clock.tick(30):
            update_interface()
            counter_init+=1
        #update_interface() #call 2nd time, temp bug fix
    
        
        #<--- Call Mainloop --->
        #returns true or false
        if  main_loop():
            ##print(user_sunk)
            gamePlay_sound.stop()
            pass
        else: run = False

        #decide what gameover screen to display
        if user_sunk == sum(num_to_generate):
            playerWin_sound.play(-1)
            run = player_win()

            #when quit is pressed all pygame objects are destroyed
            #this can raise error for trying to stop media objects
            try:
                playerWin_sound.stop()
            except pygame.error:
                pass
            
        elif enemy_sunk_ships == sum(num_to_generate):
            playerLoose_sound.play(-1)
            run = player_loose()
            try:
                playerLoose_sound.stop()
            except pygame.error:
                pass

        #else means player has quit game
        else: run = False



################################## MAIN PROGRAM #################################



            ### Initialise Display ###
'''
    The display must be initlaised before
    sptites or errors will occur
'''

screen = screen_size(screen_width,screen_height)
prefrences(screen)
set_title('BattleFleets')

                ### Initialise sprites ###

#-------------------------------------------------------
#                 sprite image array                   #
#0 = water [M]                                         #
#1 = miss  [0]                                         #
#2 = show  [1]                                         #
#3 = hit   [2]                                         #
#4 = sunk  [3]                                         #
#                                                      #
sprite = makeSprite("water.bmp")                       #
sprite.addImage("miss.bmp")                            #
sprite.addImage("ship.bmp")                            #
sprite.addImage("shipdamaged.bmp")                     #
sprite.addImage("shipsunk.bmp")                        #
#-------------------------------------------------------

instructions()
#get users username
name = get_input()

#sets rest of game up
runGame()

#close window without raising errors
pygame.quit()
