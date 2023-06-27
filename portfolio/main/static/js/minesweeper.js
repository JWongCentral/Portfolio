document.addEventListener('DOMContentLoaded',() =>{

    const grid = document.querySelector('.grid');

    const restart_button = document.getElementById('restart')
    restart_button.onclick = restartGame

    const AI_Solver = document.getElementById('ai_solver')
    AI_Solver.onclick = runSolver

    const output = document.querySelector('.output')


    //specifically so we can get the csrf token from cookies data/info
    const getCookie = (name) =>{
        let cookieValue = null
        if(document.cookie && document.cookie !== ''){
            const cookies = document.cookie.split(';')
            for(let i = 0; i < cookies.length; i++){
                const cookie = cookies[i].trim();
                if(cookie.substring(0,name.length+1) === (name +'=')){
                    cookieValue = decodeURIComponent(cookie.substring(name.length+1))
                    break
                }
            }
        }
        return cookieValue
    }

    const winGame = document.querySelector(".win")
    const loseGame = document.querySelector(".lose")
    const bombLogo = '💣';
    const flagLogo = '🚩'
    //its a 1d array of 20x20, to keep it simple
    let width = 20;
    
    let bombAmount = 80
    let flags = 0

    //contains all the square/divs
    let squares = [] 
    let isGameOver = false;
    let isGameStarted = false;

    //game array containing X's and safes
    let gameArray = []

    function createBoard(){
        //randomized gameArray
        gameArray = createBombArray()

        //array to iterate thru the 
        for(let i = 0; i < width*width; i++){

            const square = document.createElement('div')
            square.setAttribute('id',i)

            square.classList.add(gameArray[i])
            grid.appendChild(square)
            squares.push(square)
            square.addEventListener('click', function(e){
                click(square)
            })
            square.addEventListener('contextmenu', (e) => {
                e.preventDefault()
                addFlag(square)
                checkForWin()
            })


        }
        calculateNumber()
    }

    function restartGame(){
        eraseOutput()
        isGameOver=false
        isGameStarted = false
        winGame.style.visibility='hidden'
        loseGame.style.visibility='hidden'
        gameArray = createBombArray()
        for(let i = 0; i < gameArray.length; i++){
            if(squares[i].classList.contains('checked'))
                squares[i].classList.remove('checked')
            if(squares[i].classList.contains('flag'))
                squares[i].classList.remove('flag')
            if(squares[i].classList.contains('flag_glow'))
                squares[i].classList.remove('flag_glow')
            if(squares[i].classList.contains('open_glow'))
                squares[i].classList.remove('open_glow')
            squares[i].classList.remove(squares[i].classList)
            squares[i].classList.add(gameArray[i])
            squares[i].innerHTML=''
            squares[i].removeAttribute('data');
        }
        calculateNumber()
    }
    function createBombArray(){
        //creates 2 array one with valid and oen with bomb
        const bombsArray = Array(bombAmount).fill('X')
        const emptyArray = Array(width*width-bombAmount).fill('0')
        //mesh the two together randomly
        ret = emptyArray.concat(bombsArray).sort(() => Math.random() -0.5)
        return ret
    }

    function calculateNumber(){
        //since its a 1d array we gotta do some weird math
        for(let i = 0; i < squares.length; i++){
            total = 0;
            
            //simple way of detecting edge cases
            const isLeftEdge = (i % width == 0)
            const isRightEdge = (i % width == width-1)
            //checks if it is NOT a bomb
            if(squares[i].classList.contains('0')){
                //checking left side
                if(i > 0 && !isLeftEdge && squares[i-1].classList.contains('X')) total++
                //checking top right side
                if(i > width-1 && !isRightEdge && squares[i+1-width].classList.contains('X')) total++
                //checking top side
                if(i > width && squares[i-width].classList.contains('X')) total++
                //checking top left side
                if(i > width+1 && !isLeftEdge && squares[i-1-width].classList.contains('X')) total++
                //checking right side
                if(i < (width*width)-1 && !isRightEdge && squares[i+1].classList.contains('X')) total++
                //checking bottom left side
                if(i < (width*(width-1)) && !isLeftEdge && squares[i-1+width].classList.contains('X')) total++
                //checking bottom right side
                if(i < (width*(width-1)-2) && !isRightEdge && squares[i+1+width].classList.contains('X')) total++
                //checking directly bottom side
                if(i < (width*(width-1)-1) && squares[i+width].classList.contains('X')) total++



                squares[i].setAttribute('data',total);
                
            }

        }
    }

    function click(square){

        if(isGameOver)return
        if(square.classList.contains('checked') || square.classList.contains('flagged')) return
        if(!isGameStarted){
            while(square.classList.contains('X') || parseInt(square.getAttribute('data'))!=0){
                restartGame()
            }
            isGameStarted=true
        }

        if(square.classList.contains('open_glow'))
            square.classList.remove('open_glow')
        else if (square.classList.contains('flag_glow'))
            square.classList.remove('flag_glow')

        //clicked on bomb
        if(square.classList.contains('X')){
            gameOver()
        }
        
        //clicked on safe
        else{
            let total = square.getAttribute('data')

            //numbered tile
            if(total != 0){
                square.classList.add('checked')
                square.innerHTML = total
                return
            }
            else{
                if(square.classList.contains('flag')){
                    addFlag(square)
                }
                openNeighbor(parseInt(square.getAttribute('id')))
                square.classList.add('checked')
            }
        }
    }

    function openNeighbor(position){

        const isLeftEdge = (position%width==0)
        const isRightEdge = (position%width== width-1)
        
        //timeout at 10ms
        setTimeout(() =>{

            //left
            if(position > 0 && !isLeftEdge){
                const newId = squares[parseInt(position-1)].id
                const newSquare = document.getElementById(newId)
                click(newSquare)
            }
            //right
            if(position < (width*width)-1 && !isRightEdge){
                const newId = squares[parseInt(position+1)].id
                const newSquare = document.getElementById(newId)
                click(newSquare)
            }
            //top right
            if(position > width-1 && !isRightEdge){
                const newId = squares[parseInt(position+1-width)].id
                const newSquare = document.getElementById(newId)
                click(newSquare)
            }
            //top
            if(position > width){
                const newId = squares[parseInt(position-width)].id
                const newSquare = document.getElementById(newId)
                click(newSquare)
            }
            //top left
            if(position > width+1 && !isLeftEdge){
                const newId = squares[parseInt(position-1-width)].id
                const newSquare = document.getElementById(newId)
                click(newSquare)
            }
            //bottom left
            if(position < (width*(width-1)) && !isLeftEdge){
                const newId = squares[parseInt(position-1+width)].id
                const newSquare = document.getElementById(newId)
                click(newSquare)
            }
            //bottom right
            if(position < (width*(width-1)-2) && !isRightEdge){
                const newId = squares[parseInt(position+1+width)].id
                const newSquare = document.getElementById(newId)
                click(newSquare)
            }
            //bottom
            if(position < (width*(width-1)-1)){
                const newId = squares[parseInt(position+width)].id
                const newSquare = document.getElementById(newId)
                click(newSquare)
            }

        }, 10)

    }

    //game over
    function gameOver(){
        isGameOver = true
        loseGame.style.visibility = "visible"

        //show all
        squares.forEach(square => {
            if (square.classList.contains('X')){
                square.innerHTML = bombLogo
            }
        })
    }

    //flagging tile
    function addFlag(square){
        if (isGameOver)return
        
        if(square.classList.contains('open_glow'))
            square.classList.remove('open_glow')
        else if (square.classList.contains('flag_glow'))
            square.classList.remove('flag_glow')

        //check if its opened/does not exceed bomb count
        if(!square.classList.contains('checked') && (flags < bombAmount)){
            
            //activate flag
            if(!square.classList.contains('flag')){
                square.classList.add('flag')
                square.innerHTML = flagLogo
                flags++

            //deactive flag
            }else{
                square.classList.remove('flag')
                square.innerHTML = ""
                flags--
            }
        }
    }

    function checkForWin(){
        let count = 0
        for (let i = 0; i < squares.length; i++){
            if(squares[i].classList.contains('flag') && squares[i].classList.contains('X')){
                count++
            }
            if(count == bombAmount){
                gameOver = true;
                winGame.style.visibility='visible'
            }
        }
    }

    //API CALLS BELOW
    //getString() returns gamestate as a string
    //sendPost() will return true/false if data was sent successfully

    //used to get the string for the solver
    /*
    ? = flag
    0-9 = bomb count and opened
    _ = unknown unchecked tile
    */
    function getString(){
        ret = ""
        for(let i = 0; i < width*width; i++){
            if(squares[i].classList.contains('flag')){
                ret+='?'
            }
            else if (squares[i].classList.contains('checked')){
                ret+=squares[i].getAttribute('data')
            }
            else{
                ret+='_'
            }

        }
        return ret
    }



    function getRequest(){
        const requestObj = new XMLHttpRequest()
        requestObj.onreadystatechange = function(){
            if(this.readyState == 4 && this.status == 200){
                loadData(this.responseText)
            }
        }

        requestObj.open("GET", '/projects/minesweeper/get')
        requestObj.send()
    }

    function loadData(jsonData){
        data = JSON.parse(jsonData)

        entries = data['entries']
        temp = ""

        //shifting through data
        for(let i = 0; i < entries; i++){

            //gathering data
            current = data[i]
            row = parseInt(current['row'])
            col = parseInt(current['col'])
            probability = parseFloat(current['probability'])*100
            action = current['action']=='?'?"flag":"open"

            //creating text
            entry = document.createElement('div')
            entry.setAttribute('class',"entry "+i)
            entry.innerHTML = "Row:"+row+"|Col:"+col+"|Probability:"+probability.toFixed(2)+"%|Action:"+action
            output.appendChild(entry)

            console.log(row+(width*col))
            //adding glow tag to the according tiles
            if(action == 'flag'){
                document.getElementById(row+(width*col)).classList.add('flag_glow')
            }
            else if (action == 'open'){
                document.getElementById(row+(width*col)).classList.add('open_glow')
            }


        }
    }

    function postRequest(gamestate){
        AI_Solver.visibility = 'hidden'
        const requestObj = new XMLHttpRequest()
        requestObj.onreadystatechange = function(){
            if(this.readyState == 4 && this.status == 200){
                console.log(this.responseText)
                getRequest()
            }
            
        }

        requestObj.open("POST", '/projects/minesweeper/post')
        csrftoken = getCookie('csrftoken')
        requestObj.setRequestHeader('X-CSRFToken',csrftoken)


        const formdata = new FormData()
        formdata.append('gamestate',gamestate)

        requestObj.send(formdata)
    }


    /*
    this will work in multiple steps.
    1. sends a POST request to the server
        then javascript will listen (timeout of 30s) for the response/get request
    2. the server will then react by gathering the game state to a string
    3. then python/django will compile and run the C++ script
        -note: its easier to compile C+ scripts in python than it is in JS so we're proceeding it this way
    4. Once the script is finished it will then store the data in the backend
    5. The finished data will then be gathered through the get request
    */

    //used to run solver
    function runSolver(){
        if(!isGameOver && isGameStarted){
            postRequest(getString())
            eraseOutput()
        }
    }

    function eraseOutput(){
        var child = output.lastElementChild
        while(child){
            output.removeChild(child)
            child = output.lastElementChild
        }
    }
    


    createBoard();
})

