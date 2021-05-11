function togglePasswordVisibility() {
    var pass = document.getElementById("password");
    if (pass != null)
    if (pass.type == "password") {
        pass.type = "text";
    } else {
        pass.type = "password";
    }
}