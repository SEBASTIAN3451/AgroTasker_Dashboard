const express = require('express');
const cors = require('cors');
const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http);

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Almacenamiento temporal de datos
let sensorData = {
    ph: [],
    temperatura: [],
    humedad: []
};

// Ruta para recibir datos del ESP32
app.post('/api/sensors', (req, res) => {
    const { sensor, value } = req.body;
    
    // Guardar datos
    if (sensorData[sensor]) {
        sensorData[sensor].push({
            value: parseFloat(value),
            timestamp: new Date()
        });
        
        // Mantener solo los últimos 100 datos
        if (sensorData[sensor].length > 100) {
            sensorData[sensor].shift();
        }
        
        // Emitir nuevos datos a todos los clientes conectados
        io.emit('sensor-update', { sensor, value });
        
        res.json({ success: true });
    } else {
        res.status(400).json({ error: 'Sensor no válido' });
    }
});

// Ruta para obtener todos los datos
app.get('/api/data', (req, res) => {
    res.json(sensorData);
});

// Socket.IO connection handling
io.on('connection', (socket) => {
    console.log('Cliente conectado');
    // Enviar datos actuales al nuevo cliente
    socket.emit('initial-data', sensorData);
});

const PORT = process.env.PORT || 3000;
http.listen(PORT, () => {
    console.log(`Servidor corriendo en puerto ${PORT}`);
});