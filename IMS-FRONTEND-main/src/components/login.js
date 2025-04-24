import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./login.css";
import logo from "../assets/bleu_logo1.jpg";
import coffeeImage from "../assets/Coffee/CaramelMachiatto.jpg";

const Login = () => {
  const [credentials, setCredentials] = useState({ username: "", password: "" });
  const [passwordVisible, setPasswordVisible] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      // Use URLSearchParams to format the body for 'application/x-www-form-urlencoded'
      const formData = new URLSearchParams();
      formData.append("username", credentials.username);
      formData.append("password", credentials.password);

      const response = await fetch("http://localhost:8000/auth/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData.toString(),  // Send data in the correct format
      });

      const data = await response.json();

      if (response.ok) {
        alert("Login successful!");
        
        // Decode the JWT token to check user role
        const decodedToken = JSON.parse(atob(data.access_token.split('.')[1]));  // Decode the token
        const userRole = decodedToken.role;

        // Navigate based on the user role
      if (userRole === 'admin') {
        navigate("/admin-home");  // Corrected the route to '/admin-home'
      } else if (userRole === 'manager') {
        navigate("/manager-home");  // Navigate to Manager homepage
      } else {
        alert("Role not recognized.");
      }
    } else {
      alert(data.message || "Login failed. Please check your credentials.");
    }
  } catch (error) {
    console.error("Login error:", error);
    alert("An error occurred. Please try again later.");
  }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-box">
          <img src={logo} alt="Bleu Bean Cafe" className="logo" />
          <h2>Welcome Back</h2>
          <p>Please Enter Your Details To Log In.</p>

          <form onSubmit={handleLogin}>
            <label>Username</label>
            <input
              type="text"
              placeholder="Enter your username"
              value={credentials.username}
              onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
            />

            <label>Password</label>
            <div className="password-container">
              <input
                type={passwordVisible ? "text" : "password"}
                placeholder="Enter your password"
                value={credentials.password}
                onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
              />
              <span
                className="eye-icon material-symbols-outlined"
                onClick={() => setPasswordVisible(!passwordVisible)}
              >
                {passwordVisible ? "visibility_off" : "visibility"}
              </span>
            </div>

            <div className="remember-me">
              <input type="checkbox" id="remember" />
              <label htmlFor="remember">Remember Me</label>
            </div>

            <button type="submit">Log In</button>

            <p className="forgot-password">
              Forgot Password? <Link to="/reset-password">Reset Here</Link>
            </p>
          </form>
        </div>
      </div>

      <div className="image-container">
        <img src={coffeeImage} alt="Caramel Macchiato" className="coffee-image" />
      </div>
    </div>
  );
};

export default Login;
