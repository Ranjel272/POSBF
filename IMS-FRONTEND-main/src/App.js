import React from "react";
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import Login from "./components/login";
import ResetPassword from "./components/ResetPassword";
import Ahomepage from "./components/Ahomepage";
import Shomepage from "./components/Shomepage";
import Mhomepage from "./components/Mhomepage";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/login" element={<Login />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/admin-home" element={<Ahomepage />} />
        <Route path="/staff-home" element={<Shomepage />} />
        <Route path="/manager-home" element={<Mhomepage />} />
      </Routes>
    </Router>
  );
};

export default App;
