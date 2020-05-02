# Imports
import numpy as np
np.set_printoptions(suppress=True)
from shutil import copyfile
import random
from importlib import reload
from keras.utils import plot_model
from game import Game, GameState
from agent import Agent
from memory import Memory
from model import Residual_CNN
from funcs import playMatches, playMatchesBetweenVersions
import loggers as lg
from settings import run_folder, run_archive_folder
import initialise
import pickle
import config
import clients
def initialboard():
    board=[]
    f=open("gui4.txt", "w")
    f.write("0\r\n" )
    for i in range(19):
        for j in range(19):
            if GameInfo.board[i][j]=="B":
                board.append(1)
            elif GameInfo.board[i][j]=="W":
                board.append(-1)
            else:
                board.append(0)
           
    return board

def theend():
    f=open("gui4.txt", "w")
    f.write("1\r\n" )
    f.write("B %d \r\n" %GameInfo.score["B"])
    f.write("W %d \r\n" %GameInfo.score["W"])


def main():
    #initialize game
    env = Game()
    mode=-1
    playerColor=""
    oppcolor=""
    playerName="JoGo"
    playerTurn=0
    action=0
    sc=[0,0,0]
    

    ai = Agent('current_player', env.state_size, env.action_size, config.MCTS_SIMS, config.CPUCT)
    while mode==-1:
        f=open("gui3.txt", "r")
        f1=f.readlines()
        j=0
        for i in f1:
            if j==0:
                #if mode =0 --> AI Vs AI else mode=1--> AI VS User
                mode=int(i)
            if j==1:
                #PlayerNum=0 --> black(player1) 1--> white(player2)
                playerColor=str(i)
            j=j+1
        
    
    if mode==0:
        print("AI vs AI")
        global GameInfo
        
        while(1):
            # print(type(GameInfo.RemainTime))
            # print(GameInfo.score)
            try:
                if GameInfo.State == States.INIT:
                    await InitState(playerName)
                elif  GameInfo.State == States.READY:
                    await ReadyState()
                    playerColor=GameInfo.playerColor

                    if GameInfo.endgame==False:
                         initialboard()
                         if playerColor=="B":
                             oppcolor="W"
                             playerTurn=1
                             env.gameState.playerTurn==1
                         else:
                             oppcolor="B"
                             playerTurn=-1
                             env.gameState.playerTurn==-1
                    else:
                        theend()
                
                    

                    
                elif  GameInfo.State == States.IDLE:
                    await IdleState()
                    if GameInfo.oppmove[0]==-1:
                        if playerColor=="B":
                            xy=362
                            env.gameState.board[xy]=-1
                        else:
                            xy=361
                            env.gameState.board[xy]=1
                    else:
                        xy=GameInfo.oppmove[0]+(GameInfo.oppmove[1]*19)
                        env.gameState.board[xy]=-playerTurn
                    
                    env.gameState.renderThink()


                elif  GameInfo.State == States.THINK:
                    action=ai.act(State=env.gameState,1)
                    typ=0
                    if action==361:
                        env.gameState.board[361]=1
                        typ=1
                    elif action==362:
                        env.gameState.board[361]=-1
                    else:
                        typ=0
                        x =  action % 19
                        y =  action / 19
                    await ThinkState(x,y,typ)
                    env.gameState.renderWait()
            except:
                GameInfo.State = States.INIT


    if mode==1:
        player = User('player', env.state_size, env.action_size)
        if playerColor=="B":
            playMatches(player, ai, EPISODES=0, lg.logger_main, turns_until_tau0 = config.TURNS_UNTIL_TAU0, memory = None, goes_first = 1)
        else:
            playMatches(ai, player, EPISODES=0, lg.logger_main, turns_until_tau0 = config.TURNS_UNTIL_TAU0, memory = None, goes_first = 1)

            
  
    
if __name__== "__main__":
    main()
