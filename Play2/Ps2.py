import pygame
import numpy as np
# Turtoriales
# 
#https://pythonhosted.org/triangula/sixaxis.html (pairing)
#http://wiki.ros.org/ps3joy/Troubleshooting
pygame.init()
pygame.joystick.init()

joystick = pygame.joystick.Joystick(0)
joystick.init()

print ('Initialised Joystick : %s' % joystick.get_name())
print ('Press ESC to stop')

screen = pygame.display.set_mode((100,100))

# get count of joysticks=1, axes=27, buttons=19 for DualShock 3

joystick_count = pygame.joystick.get_count()
print("joystick_count")
print(joystick_count)
print("--------------")

numaxes = joystick.get_numaxes()
print("numaxes")
print(numaxes)
print("--------------")

numbuttons = joystick.get_numbuttons()
print("numbuttons")
print(numbuttons)
print("--------------")

loopQuit = False


button = np.zeros(numbuttons, dtype = int)
axis = np.zeros(numaxes, dtype = float)

while loopQuit == False:


# test joystick axes
        for i in range(0,numaxes):
                pygame.event.pump()
                axis_now= float(joystick.get_axis(i))
                if axis_now != axis[i]:
                    axis[i] = axis_now
                    if i != 5 and i != 6:
                        print("Axis " + str(i) + " = " + str(axis[i]))
        #print("--------------")

# test controller buttons
        for i in range(0,numbuttons):
                pygame.event.pump()
                button_now= int(joystick.get_button(i))
                if button_now != button[i]:
                    button[i] = button_now
                    if i!= 0 and i!=4:
                        print("Button " + str(i) + " = " + str(button[i]))
        #print("--------------")
        
# quit if escape pressed
        for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        loopQuit = True

        pygame.display.update()

pygame.quit()
