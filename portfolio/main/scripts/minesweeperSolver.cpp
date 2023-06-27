#include <iostream>
#include <string>
#include <omp.h>
#include <stdlib.h>
#include <vector>
#include <cstring>
#include <chrono>
#include <ctime> 
#include <fstream>

using namespace std;

#define MAX_THREADS 8

//to be used later
enum possibleActions {flag, open};

enum state{
    unknown, //will be marked with a "_"
    integer, //will be marked with a "0" where 0 can be any constant number
    flagged  //will be marked with a "?" to say it is currently flagged
};
//stores game state
struct possibility{
    char ** gameState;
};

//stores next possible move
struct moves{
    int row,col;
    double probability;
    possibleActions action;
};

//stores position (basically just a tuple for x,y location in game board)
struct position{
    int row,col;
};

//function declarations
int getNeighboringFlags(char** array, int r, int c);
void loadArray(string& s, int r, int c);
void printArray(char ** array);
vector<moves> BasicRule1(char ** array);
vector<moves> BasicRule2(char **array);
bool countingCheck(int i,int j, char ** array);
bool added(vector<position> &vec, int r, int c);
vector<position> getUnknownNeighbors(char ** array, int i, int j);
vector<moves> ruleThree();
void brutus(char ** gameState, vector<position> flags, vector<possibility>& ret);
vector<moves> basicRules();
bool countingCheckOpen(int i, int j, char ** array);
string loadTrial(int num);
string getTrial(int num);
void printMoves(vector<moves> vec, string & ret);
void testTrial(int num);
void performActions(vector<moves> vec, int lives, char ** answer);
void openNeighbors(int i, int j, char ** answer);
char ** getArray(string s, int r, int c);



//global vars
int row, col;
int numBombs;
char ** gameBoard;
int points [] = {-1,-1,-1,0,-1,1,0,-1,0,1,1,-1,1,0,1,1,};





//gets the sum of the flaged values around coordinate r and c
//this helps determine if you can click safely
int getNeighboringFlags(char** array, int r, int c){
    int sumOfFlags=0;
    
    //grabs 1 tile away from r,c
    for(int i = -1; i <= 1;i++){
        for(int j = -1; j <= 1; j++){

            //validation
            if(r+i >=0 && r+i < row && c+j >= 0 && c+j < col){
                if(array[r+i][c+j] == '?'){ 
                    sumOfFlags++;
                }
            }
        }
    }

    return sumOfFlags;
}



void loadArray(string& s, int r, int c){
    row = r;
    col = c;
    gameBoard = new char*[r];
    for(int i = 0; i < r; i++){
        gameBoard[i] = new char[c];
        for(int j = 0; j < c; j++){
            gameBoard[i][j] = s.at((i*r)+(j));
        }
    }
}

void printArray(char ** array){
    for (int r = 0; r < row; r++){
        for(int c = 0; c < col; c++){
            cout << array[r][c];
        }
        cout << endl;
    }
}

//First basic rule...
//if a node has a number and the neighboring number of flags are the same
//then the rest of the unknowns are safe
/**
*   ? ? ?
*   ? 1 F
*   ? ? ?
*
*   turns into...
*
*   O O O
*   O 1 F
*   O O O
* 
*   Where O means it is safe to open with 0% chance of being a bomb
**/
vector<moves> BasicRule1(char ** array){
    vector<moves> ret;
    int r,c;
    vector<position> temp;
    char ind;
    
    //#pragma omp parallel for num_threads(MAX_THREADS) collapse(2)
    for(r = 0; r < row; r++){
        for(c = 0; c < col; c++){
            //ind = index in question
            ind = array[r][c];
            //we reached a number now we check
            if(ind >= '1' && ind < '9'){
                //if the numbered tile is the same number of flags, then rest are safe
                if((ind-'0') == getNeighboringFlags(array,r,c)){
                    temp = getUnknownNeighbors(array,r,c);
                    for(int i = 0; i < temp.size();i++){
                        struct moves temp2;
                        temp2.row = temp[i].row;
                        temp2.col = temp[i].col;
                        temp2.probability = 0;
                        temp2.action = open;
                        ret.push_back(temp2);
                    }
                }
            }
        }
    }


    //remove duplicates
    int index = 0;
    while(index < ret.size()){
        struct moves temp2;
        bool erased = false;
        temp2 = ret[index];
        for(int i = index+1; i < ret.size(); i++){
            if(temp2.row == ret[i].row && temp2.col == ret[i].col){
                ret.erase(ret.begin()+i);
                erased = true;
            }
        }
        if(!erased){
            index++;
        }
    }

    return ret;
}

