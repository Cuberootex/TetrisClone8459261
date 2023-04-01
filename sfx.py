import pygame, os
from random import choice
dir_path = os.path.dirname(os.path.realpath(__file__))
pygame.mixer.init()


def movePieceSound():
    moveFolder = dir_path + "\\sounds\\move"
    """
    print(moveFolder)
    moveFolderContents = [f for f in os.listdir(moveFolder)]
    n = moveFolder + "\\"
    cnt = 0
    for x in moveFolderContents:
        print(x, pygame.mixer.Sound(n + x)._ge)
        cnt += pygame.mixer.Sound(n + x).get_num_channels()
    print(cnt)
    snd = choice(moveFolderContents)
    pygame.mixer.Sound(n + snd).play()
    """