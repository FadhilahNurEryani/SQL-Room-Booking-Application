// Scroll Top Button

function showScrollTop(){
    if (document.body.scrollTop > 400 || document.documentElement.scrollTop > 400){
        document.getElementById('scrollTop').style.opacity = '1';
        document.getElementById('scrollTop').style.visibility = 'visible';
    } else{
        document.getElementById('scrollTop').style.opacity = '0';
        document.getElementById('scrollTop').style.visibility = 'hidden'; 
    }
}

window.addEventListener('scroll', showScrollTop)

function scrollToTop(){
    window.scrollTo(0,0);
}

// Navbar Toggle 
let navigation = document.querySelector('nav');
let navMenu = document.querySelector('.nav-menu');
let navClose = document.getElementById('nav-close');
let navToggle = document.getElementById('nav-toggle');
let overlay = document.querySelector('.overlay')

function showNav(){
    navToggle.style.display = 'none';
    navMenu.classList.add('open');
    overlay.style.opacity = '1';
}

function hideNav(){
    navToggle.style.display = 'inline-flex';
    navMenu.classList.remove('open');
    overlay.style.opacity = '0';
}


// Navbar change on scroll to colour

function changeHoverColor(newColor) {
    const root = document.documentElement;
    root.style.setProperty('--nav-hover-color', newColor);
}

let nav = document.querySelector('nav');

function changeHeader() {
    if (document.body.scrollTop > 50) {
        nav.classList.add('change-header');
        changeHoverColor('#ffff');


    } else if (document.documentElement.scrollTop > 50) {
        nav.classList.add('change-header');
        changeHoverColor('#ffff');
    }
    else {
        nav.classList.remove('change-header');
        changeHoverColor('#0065b9');
    }
}
window.addEventListener('scroll', changeHeader)



// Slide In Animations

const inViewport = (entries, observer) => {
    entries.forEach(entry => {
        entry.target.classList.toggle('is-inViewport', entry.isIntersecting);
    })
}

const Obs = new IntersectionObserver(inViewport);
const obsOptions = {};

const ELs_inViewport = document.querySelectorAll('[data-inViewport]');
ELs_inViewport.forEach(EL => {
    Obs.observe(EL, obsOptions);
});

function homeRedir(){
    window.location.href = "/";

}

// Password Visible Toggle

const password = document.getElementById('password')
const toggle = document.querySelector('.ri-eye-off-line')

toggle.addEventListener("click", () =>{
    if(password.type ==="password"){
      password.type = "text";
      toggle.classList.replace("ri-eye-off-line","ri-eye-line");
    }else{
      password.type = "password";
      toggle.classList.replace("ri-eye-line","ri-eye-off-line");
    }
})

document.addEventListener("DOMContentLoaded", function() {
    const oldPasswordToggle = document.querySelector('.oldpasswordtoggle')
    const newPasswordToggle = document.querySelector('.newpasswordtoggle')
    const confirmToggle = document.querySelector('.confirmtoggle')
    const delpasswordToggle = document.querySelector('.delpasswordtoggle')

    function toggleVisibility(fieldId, toggleButton) {
        const field = document.getElementById(fieldId)
        if(field.type === "password"){
            field.type = "text";
            toggleButton.classList.replace("ri-eye-off-line", "ri-eye-line");
        }else{
            field.type = "password";
            toggleButton.classList.replace("ri-eye-line", "ri-eye-off-line");
        }
    }

    oldPasswordToggle.addEventListener("click", () => {
        toggleVisibility('oldpassword', oldPasswordToggle)
    });

    newPasswordToggle.addEventListener("click", () => {
        toggleVisibility('newpassword', newPasswordToggle)
    });

    confirmToggle.addEventListener("click", () => {
        toggleVisibility('confirm', confirmToggle)
    });

    delpasswordToggle.addEventListener("click", () => {
        toggleVisibility('delpassword', delpasswordToggle)
    });

});





// Auto Submit Location Form

function submitForm() {
    document.querySelector('.locations').submit();
}

function submitForm1() {
    document.querySelector('.bookingcategories').submit();
}