//check the known tile, if the number of unknown is the same as the number. we can flag
//the unknowns
/**
*   1 ? ?
*   2 3 F
*   1 ? ?
*
*   turns into...
*
*   1 F ?
*   2 3 F
*   1 F ?
* 
*   where we now know the 2 ? are flags because of the 1,2,1 or any order of em could work.
*   Then we can rerun rule 1 to finish off the rest of the unknowns
*   
*   Special Case:
*
*   2 ? ?
*   3 ? ?
*   2 F ?
*
*
*   We can assume that the flag here came from another rule and we need to account for this
*   TO fix this we can actually subtract the tile number with neighboring flags then check the unknowns again
*
*   2 ? ?
*   2 ? ?
*   0 F ?
*
*   And when we can use the aforementioned case above to check for unknown neighbors and flag them accordingly
*
*   2 F ?
*   2 F ?
*   0 F ?
*   
*   Then putting it back together
*
*   2 F ?
*   3 F ?
*   2 F ?
**/
vector<moves> BasicRule2(char **array){
    vector<moves> ret;

    vector<struct position> temp;
    struct moves temp2;
    int r,c,flags;
    char ind ;
    //#pragma omp parallel for shared(array) private(r,c,temp,ind,temp2,flags)  num_threads(MAX_THREADS) collapse(2)
    for(r = 0; r < row; r++){
        for(c = 0; c < col; c++){
            //ind = index in question
            ind = array[r][c];
            
            //we reached a number now we check
            if(ind >= '1' && ind < '9'){

                temp = getUnknownNeighbors(array,r,c);
                flags = getNeighboringFlags(array,r,c);

                //if the number of unknowns is the same as the tile number
                if(ind-'0' == temp.size() && flags == 0){
                    //then those unknowns are guaranteed bombs
                    for(int i = 0; i < temp.size();i++){
                        temp2.row = temp[i].row;
                        temp2.col = temp[i].col;
                        temp2.probability = 1.0;
                        temp2.action = flag;
                        ret.push_back(temp2);
                    }
                }

                //if there are flags we have to use the special case, where we need to subtract
                //the number of flags from the known tile number
                else if((ind-'0'-flags) == temp.size() && temp.size() != 0){
                //then those unknowns are guaranteed bombs
                    for(int i = 0; i < temp.size();i++){
                        temp2.row = temp[i].row;
                        temp2.col = temp[i].col;
                        temp2.probability = 1.0;
                        temp2.action = flag;
                        ret.push_back(temp2);
                    }
                }

            }

        }
    }
    return ret;
}




/*
    Can realistically only be performed on the FLAG check
    the node that is passed is the UNKNOWN tile's location
    We are only checking this tile and return true or false if this game state can exist
    1. It will first grab all the known tiles that are adjacent to this tile.
    2. We will iterate through all the known tiles and subtract the number of flags around this known tile
    3. If it is negative we will return false cause this game state can't exist
*/
bool countingCheck(int i, int j,char ** array) {

    //we are assuming the tile in question is flagged
    if(array[i][j] !='?') return false;


    vector<position> knownTiles;
    struct position temp;
    int r1,c1;
    //for loop to grab array[i][j] KNOWN neighbors
    for(r1 = -1; r1<=1;r1++){
        for(c1 = -1; c1<=1; c1++){
            if(i+r1 >=0 && i+r1< row && j+c1 >= 0 && j+c1 <= col){
                if(array[i+r1][j+c1] >= '1' && array[i+r1][j+c1] <= '9'){
                    temp.row = i+r1;
                    temp.col = j+c1;
                    knownTiles.push_back(temp);
                }
            }
        }
    }
    
    //there are known tiles around it so we check if we end up counting negatives
    if (knownTiles.size()>0){
        for(int i1 = 0; i1 < knownTiles.size();i1++){
            int r = knownTiles.at(i1).row;
            int c = knownTiles.at(i1).col; 
            int temp = getNeighboringFlags(array,r,c);
            //checks the number offset from char->int
            //then we subtract the known number of flags
            //cause if there are 4 flags but the number is 3, this gamestate cannot occur
            if((array[r][c]-'0'-temp) < 0){
                return false;
            }
        }
    }

    return true;
}

