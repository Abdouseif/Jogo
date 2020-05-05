# Imports
import numpy as np
np.set_printoptions(suppress=True)
from shutil import copyfile
import random
import time
from importlib import reload
from game import Game, GameState
from agent import Agent
from funcs import playMatches
import initialise
import pickle
import config
from client import *
import ctypes
import logging
import threading
from typing import List
import ctypes
import go
import asyncio
import math
import pygame
from sys import exit
from gui import *
BACKGROUND = 'images/go.jpg'
STARTBG='images/dest.jpg'
STARTBGP='images/destp.jpg'
AIBG='images/ai.jpg'
AIBGP='images/aip.jpg'
BRAIN='images/brain.png'
BRAINP='images/brainp.png'
PASS='images/pass.jpg'
BLACKBG='images/black.png'
WHITEBG='images/white.jpg'
BOARD_SIZE = (820, 820)
SCREEN_SIZE = (1200,820)
WHITE = (220, 220, 220)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0) 
BLUE = (0, 0, 128)
RED=(255,0,0)
#BGC=(246,232,174)
BGC=(255,255,255)



GameInfo = GameServer()
def initialboard():
    board=[]
    f=open("gui4.txt", "w")
    f.write("0\r\n" )
    GameInfo.board = np.zeros([19,19])
    for i in range(19):
        for j in range(19):
            if GameInfo.board[i][j]=="B":
                board.append(1)
            elif GameInfo.board[i][j]=="W":
                board.append(-1)
            else:
                board.append(0)
    board.append(0)
    board.append(0)
    return board
    
def initialdboard(iboard):
    board=[]
    for r in range(19):
        row=[]
        for c in range(19):
            row.append(iboard[r*19+c])
        board.append(row)
    return np.array(board)



def theend(gboard):
    score=(str(GameInfo.score["W"]),str(GameInfo.score["B"]))
    guiboard.updateMsg("","GAME ENDED",RED)
    gboard.updateScoreMsg(score)
    


