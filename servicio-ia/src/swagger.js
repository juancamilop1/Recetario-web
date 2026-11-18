const swaggerJsdoc = require('swagger-jsdoc');

const options = {
  definition: {
    openapi: '3.0.3',
    info: {
      title: 'Recetario — Microservicio IA',
      version: '1.0.0',
      description:
        'API Node.js para sugerencias de recetas y generación de preparación mediante IA (Google Gemini). Consumida por Django.',
    },
    servers: [
      { url: '/', description: 'Servidor actual' },
    ],
    tags: [
      { name: 'Salud', description: 'Estado del servicio' },
      { name: 'IA', description: 'Operaciones con inteligencia artificial' },
    ],
  },
  apis: ['./src/routes.js'],
};

module.exports = swaggerJsdoc(options);