//very Similar to the function above but now we check it for the open case
//Such that if there ever is an open case than the affected KNOWN tiles should have an unknown if the count is > 0
//Remember we are still subtracting if there is a flag but if we consider it safe/open
//then we must consider that if there are a tile such as so...
/*
*   S F S
*   S 3 F
*   S S S
*   this cannot exist because there is no room to flag anymore, so we need to count number of open/safe spots in this case
*/
bool countingCheckOpen(int i, int j, char ** array){
    //we are assuming the tile is SAFE
    if(array[i][j] !='S') return false;
    
    //first we will grab affected KNOWN tiles
    vector<position> knownTiles;
    
    //for loop to grab array[i][j] KNOWN neighbors
    for(int r1 = -1; r1<=1;r1++){
        for(int c1 = -1; c1<=1; c1++){
            if(i+r1 >=0 && i+r1< row && j+c1 >= 0 && j+c1 <= col){
                if(array[i+r1][j+c1] >= '1' && array[i+r1][j+c1] <= '9'){
                    struct position temp;
                    temp.row = i+r1;
                    temp.col = j+c1;
                    knownTiles.push_back(temp);
                }
            }
        }
    }

    //if we are saying its safe we need to check there are still enough unknowns to solve the rest of the puzzle
    //otherwise we have way too few bombs around a known tile.

    if (knownTiles.size()>0){
        for(int i1 = 0; i1 < knownTiles.size();i1++){
            int r = knownTiles[i1].row;
            int c = knownTiles[i1].col; 

            int possibleBombs = 0;

            //checking neighboring tiles around known tiles
            //possible bombs are any F or unknown tiles
            for(int r1 = -1; r1<=1;r1++){
                for(int c1 = -1; c1<=1; c1++){
                    if(r+r1 >=0 && r+r1< row && c+c1 >= 0 && c+c1 <= col){
                        if(array[r+r1][c+c1] == '?' || array[r+r1][c+c1] == '_'){
                            possibleBombs+=1;
                        }
                    }
                }
            }

            //the maximum number of possible bombs is lower thna the tile number, impossible state
            if (possibleBombs < array[r][c]-'0'){
                return false;
            }

            
        }
    }
    return true;


}



bool added(vector<position> &vec, int r, int c){
    for(int i = 0; i < vec.size(); i++){
        if(vec[i].row == r && vec[i].col == c){
            return false;
        }
    }
    struct position temp;
    temp.row = r;
    temp.col = c;
    vec.push_back(temp);
    return true;
}