async def main():
    #initialize game
    global GameInfo
    env = None
    gamepos = None
    mode=-1
    playerColor=""
    oppcolor=""
    playerName="JoGo"
    playerTurn=0
    action=0
    sc=[0,0,0]
    ai = None
    chosen=-1

    while mode==-1:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x = event.pos[0]
                    y = event.pos[1]
                    if x>865 and x<965 and y>50 and y<150:
                        if chosen==-1 or chosen==1:
                            chosen=0
                            guiboard.startmenu(startbg,aibgp,brain)
                        else:
                            chosen=-1
                            guiboard.startmenu(startbg,aibg,brain)
                    if x>1048 and x<1148 and y>50 and y<150:
                        if chosen==-1 or chosen==0:
                            chosen=1
                            guiboard.startmenu(startbg,aibg,brainp)
                        else:
                            chosen=-1
                            guiboard.startmenu(startbg,aibg,brain)
                    
                    if x>910 and x<1096 and y>200 and y<400:
                        if chosen==-1:
                            guiboard.updateMsg("","Choose the mode first!",RED)
                        else:
                            guiboard.startmenu(startbgp,aibg,brain)
                            mode=chosen
                    
                            
    if mode==0:
        print("AI vs AI")
        turn = 0
        game_start = time.time()
        perv_turn = time.time()
        GameInfo.State = States.INIT
        
        while(1):
            if GameInfo.endgame==True:
                theend(guiboard)
            #guiboard.updateMsg("","Waiting for server")
            # print(type(GameInfo.RemainTime))
            # print(GameInfo.score)
           
            if GameInfo.State == States.INIT:
                guiboard.updateMsg("","Initialized",RED)
                await InitState(GameInfo, playerName)
            elif GameInfo.State == States.READY:
                await ReadyState(GameInfo)
                playerColor=str(GameInfo.PlayerColor)
                print(playerColor)
                guiboard.updateMsg("","Iam Ready!",RED)
                if GameInfo.endgame==False:
                        board = initialboard()
                        if playerColor=="b" or playerColor=="B" or playerColor=="black" or playerColor=="BLACK":
                            oppcolor="W"
                            playerTurn=1
                        else:
                            oppcolor="B"
                            playerTurn=-1
                        
                        if env is None:
                            env = Game(board, 1)
                            env.gameState.render()
                            ai = Agent('current_player', env.state_size, env.action_size, config.MCTS_SIMS, config.CPUCT)
                            gamepos = go.Position(board=initialdboard(board))
                else:
                    theend(guiboard)
            
                

                
            elif  GameInfo.State == States.IDLE:
                await IdleState(GameInfo)
                action = None
                baction = None
                if GameInfo.getOppMove(0)==-1:
                    if playerColor=="B":
                        action=362
                    else:
                        action=361
                elif GameInfo.getOppMove(0)==-2:
                    pass
                else:
                    baction = (int(GameInfo.getOppMove(0)),int(GameInfo.getOppMove(1)))
                    action=int(GameInfo.getOppMove(0))*19+int(GameInfo.getOppMove(1))
                gamepos = gamepos.play_move(baction, env.gameState.playerTurn, mutate=True)
                env.step(action)
                turn = turn + 1  
                this_turn = time.time()
                print()
                print()
                print()
                print("************************* TURN: ", turn," *************************")
                print("This turn took ", (this_turn-perv_turn)/60, " mins")
                print("It has been ", (this_turn-game_start)/60, " mins from the start of the game") 
                env.gameState.render()
                env.gameState.renderThink(guiboard)


            elif  GameInfo.State == States.THINK:
                
                action, gamepos=ai.act(gamepos, env.gameState, turn)
                print(gamepos.score())
                typ=0
                if action==361:
                    typ=1
                elif action==362:
                    typ = 1
                else:
                    typ=0
                    y =  action % 19
                    x =  math.floor(action / 19)
                
                
                await ThinkState(GameInfo, x,y,typ)
                if GameInfo.validmove==True:
                    env.step(action)
                turn = turn + 1  
                this_turn = time.time()
                print()
                print()
                print()
                print("************************* TURN: ", turn," *************************")
                print("This turn took ", (this_turn-perv_turn)/60, " mins")
                print("It has been ", (this_turn-game_start)/60, " mins from the start of the game") 
                env.gameState.render()
                env.gameState.renderWait(guiboard)



    if mode==1:
        pygame.draw.rect(guiboard.screen, BGC,(820,0,1200,500))
        pygame.draw.rect(guiboard.screen, BGC,(820,500,1200,820))
        guiboard.screen.blit(blackbg, (865, 50))
        guiboard.screen.blit(whitebg, (1048, 50))
        guiboard.updateMsg("","Choose your color!",RED)
        pygame.display.update()
        usercolor=""
        while usercolor=="":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x = event.pos[0]
                        y = event.pos[1]
                        if x>865 and x<965 and y>50 and y<150:
                            usercolor="BLACK"
                        if x>1048 and x<1148 and y>50 and y<150:
                            usercolor="WHITE"
        pygame.draw.rect(guiboard.screen, BGC,(820,500,1200,820))
        guiboard.updateMsg("","Its Your Turn",RED)
        while(True):
            useraction=guiboard.getUserAction(passbg,usercolor)
            guiboard.updateMsg(str(useraction),usercolor,RED)

    #     player = User('player', env.state_size, env.action_size)
    #     if playerColor=="B":
    #         playMatches(player, ai, EPISODES=0, lg.logger_main, turns_until_tau0 = config.TURNS_UNTIL_TAU0, memory = None, goes_first = 1)
    #     else:
    #         playMatches(ai, player, EPISODES=0, lg.logger_main, turns_until_tau0 = config.TURNS_UNTIL_TAU0, memory = None, goes_first = 1)

            
  
    
if __name__== "__main__":
    pygame.init()
    pygame.display.set_caption('Jogo')
    screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
    background = pygame.image.load(BACKGROUND).convert()
    guiboard = Board(screen,background)
    startbg=pygame.image.load(STARTBG).convert()
    startbgp=pygame.image.load(STARTBGP).convert()
    aibg=pygame.image.load(AIBG).convert()
    brain=pygame.image.load(BRAIN).convert()
    aibgp=pygame.image.load(AIBGP).convert()
    brainp=pygame.image.load(BRAINP).convert()
    passbg=pygame.image.load(PASS).convert()
    blackbg=pygame.image.load(BLACKBG).convert()
    whitebg=pygame.image.load(WHITEBG).convert()
    #guiboard.startmenu(startbg)
    guiboard.startmenu(startbg,aibg,brain)
    asyncio.get_event_loop().run_until_complete(main())

