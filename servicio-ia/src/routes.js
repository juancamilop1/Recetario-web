const express = require('express');
const { sugerirReceta, generarPreparacion } = require('./gemini');

const router = express.Router();

/**
 * @openapi
 * /health:
 *   get:
 *     tags: [Salud]
 *     summary: Estado del microservicio
 *     responses:
 *       200:
 *         description: Servicio en ejecución
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: ok
 *                 service:
 *                   type: string
 *                   example: recetario-servicio-ia
 *                 geminiConfigured:
 *                   type: boolean
 */
router.get('/health', (_req, res) => {
  const key = process.env.GEMINI_API_KEY;
  res.json({
    status: 'ok',
    service: 'recetario-servicio-ia',
    geminiConfigured: Boolean(key && key !== 'TU_API_KEY_AQUI'),
  });
});

/**
 * @openapi
 * /api/sugerir-receta:
 *   post:
 *     tags: [IA]
 *     summary: Sugerir una receta completa con IA
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               ingredientes:
 *                 type: string
 *                 example: pollo, arroz, cebolla
 *               categoria:
 *                 type: string
 *                 example: almuerzo
 *               preferencias:
 *                 type: string
 *                 example: poca grasa, 30 minutos
 *     responses:
 *       200:
 *         description: Receta sugerida
 *       400:
 *         description: Datos inválidos
 *       503:
 *         description: IA no configurada o no disponible
 */
router.post('/api/sugerir-receta', async (req, res) => {
  try {
    const { ingredientes, categoria, preferencias } = req.body || {};
    if (!ingredientes && !categoria && !preferencias) {
      return res.status(400).json({
        error: 'Indica al menos ingredientes, categoría o preferencias.',
      });
    }
    const data = await sugerirReceta({ ingredientes, categoria, preferencias });
    res.json({ ok: true, fuente: 'gemini', data });
  } catch (err) {
    console.error('sugerir-receta:', err);
    const status = err.status && err.status >= 400 ? err.status : 503;
    res.status(status).json({ ok: false, error: err.message || 'Error al consultar IA' });
  }
});

/**
 * @openapi
 * /api/generar-preparacion:
 *   post:
 *     tags: [IA]
 *     summary: Generar pasos de preparación con IA
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [nombre, ingredientes]
 *             properties:
 *               nombre:
 *                 type: string
 *               ingredientes:
 *                 type: string
 *               categoria:
 *                 type: string
 *     responses:
 *       200:
 *         description: Preparación generada
 *       400:
 *         description: Faltan campos
 *       503:
 *         description: IA no configurada o no disponible
 */
router.post('/api/generar-preparacion', async (req, res) => {
  try {
    const { nombre, ingredientes, categoria } = req.body || {};
    if (!nombre || !ingredientes) {
      return res.status(400).json({
        error: 'nombre e ingredientes son obligatorios.',
      });
    }
    const data = await generarPreparacion({ nombre, ingredientes, categoria });
    res.json({ ok: true, fuente: 'gemini', data });
  } catch (err) {
    console.error('generar-preparacion:', err);
    const status = err.status && err.status >= 400 ? err.status : 503;
    res.status(status).json({ ok: false, error: err.message || 'Error al consultar IA' });
  }
});

module.exports = router;
