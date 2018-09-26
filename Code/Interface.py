import RPi.GPIO as GPIO 
import time

GPIO.setmode(GPIO.BCM)


class Interface:

  def __init__(self):
    #self.select_pins_ldr=[14,15,18,23]
    self.select_pins_ldr=[15,14,23,18]
    self.select_pins_ldr1=[2,3,4,17][::-1]

    #self.input_data=[24,25,8,7]
    self.input_data=[25,24,7,8]
    #d={25:0,24:1}

    self.select_pins_led=[6,13,19,26]
    self.select_pins_led1=[12,16,20,21]

    self.button=10

    self.indicator_led=9
    
    self.set_pins()

  def set_pins(self):
    for i in self.select_pins_ldr:
      GPIO.setup(i,GPIO.OUT)
      GPIO.output(i,GPIO.LOW)

    for i in self.select_pins_ldr1:
      GPIO.setup(i,GPIO.OUT)
      GPIO.output(i,GPIO.LOW)

    for i in self.input_data:
      GPIO.setup(i,GPIO.IN)

    for i in self.select_pins_led:
      GPIO.setup(i,GPIO.OUT)
      GPIO.output(i,GPIO.LOW)

    for i in self.select_pins_led1:
      GPIO.setup(i,GPIO.OUT)
      GPIO.output(i,GPIO.HIGH)

    GPIO.setup(self.button,GPIO.IN)

    GPIO.setup(self.indicator_led,GPIO.OUT)
    GPIO.output(self.indicator_led,GPIO.LOW)
    
  def set_led_pins_low(self,p1,p2):
    GPIO.output(self.select_pins_led[p2[0]],GPIO.LOW)
    GPIO.output(self.select_pins_led1[p2[1]],GPIO.HIGH)
    GPIO.output(self.select_pins_led[p1[0]],GPIO.LOW)
    GPIO.output(self.select_pins_led1[p1[1]],GPIO.HIGH)
      

  def recieve_data_from_ldr(self,x,y):
    #print(self.select_pins_ldr1[y])
    GPIO.output(self.select_pins_ldr[x],GPIO.HIGH)
    GPIO.output(self.select_pins_ldr1[y],GPIO.HIGH)
    time.sleep(0.1)
    data=GPIO.input(self.input_data[x])
    GPIO.output(self.select_pins_ldr[x],GPIO.LOW)
    GPIO.output(self.select_pins_ldr1[y],GPIO.LOW)
    time.sleep(0.05)
    return data 

  def send_data_to_led(self,p1,p2):
    p1=p1[::-1]
    p1[0]=3-p1[0]
    p2=p2[::-1]
    p2[0]=3-p2[0]
    #count=0
    while True:
        GPIO.output(self.select_pins_led[p2[0]],GPIO.LOW)
        GPIO.output(self.select_pins_led1[p2[1]],GPIO.HIGH)
        GPIO.output(self.select_pins_led[p1[0]],GPIO.HIGH)
        GPIO.output(self.select_pins_led1[p1[1]],GPIO.LOW)
        
        

        t=time.time()
        flag=0
        print(self.read_button())
        while time.time()-t<0.5:
          if self.read_button():
            flag=1
            self.set_led_pins_low(p1,p2)
            break 
        if flag==1:
          break
        
        self.set_led_pins_low(p1,p2)
        time.sleep(0.1)
        
        GPIO.output(self.select_pins_led[p1[0]],GPIO.LOW)
        GPIO.output(self.select_pins_led1[p1[1]],GPIO.HIGH)
        GPIO.output(self.select_pins_led[p2[0]],GPIO.HIGH)
        GPIO.output(self.select_pins_led1[p2[1]],GPIO.LOW)

        t=time.time()
        flag=0
        while time.time()-t<0.5:
          if self.read_button():
            flag=1
            self.set_led_pins_low(p1,p2)
            break 
        if flag==1:
          break
        
        self.set_led_pins_low(p1,p2)
        #count+=1
        #if count==4:
            #break
    time.sleep(2)
          

  def read_button(self):
    if not GPIO.input(self.button)==1:
        return True
    else:
        return False

  def set_indicator_led(self,val):
    if val==1:
      GPIO.output(self.indicator_led,GPIO.HIGH)
    else:
      GPIO.output(self.indicator_led,GPIO.LOW)

  def wait_for_button_to_be_pressed(self):
    while not self.read_button():
      pass 
    self.set_indicator_led(1)
    time.sleep(2)
    


