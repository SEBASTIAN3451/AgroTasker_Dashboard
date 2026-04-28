// Módulo de Reportes y Exportación
const ReportGenerator = {
    generatePDF() {
        const html = `
        <html>
        <head><meta charset="utf-8"><title>Reporte AgroTasker</title></head>
        <body style="font-family: Arial; padding: 20px;">
            <h1>📋 REPORTE DE MONITOREO AGROTASKER</h1>
            <p><strong>Fecha:</strong> ${new Date().toLocaleString('es-MX')}</p>
            <p><strong>Cultivo:</strong> Mango</p>
            <hr>
            
            <h2>Datos Actuales de Sensores</h2>
            <table border="1" cellpadding="10" style="width: 100%; border-collapse: collapse;">
                <tr style="background: #f0f0f0;">
                    <th>Parámetro</th>
                    <th>Valor</th>
                    <th>Rango Óptimo</th>
                    <th>Estado</th>
                </tr>
                <tr>
                    <td>Humedad Suelo</td>
                    <td id="rep-humedad">--</td>
                    <td>40-60%</td>
                    <td id="rep-humedad-status">--</td>
                </tr>
                <tr>
                    <td>pH Suelo</td>
                    <td id="rep-ph">--</td>
                    <td>5.5-7.0</td>
                    <td id="rep-ph-status">--</td>
                </tr>
                <tr>
                    <td>Temperatura</td>
                    <td id="rep-temp">--</td>
                    <td>24-30°C</td>
                    <td id="rep-temp-status">--</td>
                </tr>
            </table>
            
            <h2>Recomendaciones</h2>
            <ul id="rep-recomendaciones"></ul>
            
            <h2>Próximas Actividades</h2>
            <ul id="rep-tareas"></ul>
        </body>
        </html>`;
        
        const printWindow = window.open('', '', 'width=800,height=600');
        printWindow.document.write(html);
        printWindow.document.close();
        printWindow.print();
    },

    exportToCSV() {
        const data = localStorage.getItem('sensorHistory') || '{}';
        const csv = 'Fecha,Humedad,Temperatura,pH\n' + 
                    JSON.parse(data).map(d => `${d.date},${d.humidity},${d.temp},${d.ph}`).join('\n');
        const blob = new Blob([csv], {type: 'text/csv'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'agrotasker-datos.csv';
        a.click();
    }
};
