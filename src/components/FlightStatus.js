// src/components/FlightStatus.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import './FlightStatus.css';

const FlightStatus = () => {
  const [flights, setFlights] = useState([]);
  const socket = io('http://localhost:5000', {
    transports: ['websocket', 'polling']
  });

  useEffect(() => {
    const fetchFlights = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/flights');
        setFlights(response.data);
      } catch (error) {
        console.error('Error fetching flights:', error);
      }
    };

    fetchFlights();

    socket.on('flight_update', (updatedFlight) => {
      setFlights((prevFlights) =>
        prevFlights.map((flight) =>
          flight.id === updatedFlight.id ? updatedFlight : flight
        )
      );
    });

    return () => socket.disconnect();
  }, [socket]);

  return (
    <div className="flight-status-container">
      <h1>Flight Status</h1>
      <div className="flight-list">
        {flights.map((flight) => (
          <div key={flight.id} className="flight-card">
            <p><strong>Flight:</strong> {flight.flight_iata}</p>
            <p><strong>Status:</strong> {flight.flight_status}</p>
            <p><strong>Gate:</strong> {flight.gate}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FlightStatus;