//returns a vector of all the position of the UNKNOWN neighbors of this tile
//we are assuming this tile is a KNOWN tile
vector<position> getUnknownNeighbors(char ** array, int i, int j){
    vector <position> ret;
    //needs to be a known tile otherwise disregard
    if(!(array[i][j] >'0' && array[i][j] <='9')) return ret;
    for(int r = -1; r<=1;r++){
        for(int c = -1; c<=1; c++){
            //bound checking
            if(r+i >=0 && r+i< row && c+j>= 0 && c+j <= col){
                //if unknown we add
                if(array[r+i][c+j]=='_'){
                    struct position temp;
                    temp.row = r+i;
                    temp.col = c+j;
                    ret.push_back(temp);
                }
            }
        }
    }
    return ret;
}
//rule 3:
//we will first get a list of all UNKNOWN tiles that are adjacent to a known tile
//once we have found that then we'll call the recursive exploration on that chunk
vector<moves> ruleThree() {
    vector<position> unknowns;
    vector<position> knowns;
    vector<moves> ret;
    for (int i = 0; i < row; i++) {
        for (int j = 0; j < col; j++) {
            
            //if numeric/known we will get neighbors
            if(gameBoard[i][j] >'0' && gameBoard[i][j] < '9'){
                //dealing with unknowns
                vector<position> neighbors = getUnknownNeighbors(gameBoard, i,j);
                //go through neighbors to add to main list
                for(int k = 0; k < neighbors.size();k++){
                    added(unknowns,neighbors[k].row,neighbors[k].col);
                }

                //dealing with knowns(for checking if we are done traversing)
                if(neighbors.size()>0){
                    struct position temp;
                    temp.row = i;
                    temp.col = j;
                    knowns.push_back(temp);
                }
            }
        }
    }

    


    //vector now has the entire traversal list so we will now check all possible game states
    vector<possibility> check;

    brutus(gameBoard,unknowns,check);

    //we have now finished preprocessing it, now we just need to calculate the probability using a simple
    // count amount divided by total amount
    //
    //
    //        count/total = 0.758912783 or some double value and this is the probability
    //
    //

    //populating moves/return val
    for(int i = 0; i < unknowns.size(); i++){
        struct moves temp;
        temp.row = unknowns[i].row;
        temp.col = unknowns[i].col;
        temp.probability = 0.0;
        temp.action = open;
        ret.push_back(temp);
    }

    //readjust the moves based off of our statistics
    for(int i = 0; i < check.size();i++){

        char ** boardState = check[i].gameState;
        
        //going through unknowns and adding in probability counter
        for(int j = 0; j < unknowns.size(); j++){
            struct position temp;
            temp = unknowns[j];
            if(boardState[temp.row][temp.col] == '?'){
                ret[j].probability += (1.0/((double)check.size()));
                if(ret[j].probability >= 0.5) ret[j].action = flag;
            }
            
        }

    }


    

    return ret;

}
/*
    Recursive call to do a DFS like explorative search
    gameState -> is a PRIVATE gameState and will be duplicated as we traverse to avoid shallow copy problems
    flags -> will contain the list of unknown tiles and this will also be private

*/
void brutus(char ** gameState, vector<position> flags, vector<possibility>& ret){

    //we have traversed entire flags array so we will add it to the gameState
    if(flags.size() == 0){
        struct possibility temp;
        temp.gameState = new char*[row];
        for(int i = 0; i < row; i++){
            temp.gameState[i]  = new char[col];
            int j;
            //#pragma omp parallel for shared(temp,i) private(j) num_threads(MAX_THREADS)
            for(j = 0; j < col; j++){
                temp.gameState[i][j] = gameState[i][j];
            }
        }
        ret.push_back(temp);
        return;
    }

    //create deep copy
    char ** array;
    array = new char*[row];
    for(int i = 0; i < row; i++){
        array[i]  = new char[col];
        for(int j = 0; j < col; j++){
            array[i][j] = gameState[i][j];
        }
    }
    
    //creating deep copy vector
    //cant use =, it only works for primitives
    vector<position> check;
    for(int i = 0; i < flags.size(); i++){
        struct position temp;
        temp.row = flags[i].row;
        temp.col = flags[i].col;
        check.push_back(temp);
    }
    


    //we will first check flag state and then the unflagged state
    int r = check[0].row;
    int c = check[0].col;


    //we have stored first value, so we will erase it for recursive calls
    check.erase(check.begin());

    //simple parallel
    int i;
    
    
    for(i = 0; i < 2; i++){
        if(i == 0){
            array[r][c] = '?';
            //check if this flag is possible
            if(countingCheck(r,c,array)){
                brutus(array,check,ret);
            }
        }
        else{
            array[r][c] = 'S';
            //we have checked flagged state, now lets check unflagged state
            if(countingCheckOpen(r,c,array)){
                brutus(array,check,ret);
            }
        }
    }
        
    
    
}

//will only run basic rules 1,2
vector<moves> basicRules(){
    vector<moves> rule1,rule2;
    if(gameBoard == NULL){
        return rule1;
    }

    //run the rules
    rule2 = BasicRule2(gameBoard);
    for(int i = 0; i < rule2.size(); i++){
        struct moves temp = rule2[i];
        gameBoard[temp.row][temp.col] = '?';
    }

    
    //checking those flags
    rule1 = BasicRule1(gameBoard);
    for(int i = 0; i < rule2.size();i++){
        rule1.push_back(rule2[i]);
    }
    

    
    
    

    return rule1;
}

vector<moves> solver(){
    vector<moves> ret,temp;
    ret = basicRules();
    if(ret.size() != 0){
        return ret;
    }
    
    ret.clear();
    temp = ruleThree();
    
    //rule 3 cannot apply here an island is created and we cannot calculate it, its up to the gods to decide now
    if(temp.size() == 0){
        return ret;
    }

    //there are 2 cases
    //one where there are absolutes and one where there are not so first we check if there are absolutes
    for(int i = 0; i < temp.size();i++){
        if(temp[i].probability == 1.0 || temp[i].probability == 0.0){
            ret.push_back(temp[i]);
        }
    }


    if(ret.size() != 0){
        return ret;
    }
    
    //there are no absolute so we go for next highest chance
    struct moves max;
    max = temp[0];
    for(int i = 1; i < temp.size(); i++){
        double probability = temp[i].probability;

        //if it is open, then that means probability is inversed to 3%, so it means 97% good choice
        if(temp[i].action == open){
            probability = (probability-1)*-1;
        }

        if (probability > max.probability){
            max = temp[i];
        }
    }

    ret.push_back(max);
    return ret;
        
    

}

