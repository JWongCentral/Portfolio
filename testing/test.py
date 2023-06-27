
def glowEffect(x,y,color,iteration,rate):
    #5%{box-shadow: 0 0 6.5px 6.5px #0ff;}
    for i in range(iteration):
        print("5%{box-shadow: 0 0 " + str(x+i*rate) + "px " + str(y+i*rate) + "px "+ color )
    
    for i in range(iteration,0,-1):
        print("5%{box-shadow: 0 0 " + str(x+i*rate) + "px " + str(y+i*rate) + "px "+ color )