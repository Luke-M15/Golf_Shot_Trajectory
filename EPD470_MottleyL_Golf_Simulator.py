# -*- coding: utf-8 -*-
"""
Luke Mottley
EPD 470 Final Project - Golf Simulator
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

 # unit conversions
oz2g = 28.3495
in2m = .0254
mph2mps = .44704
m2yd = 1.09361


def clubSelection(df):
    club = input('What club would you like to use? ')
    
    while club.lower() not in df.index:
        print('The club you selected is not avalaible.')
        club = input('Please select Driver, 3 Wood, Hybrid, 4-9 Iron, PW, GW, SW, LW or q to quit. ')
        if club == 'q':
            break
    
    loft = df['Loft (deg)'].loc[club]
    length = df['Length (in)'].loc[club]
    mass = df['Mass (g)'].loc[club]
    v = df['Average Swing Speed (mph)'].loc[club]
    
    return club, loft, length, mass, v
    
    
        

def initial_launch(club,loft,length,mClub,vSwing,mBall,include_miss = False):
    
    if include_miss:
        #TODO: add some randomization for the miss factor
        pass
    else:
        miss = 0
    
    #TODO: could just add e factor to club data sheet
    if club.lower() in ['driver',' 3 wood']:
        e = .83
    elif club.lower() == 'hybrid':
        e = .8
    else:
        e = .78
   
    #TODO: use club length to get club head speed, vSwing could be hand speed or something    
    vClub = vSwing
        
    vBall = vClub*((1+e)/(1+mBall/mClub))*np.cos(np.deg2rad(loft))*(1-.14*miss)  #mph
    vBall *= .44704     # convert ball speed to m/s, club speed in mph for spin equation
    alpha = loft*(.96-.0071*loft)  #degrees
    omega = 160*vClub*np.sin(np.deg2rad(loft))    #rpm
    omega *= .1047   # convert rpm to rad/sec
    
    return vBall, alpha, omega

def calc_flight(v,alpha,omega,r,rho,dt,cd,m,g,spin_decay,x=0,maxIter = 10000):
     
    cols = ['t','x','y','V','Vx','Vy','Ax','Ay','alpha','alpha2','omega']
    m /= 1000       # convert the ball mass from g to kg
    s_decay = 1-spin_decay*dt
    t = 0
    y = 0
    alpha = np.deg2rad(alpha)
    vx = v*np.cos(alpha)
    vy = v*np.sin(alpha)
    alpha2 = alpha
    i = 0
    position_list = []
    while y  > -.00001:    
             
        ax = (-.5*np.pi*rho*r**3*v*omega*np.sin(alpha)
              -.5*np.pi*rho*r**2*v**2*cd*np.cos(alpha))/m
     
        ay = (.5*np.pi*rho*r**3*v*omega*np.cos(alpha)
              -.5*np.pi*rho*r**2*v**2*cd*np.sin(alpha)-m*g)/m
    
        position_list.append([t,x,y,v/mph2mps,vx,vy,ax,ay,np.rad2deg(alpha),np.rad2deg(alpha2),omega])
    
        t = t+dt
        x = x + vx*dt
        y = y + vy*dt
        omega *= s_decay
        vx = vx + ax*dt
        vy = vy + ay*dt
        v = np.sqrt(vx**2+vy**2)
        alpha = np.arctan2(y,x)
        alpha2 = np.arctan(vy/vx)
        i+=1
        if i > maxIter:
            print('reached iteration limit')
            break
     
    
    df = pd.DataFrame(position_list,columns = cols)
    df.set_index('t',inplace=True)
    
    return df

#def plot_hole(df_list,hole_Length):
    

if __name__ == "__main__":    
    # constants
    r = 1.68*in2m    # m, radius of golf ball 
    rho = 1.225     # kg/m^3, density of air, standard atmosphere
    g = 9.81        # m/s^2, gravitational acceleration
    dt = .01        # s, time step 
    cd = .18        # coefficient of drag for golf ball
    spin_decay = .033   # %/sec, the decay rate of the ball spin
    mBall = 1.62*oz2g   #gram, mass of golf ball
        
    # golf club data file
    df_clubs = pd.read_csv(r'C:\Users\motts\Documents\Grad School\BoxSync\EPD 470\Final Project\Golf_CLub_data.csv', index_col = 'Club')
    vSwing = 80     #mph, swing speed
    
    
    
    #TODO: randomize the direction of the wind and the speed of the wind
    
    dis2green = np.random.randint(150,600)
    holeLength=200
    print('The hole is {} yards long'.format(holeLength))
    dis2green = holeLength
    x=0
    flight_list = []
    '''
    while dis2green > 0:
        # ask user to select a club
        club, loft, length, mClub, vSwing = clubSelection(df_clubs)
    
        # initial launch conditions, ball speed in m/s, angle in degrees and spin in rad/sec
        vBall, alpha, omega = initial_launch(club,loft,length,mClub,vSwing,mBall)
    
        #calulate the ball's flight
        df_flight = calc_flight(vBall,alpha,omega,r,rho,dt,cd,mBall,g,spin_decay,x)
        x = df_flight['x'].iloc[-1]
        dis2green = holeLength - x*m2yd
        df_flight.x *= m2yd
        df_flight.y *= m2yd
        flight_list.append(df_flight)
        if dis2green < -20:
            print('Your shot went over the green and into the pond!!!! \n Try Again.')
            break    
        elif (dis2green < 0 and dis2green >= -20):
            print('You made it on the green!!! Nice Job!!!')
        else:
            print('Next shot. \n You are {:.4} yd from the green'.format(dis2green))
    '''            
    # ask user to select a club
    club, loft, length, mClub, vSwing = clubSelection(df_clubs)

    # initial launch conditions, ball speed in m/s, angle in degrees and spin in rad/sec
    vBall, alpha, omega = initial_launch(club,loft,length,mClub,vSwing,mBall)

    #calulate the ball's flight
    df_flight = calc_flight(vBall,alpha,omega,r,rho,dt,cd,mBall,g,spin_decay,x)
    x = df_flight['x'].iloc[-1]
    dis2green = holeLength - x*m2yd
    df_flight.x *= m2yd
    df_flight.y *= m2yd
    plt.close('all')
    
    fig1, ax1 = plt.subplots()
    df_flight.plot(x='x',y='y', ax=ax1)
    ax1.set_xlabel('X position (yd)')
    ax1.set_ylabel('Y position (yd)')
    ax1.set_xbound(lower = 0)
    ax1.set_ybound(lower = 0)
    
    fig2, ax2 = plt.subplots(2,2,sharex='col')
    df_flight.plot(y='Vx', ax=ax2[0,0])
    ax2[0,0].set_ylabel('Vx (m/s)')
    ax2[0,0].grid(True)
    df_flight.plot(y='Vy', ax=ax2[1,0])
    ax2[1,0].set_ylabel('Vy (m/s)')   
    ax2[1,0].set_xlabel('time (sec)')
    ax2[1,0].grid(True)
    df_flight.plot(y='Ax',ax=ax2[0,1])
    ax2[0,1].set_ylabel('Ax (m/s^2)')
    ax2[0,1].grid(True)
    df_flight.plot(y='Ay',ax=ax2[1,1])
    ax2[1,1].set_ylabel('Ay (m/s^2)')
    ax2[1,1].set_xlabel('time (sec)')
    ax2[1,1].grid(True)
    
    
    
    
    
        