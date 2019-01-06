import pygame

def DrawMatrix(mat, surface, px):
    """print the matrix elements to screen given a pixel size"""
    H, W = len(mat[0]), len(mat)
    #display the matrix
    for y in range(W):
        for x in range(H):
            #surface.set_at((x, y), mat[y][x])
            pygame.draw.rect(surface, mat[y][x], (x*px, y*px, px, px))

def CommitChanges(chg_list, surface):
    for chg in chg_list:
        pygame.draw.rect(surface, chg[1], (chg[0]*px, chg[1]*px, px, px))