void printMoves(vector<moves> vec, string & ret){
    string s_temp = "";
    for(int i = 0; i < vec.size(); i++){
        s_temp = "";
        struct moves temp = vec[i];
        cout << "row:" << temp.row << endl << "col:" << temp.col << endl << "Probability:" << temp.probability << endl;
        if(temp.action == flag){ 
            cout << "Action: FLAG"<< endl << endl;
            s_temp += to_string(temp.row)+ "|" + to_string(temp.col) + "|" + to_string(temp.probability) + "|" +"?";
        }
        else if(temp.action == open){
             cout << "Action: OPEN"<< endl << endl;
             s_temp += to_string(temp.row)+ "|" + to_string(temp.col) + "|" + to_string(temp.probability) + "|" +"O";
        }
        ret += s_temp + "\n";
    }
}

//we will just show graph about which moves to make
void printMovesBetter(vector<moves> vec){

    char ** temp;
    temp = new char*[row];
    int i,j;
    for(i = 0; i < row; i++){
        temp[i]  = new char[col];
        //#pragma omp parallel for shared(temp,i) private (j) num_threads(MAX_THREADS)
        for(j = 0; j < col; j++){
            temp[i][j] = gameBoard[i][j];
        }
    }

    for(i = 0; i < vec.size(); i++){
        struct moves temp1;
        temp1 = vec[i];
        if(temp1.action == flag)
            temp[temp1.row][temp1.col] = 'F';
        else if (temp1.action == open)
            temp[temp1.row][temp1.col] = 'S';
    }

    printArray(temp);

}

//for testing purposes
/*

    Trial 1: 10x10 (20% bomb)
    Trial 2: 15x15 (20% bomb)
    Trial 3: 20x20 (25% bomb)
    Trial 4: 25x25 (20% bomb)
    Trial 5: 30x30 (25% bomb)
    Trial 6: 35x35 (30% bomb)
    Trial 7: 40x40 (30% bomb)
    Trial 8: 40x40 (25% bomb)

*/
string loadTrial(int num){
    switch(num){
        case 1:
        return "_____________213_______1012______1001______1001______1011______101_______112________________________";
        case 2:
        return "_________________________________________________________________________________________________________________211122________41000011_______20011100_______2102_310________114__10_____________10_____________11_______________";
        case 3:
        return "_____________________________________________________________________________________________________________2112_______________11003_______________10013_______________2001________________4102_________________101_________________212________________________________________________________________________________________________________________________________________________________________________";
        case 4:
        return "__________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________2223___________________111001___________________10000113_________________11221002_____________________1012_____________________212_____________________________________________________________________________________________________________________________________________________________________________________________________________________________________________";
        case 5:
        return "_________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________3112333212__________________321000000002__________________100000122102__________________2212111__212_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________";
        case 6:
        return "__________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________211________________________________101________________________________1013_______________________________2101________________________________222_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________";
        case 7:
        return "______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________3211___________________________________11001___________________________________10002___________________________________31101_____________________________________213______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________";
        case 8:
        return "___________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________2112____________________________________1002_________________________________2211002_________________________________1000001_________________________________1000001_________________________________1112221_________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________";
    }
    return "";
}

