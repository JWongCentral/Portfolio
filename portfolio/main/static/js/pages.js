
//uses the intersection observer to add in show/hide tags to the div
//if it is in view, then we can finish off the page/scrolling transition in css
const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        console.log(entry);
        if(entry.isIntersecting){
            entry.target.classList.add('show');
        } else {
            entry.target.classList.remove('show');
        }
    });
});


const hiddenElements = document.querySelectorAll(".page");
hiddenElements.forEach((el) => {
    observer.observe(el)
})
console.log(hiddenElements);