class Board_Handler:

  def __init__(self):
    self.previous_board=None
    self.current_board=None 

  def set_previous_board(self,previous_board):
    self.previous_board=previous_board

  def get_previous_board(self):
    return self.previous_board

  def set_current_board(self,interface,chess):
    self.current_board=[[0 for j in range(4)] for i in range(4)]
    interface.wait_for_button_to_be_pressed()
    oldPosition=None
    x,y=None,None
    for i in range(4):
        print(i,end=" ")
        for j in range(4):
            data=interface.recieve_data_from_ldr(i,j)
            self.current_board[i][j]=data
            print(data,end=" ")
            time.sleep(0.2)
        print("")
        
    previous_count=0
    for i in range(4):
        for j in range(4):
            if self.previous_board[i][j]!=None:
                previous_count+=1
                
    current_count=0
    for i in range(4):
        for j in range(4):
            if self.current_board[i][j]!=0:
                current_count+=1
    print(previous_count,current_count,self.previous_board,self.current_board)
    if previous_count==current_count:
        ans=[]
        for i in range(4):
            for j in range(4):
                if (self.previous_board[i][j]==None)^(self.current_board[i][j]==0):
                    print(self.previous_board[i][j],self.current_board[i][j])
                    if self.previous_board[i][j]!=None and self.current_board[i][j]==0:
                        oldPosition=[i,j]
                    else:
                        x=i
                        y=j
                    ans.append([i,j])
        if len(ans)==2:
            self.previous_board[ans[0][0]][ans[0][1]],self.previous_board[ans[1][0]][ans[1][1]]=self.previous_board[ans[1][0]][ans[1][1]],self.previous_board[ans[0][0]][ans[0][1]]
            self.current_board=self.previous_board
        else:
            print("Wrong Input Repeat")
            return self.set_current_board(interface,chess)
        
            
    elif previous_count-current_count==1:
        ans=[]
        for i in range(4):
            for j in range(4):
                if (self.previous_board[i][j]==None)^(self.current_board[i][j]==0):
                    print(self.previous_board[i][j],self.current_board[i][j])
                    if self.previous_board[i][j]!=None and self.current_board[i][j]==0:
                        oldPosition=[i,j]
                    else:
                        x=i
                        y=j
                    ans.append([i,j])
        if len(ans)==1:
            self.previous_board[ans[0][0]][ans[0][1]]=None
            self.current_board=self.previous_board
            print("Continue the move")
            self.current_board=[[0 for j in range(4)] for i in range(4)]
            interface.wait_for_button_to_be_pressed()
            for i in range(4):
                print(i,end=" ")
                for j in range(4):
                    data=interface.recieve_data_from_ldr(i,j)
                    self.current_board[i][j]=data
                    print(data,end=" ")
                time.sleep(0.2)
                print("")
            ans=[]
            for i in range(4):
                for j in range(4):
                    if (self.previous_board[i][j]==None)^(self.current_board[i][j]==0):
                        print(self.previous_board[i][j],self.current_board[i][j])
                        if self.previous_board[i][j]!=None and self.current_board[i][j]==0:
                            oldPosition=[i,j]
                        else:
                            x=i
                            y=j
                        ans.append([i,j])
            
            if len(ans)==2:
                self.previous_board[ans[0][0]][ans[0][1]],self.previous_board[ans[1][0]][ans[1][1]]=self.previous_board[ans[1][0]][ans[1][1]],self.previous_board[ans[0][0]][ans[0][1]]
                self.current_board=self.previous_board
                
            else:
                print("Wrong Input Repeat")
                return self.set_current_board(interface,chess)
            
        else:
            print("Wrong Input Repeat")
            return self.set_current_board(interface,chess)
        
        
    else:
        print("Wrong Input Repeat")
        return self.set_current_board(interface,chess)
    if not chess.isValid(x,y):
        print("Wrong Input Repeat")
        return self.set_current_board(interface,chess)
    
    print(oldPosition,x,y)
    return oldPosition,x,y

  def get_current_board(self):
    return self.current_board


interface=Interface()

"""
for i in range(4):
    for j in range(4):
        for k in range(4):
            for l in range(4):
                print(i,j,k,l)
                interface.send_data_to_led([i,j],[k,l])
                time.sleep(2)
"""                

"""
while True:
    for i in range(4):
        print(i,end=" ")
        for j in range(4):
            print(interface.recieve_data_from_ldr(i,j),end=" ")
            time.sleep(0.2)
        print("")
"""

#while True:
    #print(interface.recieve_data_from_ldr(1,1))
    #time.sleep(2)
"""
while True:
    print(interface.read_button())
    time.sleep(1)
"""

#interface.set_indicator_led(0)

#interface.wait_for_user_to_play()