string getTrial(int num){
    switch(num){
        case 1:
        return "X101X3X3X2121213X43X01X10124X31221001XX21X2100122123X10111001X2101X1001121122200112X23X3111X212XX3X1";
        case 2:
        return "011112X2221011101X11X22XX101X101112332221011100012XX321100000002X5XX2X101110113X32332213X212X21223X11X3X31X2102XX211122X111003X41000011111002X200111002X211122102X310X34X311X114XX103X4XX32112XX3102X44XX2113X531112X2222X12XX2X1";
        case 3:
        return "12322X3XX2X2X12X31111XXX33X53312223XX43X124X23X5X1001X23XXX3222223XX2211112234X2XX11X33422X1123X1111332223X2X2112XX321211X11X32311003XX31X2X222113X310013XX332421X1013XX2001X33X2X3X12212X7X4102333232X201X13XXXX101XX2X111101112X5X3212222110000111112111X11122321002X3101112222X3XXX2113XX101X12X22X4465X12X54201223X3323XXX21X3XX1013X32X3X5442211223211XX4325XXX102X0001X224XX3X4X42103X000112X223X3X210002X";
        case 4:
        return "000002X2122211012X3210122000014X31XX4X201X4XX113XX00002XX445X4X2012X3322XX322213X5XXX2211001222X3342XX3X32X33210000123X323X3X224X311211001233XX4X34X41002X2001X2101XXX323XX5X20001122222X1123443235XX43112211XX12333X32XX3XX33XX21XX112322XX3X3X334X42234X2332101X222323111X5X21X21X11X10111001X21112XX2222011112110000113X2012212X2011101X11221002X2000002X311X112333XX1012210011112X11111X2XX42212X21112X101110001135X413X32X11X2110000000001XX5X3X32223320000000122113XX2212X11XX210001101XX20122100112233X32101X125X30001110001X113XX10221X3X20001X100011102X3101X124320001221000111223222112XX100013X31001X11X3XX21X22210001XXX100111113X32X";
        case 5:
        return "0112X10000002X5X4X23X4X23X3XX224X4331000013XXXX22XXX3X4X323XXXX4XX100013X4333334X433X22232X423X321101XX2123XX322X4322XX22212221X2244322XX43X223XX22X4X2X21X2222XXX21X5X3212X34X211213X3234X113XX212X3X10113X4321003X22XX21012221213231114X4XX321X544X42011101X213X4X33XX534XX2XXXX4X212X10123X3X4XX3XX5X235X4X53X33X211112X33122334XX212XX2X2112X22123X44X20112X333223XX221123223X5XX4XX201X34X21X3X32X113XX11XXXXX3332013X4X212X321222XX3112333212X3213X4220112X11X3321000000002XX2X322X101121123X1000001221023333X221212X1001X32212111XX212X22X3X101X33210113X3X3X335X33X4X43312122X2X10002X313X4XX22XX53XX211X111211011222012X32113X4X43X1222011100X32X210123210113X22221X101X210X5X3X1012XX10112111X1123333X21XX332212X44212X20133212XXX212XX43X11X33X2X12X201XX12X6X521222X322113X3211111012223X4XX11X1123X2223X310011212111X2223222213X32XX22X2212X2X2X1111001X11X2XX4222112X3X212121101121212222XXX1000012X2100000001X2X101X1";
        case 6:
        return "01123XX3X2111X102X3X223X22X2111X21102X5XXX312X221103X522XX5X312X1123X113XXXX31012X21113XX2223XX2023311X322X3332100134X23X334X22332101XX222X1X210001111XX32XX33X43XX1011223X22212212211X224X31222XXX222101X33322X10X11XX112X13X410023421111012XXX1122122134311112XX2012X1012X1002465312X2X101XX322125X301X3211X44211XXXX13X412134X5XX12XX20123X222XXX213X5324XX12X2X4XX633X53101X5X213XX2013X22XX3X2122X4XXX32XX2233XX412442013X22X3111112234XX21222XX33XX11XX322X323220223X22X323210024X21332234XX444X3X21XX4X44X201X2222X2113X32X335XXX4X22XX5X5XX311222XX21101XXX324X4X44X3111X53XXX322X2244421013X43X4X5212X2000XX24X5X2X33X2XXX21012X324XX201110113312X42212X33444X22222X12XX4110113XX3333X112323X3X212XX221124X4X202X4X3XXX3112XX23X3222234X4211X23X313X42X6XX2013X32X334X3X23XXX2212233X223XXX53213X42223XXX544X566X312X3X223X44XX21X3X4X22X345XXX3XXXX3X33X322XXX3XX32123X43X211XX5335X5344X33X34XXXX44X2003XX211124X21X3X43XX4X22XX343X33X3002X42101X3211233XX5X52323222XX33X200112X3234X3222X2334X3X3X202X423X21000012XX3XX6XX2123X32323X202XX2X43211111233X6XXX4212XX32X233323433X4XX11X22X112XXX6X32X555X4X3XX3XX23X3233433X210135X5XX34XXXX32X44X44XX3222XXX4221213X5X322XX6X64322X3X4312X3X45XX22X3X3XX3223444XXXX32234XX012X3X223X22X22222X2XX2X4X5X3X11XX3";
        case 7:
        return "1102X2000012XX3X222102X324XX1113XX2X2232X203X301234X7X523XX213X3XXX311X3X4434XXXX324X313XXXXXX4X3322X2234542122212XX4X644X3XX33XX555X5X5X422234X3XX22X11234X33XXXX3222XX6X3X4X3XXXX22XXX5443X212XX3223X32222223XX24X41346532X34X3XX21102XX21X432001XX223323X523XXX3321112332001232235XX200235X33X33XXX4X43XX101111X1123X222XXXX3013X4X3XX4X5XX543223222X11223XX4X3X345X201XX422224X535XXX433X3X2101X3X34X5333X430235X20124X4X5X5XXXX3X3321113222XX2XX3XX13X4X212XX44XX433X54323XX1001X11233322222XX4122X5XX23XX113X4X12X3112332101X10111X6X301X3X321233102XX2112211XX2X2243201X2X6X5332211002X2012433222X2222334XXX2112X2XXXXX1001112X312X2X2XX22X1124XX4X6X3111246X421001X2223X323123432111XXX532XXX3222XX31122123X11X22X2112XX101245XX1124X5XXX4X212XX12X3112222X12X42213X3X3211234XX313233X5322X3112X11113X301X4X411001XX3X3101X4XX4X234X22X211112X31214X410002332221012XXX313XX33X3333X1113X423XX31101X102X2001243213X32X33XXX33223XXX34X4X2132202X212222X23X31224X5X32XX4X4XX44X412X4X201222XX3X3X4X201X3X32345XX433X4XX2013XX4224XX43X333X320223111XXX5XX323X322113XXX3XXXX3222X33X211X10125X54XX4X32211X24XX33XX334X1123X4X322113X5XX3224X42X222X4X421332XX4334X33X4X101XX5XX2003XX22X123X3X222X1XX4XXXX433X3212323X42014X632111X343X2X2135X434XX3X4X22X2123X112XXXX11122X2X33221X4X31245X34X33X21X2111X5XX423X223433X11XX42X22XX33X23X4343312223XX31XX21XX2X2233X312X223X2113X4XXX2X3X113X223322445432XXX201122332113X434233X2101122X11X2XXXX34X122212XX3X32X33X212X2101111X322123X6X44X23XX23X43X3X44X33X211001X1234X221213X4XXXX5X43X21122XX4X33432101233XX3X4X2023X32334X4X32211134X33XXXX2102XX4443XX313X321X12X312X2X101X22X3333X102X32XX2222X3X21X";
        case 8:
        return "X2X22X11110112XX2111X11X3X2X2110111000002322X211X333X2333X111112X3423X101X1000001X3333223XXX422X211111012X3X31101110122112XX3XX24X6X4X322112X332324X311110112XX212334X4X4X534X21X11X4XXX3X22X23X311X23X31X33X2213XX4X3112222X35X411112XXX111123X23XX322135X6X4112X12233X21121234321212X2X2222X2X2XX4XX11X323X4X223X4X11X22X3X421110122212222332113X5XX322XXX32212X34XX210001X22321001X1013X4XX31X3333X2234X2333X000112XXX10011212X223X321101X3X3XX322X21222112342100002X311012X10012222X433X3221XX2X23X20000113X21232211002X21222X22X11X33223XX211101X2233XXX210014X53X233211122X101X3211X223211XX443X2213XXXX32XX32111X22011111212XX42223X333X3X3X44X213XX3X321X100002X2013XXX2112XX34X542222102333XX101111225X4111356X31134X3XXX11X3211X222221123X3XXX5X202XXXX101X234X3112XX223X1012X2XX45X6X5X303X653312112X310013X21X2112X22XXX4X413X202XX3X2X1002X3111121111213X3112323X31111013X4221100234X33X223212X4X31232123X11111122X1000001XX3XX32XXX24X412XXXX23X311X11X22110000012223X213X4X4X3122X44X4X2022212X21111222101121102232X3X12X112X43323X42212X22X3XX211X10001X1112112X01222XX3XXXX21323X4X43X1122100111000001101X1124X5XX32X3X424X322224X20000000000110222124X4443213X4X445X33XXX310011222101X13X32XX3X2XX2123X3XXXX5XX43X1001X2XX21321XXX2233234X21X212234XX53111100234323X4X24X4322X12X53212233223XX10000001XX213XX2X334XX4334XXX201XXXX11221011100123X12X3112XX34XX3XX7X2013X531111112X211123211110134313X55XXX210123X211X33X213X22XX1111002XX324XX4XX53212X44X222XX2103X32X422X211X4X3XX44X43XX3X22XX3X11221114X3224X324X223123X45X434X31112221101123X4X32X3X21XX4X10012XXXX3X321121211112X2XX422X442225XX110001234X32X11X2X2X11X21223X112XX11X3X3";
    };
    return "";
}

