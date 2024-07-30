import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import FlightStatus from './components/FlightStatus';
import Register from './components/Register';
import UserSettings from './components/UserSetting';
import { Link } from 'react-router-dom';
import './App.css'; // Add this line to import the CSS file

const App = () => {
  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li>
              <Link to="/register">Register</Link>
            </li>
            <li>
              <Link to="/settings/1">Settings</Link> {/* Example userId */}
            </li>
          </ul>
        </nav>
        <Routes>
          <Route path="/" element={<FlightStatus />} />
          <Route path="/register" element={<Register />} />
          <Route path="/settings/:userId" element={<UserSettings />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
