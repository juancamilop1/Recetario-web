require('dotenv').config();

const express = require('express');
const cors = require('cors');
const swaggerUi = require('swagger-ui-express');
const swaggerSpec = require('./swagger');
const routes = require('./routes');

const app = express();
const PORT = Number(process.env.PORT || 3000);

app.use(cors());
app.use(express.json({ limit: '1mb' }));

app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec, {
  customSiteTitle: 'Recetario IA — Swagger',
}));
app.get('/api-docs.json', (_req, res) => res.json(swaggerSpec));

app.use(routes);

app.use((err, _req, res, _next) => {
  console.error(err);
  res.status(500).json({ ok: false, error: 'Error interno del microservicio' });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`servicio-ia escuchando en :${PORT}`);
  console.log(`Swagger UI: http://localhost:${PORT}/api-docs`);
});
