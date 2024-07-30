import React, { useEffect, useState } from 'react';
import axios from 'axios';

const UserSettings = ({ userId }) => {
  const [notifications, setNotifications] = useState(true);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/users/${userId}/settings`);
        setNotifications(response.data.notifications);
      } catch (error) {
        console.error('Error fetching settings:', error);
      }
    };

    fetchSettings();
  }, [userId]);

  const handleSave = async () => {
    try {
      await axios.put(`http://localhost:5000/api/users/${userId}/settings`, {
        notifications,
      });
      alert('Settings saved');
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  };

  return (
    <div>
      <h2>User Settings</h2>
      <label>
        <input
          type="checkbox"
          checked={notifications}
          onChange={() => setNotifications(!notifications)}
        />
        Enable Notifications
      </label>
      <button onClick={handleSave}>Save</button>
    </div>
  );
};

export default UserSettings;
