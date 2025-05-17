document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("login-form");
  
    form.addEventListener("submit", (e) => {
      e.preventDefault(); // Prevent form reload
  
      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;
      const sheetId = document.getElementById("sheet-id").value;
  
      if (!email || !password || !sheetId) {
        alert("Please fill out all fields.");
        return;
      }
  
      // Log or save input values
      console.log("Email:", email);
      console.log("Password:", password);
      console.log("Google Sheet ID:", sheetId);
  
      alert("Submitted successfully!");
    });
  });
  