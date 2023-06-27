
//uses the intersection observer to add in show/hide tags to the div
//if it is in view, then we can finish off the page/scrolling transition in css
const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        console.log(entry.target.classList);
        if(entry.isIntersecting){
            entry.target.classList.add('show');
            entry.target.classList.remove('hide');
            if(entry.target.classList.contains("one")){
                home = document.querySelector(".home")
                home.classList.add("active-page")
                console.log(home)
            }
            else if(entry.target.classList.contains("two")){
                expertise = document.querySelector(".expertise")
                expertise.classList.add("active-page")
                
            }
            else if(entry.target.classList.contains("three")){
                projects = document.querySelector(".projects")
                projects.classList.add("active-page")
            }
            else if(entry.target.classList.contains("four")){
                contact = document.querySelector(".contact")
                contact.classList.add("active-page")
            }
        } else {
            entry.target.classList.remove('show');
            if(entry.target.classList.contains("one")){
                home = document.querySelector(".home")
                home.classList.remove("active-page")
            }
            else if(entry.target.classList.contains("two")){
                expertise = document.querySelector(".expertise")
                expertise.classList.remove("active-page")
                
            }
            else if(entry.target.classList.contains("three")){
                projects = document.querySelector(".projects")
                projects.classList.remove("active-page")
            }
            else if(entry.target.classList.contains("four")){
                contact = document.querySelector(".contact")
                contact.classList.remove("active-page")
            }
        }
    });
});


const hiddenElements = document.querySelectorAll(".page");
hiddenElements.forEach((el) => {
    observer.observe(el)
})