char ** getArray(string s, int r, int c){
    char ** ret;
    ret = new char*[r];
    for(int i = 0; i < r; i++){
        ret[i] = new char[c];
        for(int j = 0; j < c; j++){
            ret[i][j] = s.at((i*r)+(j));
        }
    }
    return ret;
}

//perform the actions for testing and solving the answer through and through
void performActions(vector<moves> vec, int lives, char ** answer){
    for(int i = 0; i < vec.size(); i++){
        struct moves temp;
        temp = vec[i];
        
        //we are trying to open, if it is a bomb it is game over, and we will clear board
        //if tries is enabled after after X many attempts it will be game over otherwise they get "lives"
        //such that if they hit a bomb they lose a life and the tile automatically gets flagged
        if(temp.action == open){

            if(answer[temp.row][temp.col]=='X'){
                lives--;
                //no lives left we end game
                if (lives <= 0){
                    cout << "GAME OVER BOMB EXPLODED AT" << endl << "Row:" << temp.row << endl << "Col:" <<temp.col << endl <<endl;
                    printArray(gameBoard);
                    cout << endl << endl;
                    gameBoard = answer;
                    return;
                }

                //bomb exploded, we flag and return
                else{
                    cout << "BOMB EXPLODED AT" << endl << "Row:" << temp.row << endl << "Col:" <<temp.col << endl <<endl;
                    gameBoard[temp.row][temp.col] = '?';
                    return;
                }
            }

            else if(answer[temp.row][temp.col]>='1' && answer[temp.row][temp.col] <= '9'){
                gameBoard[temp.row][temp.col] = answer[temp.row][temp.col];
            }

            //we hit an empty tile so we open neighbors
            else if (answer[temp.row][temp.col] == '0'){
                gameBoard[temp.row][temp.col] = '0';
                openNeighbors(temp.row,temp.col,answer);
            }

        }
        
        else if (temp.action == flag){
            gameBoard[temp.row][temp.col] = '?';
        }
    }
}

