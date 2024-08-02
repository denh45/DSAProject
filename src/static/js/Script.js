const signUpButton = document.getElementById("signUp");
const signInButton = document.getElementById("signIn");
const container = document.getElementById("container");

signUpButton.addEventListener("click", () => {
  container.classList.add("right-panel-active");
});

signInButton.addEventListener("click", () => {
  container.classList.remove("right-panel-active");
});

const password = document.getElementById("password");

document.getElementById("showPassword").addEventListener("click", () => {
  const type = password.type;
  if (type === "password") {
    password.type = "text";
  } else {
    password.type = "password";
  }
});

// function eee(a){
//   console.log(')
// }

// let a = () => {

// }

// class wdd{
//   constructor(){

//   }

// }
