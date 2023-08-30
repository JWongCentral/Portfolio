import os
#simple object to manage/keep track of ticker information
#specifically so we can add and remove tickers


#open_file()
    #opens file and should be the first thing that should occur to ensure that everything is loaded
#add_ticker(name)
    #adds the ticker in question
#remove_ticker(name)
    #remove the ticker from the file
#save()
    #simply saves the file

#backup()
    #saves to the backup location
    #shouldnt have to be used, this will backup the last addition/removal
    #before the changes are made


class ticker_info(object):
    def __init__(self, dest = './financial_app/scripts/ticker'):
        self.tickers = []
        self.dest = dest
        self.file = None

    
    def getTickers(self):
        return self.tickers

    
    #this will open the file in the directory ./ticker/tickerbase.txt
    #returns true if successful
        #updates self.tickers with the updated tickers
    def open_file(self):
        try:
            self.file = open(self.dest+"/ticker_base.txt", 'r')
            temp = self.file.readlines()
            self.file.close()
            self.tickers = []

            for line in temp:
                self.tickers.append(line.replace('\n',''))
            return True
        
        #error finding it, so we will create the file
        except Exception as e:
            try:
                print(e)
                print("creating file /ticker_base.txt")
                self.file = open(self.dest+"/ticker_base.txt",'x')
                self.file.close()
                return True
            except Exception as a:
                print(a)

        return False
    
    #simple returns true if it is already added
    def ticker_exists(self,name):
        self.file = open(self.dest + '/ticker_base.txt', 'r')
        lines = self.file.readlines()
        self.file.close()
        for line in lines:
            line = line.replace('\n','')
            if (line.lower() == name.lower()):
                return True
        return False
    

    #adds ticker to the list
    def add_ticker(self,name):

        #did not open file, attempts to create/make default files
        if(self.file is None):
            print("Error file not opened")
            print('Attempting to open default')
            if(not self.open_file()):
                print("fatal error")
                return False
        
        #opens file and then adds in the name
        try:
            #checks if it exists then adds
            if(self.ticker_exists(name)):
                print("Ticker already Exists")
                return False
            #appending
            self.file = open(self.dest + '/ticker_base.txt','a')
            self.file.write(name+'\n')
            self.file.close()
            self.tickers.append('name')
            return True
        except Exception as a:
            print('Error:',a)
        

        return False
    
    #returns False if it failed to remove it
        #also false if it never existed in the first place
    #returns True if successfully removed
    def remove_ticker(self,name):
        try:
            #doesn't exist
            if (not self.ticker_exists(name)):
                return False
            #does exist so we will overwrite with current information
            else:
                self.tickers.remove(name)
                #overwriting
                self.file = open(self.dest+'/ticker_base.txt', 'w')
                for x in self.tickers:
                    self.file.write(x+'\n')
                self.file.close()
                return True
            

        except Exception as e:
            print (e)
        return False
    

    #saves to main directory
    def save(self):
        try:
            #first checks if the current file is uptodate
            self.file = open(self.dest+'/ticker_base.txt', 'r')
            temp = self.file.readlines()
            self.file.close()

            #checks if file is up to date
            updated = True
            for ind,line in enumerate(temp):
                if (not line.replace('\n','') == self.tickers[ind]):
                    updated = False
            

            #overwrites file
            if not updated:
                self.file = open(self.dest+'/tickers_base.txt', 'w')
                for i in self.tickers:
                    self.file.write(i+'\n')
                self.file.close()

            return True
        except Exception as e:
            print("Error:",e)
            return False
            


    #saves to backup file
    def backup(self):
        try:
            self.file = open(self.dest+'/ticker_base_backup.txt','w')
            for x in self.tickers:
                self.file.write(x.lower()+'\n')
            self.file.close()
            return True
        except Exception as e:
            print(e)
            return False
        




if __name__ == '__main__':
    test = ticker_info()
    #print("testing open_file", test.open_file())
    print('Testing add' , test.add_ticker('test'))
    input()
    print('Testing remove', test.remove_ticker('test'))