void openNeighbors(int i, int j, char ** answer){
    for(int r = -1; r <= 1; r++){
        for(int c = -1; c <= 1; c++){
            
            //validation
            if(i+r >= 0 && i+r < row  &&  j+c >= 0 && j+c < col 
                && gameBoard[i+r][j+c] =='_'){

                gameBoard[i+r][j+c] = answer[i+r][j+c];
                
                if(gameBoard[i+r][j+c] == '0'){
                    openNeighbors(i+r,j+c,answer);
                }

                
            }
        }
    }

    
    
}

bool testWin(){
    for(int i = 0; i < row; i++){
        for(int j = 0; j < col; j++){
            if(gameBoard[i][j] == '_'){
                return false;
            }
        }
    }
    return true;
}

void testTrial(int num){
    string game,answer;
    int trialNum = num; int size = 20;
    char ** answerArr;

    game = loadTrial(trialNum);
    answer = getTrial(trialNum);
    loadArray(game,size,size);
    answerArr = getArray(answer,size,size);
    string buffer;
    while(!testWin()){
        vector <moves> actionsToPerform;
        cout << actionsToPerform.size();
        actionsToPerform = solver();
        if(actionsToPerform.size() ==0){ 
            cout << "Algoritm cannot apply here" << endl;
            printArray(gameBoard);
            return;
        }
        cout << actionsToPerform.size();
        string s = "";
        printMoves(actionsToPerform,s);
        performActions(actionsToPerform, 3, answerArr);
        printArray(gameBoard);
    }

}



//to create a minesweeper board keep in mind the following
/*
    a '_' is an unknown square
    a '0' is an empty and opened square
    any numeric value is a numbered tile
    a 'X' is a bomb
    a '?' is a flag

*/



/*

This is only for testing purposes otherwise we will outmit this
int test(){
    auto start = std::chrono::system_clock::now();
    testTrial(3);
    auto end = std::chrono::system_clock::now();
 
    std::chrono::duration<double> elapsed_seconds = end-start;
    std::time_t end_time = std::chrono::system_clock::to_time_t(end);
 
    std::cout << "finished computation at " << std::ctime(&end_time)
              << "elapsed time: " << elapsed_seconds.count() << "s"
              << std::endl;

    


    return 0;
}
*/


//for running via django/python
int main(int argc, char *argv[]){
    
    if(argc < 2) 
        return -1;

    ofstream file;

    string temp = argv[1];
    string gamestate = argv[2];
    string ret = "";
    int size = stoi(temp);

    loadArray(gamestate,size, size);
    printMoves(solver(),ret);

    file.open("main\\scripts\\output.txt");
    file << ret;
    file.close();

    




    return 0;
}