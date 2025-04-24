import React, { useState } from "react";
import { Link } from "react-router-dom"; // Import Link
import "./ResetPassword.css";
import logo from "../assets/bleu_logo1.jpg";
import coffeeImage from "../assets/Coffee/CaramelMachiatto.jpg";

const ResetPassword = () => {
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [confirmPasswordVisible, setConfirmPasswordVisible] = useState(false);

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-box">
          <img src={logo} alt="Bleu Bean Cafe" className="logo" />
          <h2>Reset Password</h2>
          <p>Please Enter And Confirm Your New Password To Continue.</p>

          <form>
            <label>Username</label>
            <input type="text" placeholder="Enter your username" />

            <label>New Password</label>
            <div className="password-container">
              <input
                type={passwordVisible ? "text" : "password"}
                placeholder="Enter new password"
              />
              <span
                className="eye-icon material-symbols-outlined"
                onClick={() => setPasswordVisible(!passwordVisible)}
              >
                {passwordVisible ? "visibility_off" : "visibility"}
              </span>
            </div>

            <label>Confirm New Password</label>
            <div className="password-container">
              <input
                type={confirmPasswordVisible ? "text" : "password"}
                placeholder="Confirm your new password"
              />
              <span
                className="eye-icon material-symbols-outlined"
                onClick={() => setConfirmPasswordVisible(!confirmPasswordVisible)}
              >
                {confirmPasswordVisible ? "visibility_off" : "visibility"}
              </span>
            </div>

            <button type="submit">Reset Password</button>

            {/* Updated navigation to login */}
            <p className="forgot-password">
              Access Your Account? Go Back To <Link to="/">Sign In</Link> {/* Updated Link */}
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

export default ResetPassword;
