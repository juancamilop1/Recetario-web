const { GoogleGenerativeAI } = require('@google/generative-ai');

const DEFAULT_MODEL = 'gemini-3.5-flash-lite';
const DEPRECATED_MODELS = new Set([
  'gemini-1.5-flash',
  'gemini-1.5-flash-lite',
  'gemini-1.5-pro',
  'gemini-2.0-flash',
  'gemini-2.5-flash',
  'gemini-2.5-flash-lite',
]);

function resolveModelName() {
  let modelName = (process.env.GEMINI_MODEL || DEFAULT_MODEL).trim();
  if (DEPRECATED_MODELS.has(modelName)) {
    console.warn(`GEMINI_MODEL=${modelName} obsoleto; usando ${DEFAULT_MODEL}`);
    modelName = DEFAULT_MODEL;
  }
  return modelName;
}

function getModel() {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey || apiKey === 'TU_API_KEY_AQUI') {
    const err = new Error(
      'GEMINI_API_KEY no configurada. Define la variable de entorno con tu clave de Google AI Studio.'
    );
    err.status = 503;
    throw err;
  }
  const genAI = new GoogleGenerativeAI(apiKey);
  return genAI.getGenerativeModel({ model: resolveModelName() });
}

async function sugerirReceta({ ingredientes, categoria, preferencias }) {
  const model = getModel();
  const prompt = `
Eres un asistente de cocina. Responde SOLO en español y en JSON válido (sin markdown) con esta forma:
{
  "nombre": "string",
  "categoria": "string",
  "ingredientes": "string (lista legible)",
  "preparacion": "string (pasos numerados)"
}

Datos del usuario:
- Ingredientes disponibles: ${ingredientes || 'no especificados'}
- Categoría deseada: ${categoria || 'libre'}
- Preferencias: ${preferencias || 'ninguna'}

Genera una receta práctica y clara.
`.trim();

  const result = await model.generateContent(prompt);
  const text = result.response.text().trim();
  return parseJsonResponse(text);
}

async function generarPreparacion({ nombre, ingredientes, categoria }) {
  const model = getModel();
  const prompt = `
Eres un asistente de cocina. Responde SOLO en español y en JSON válido (sin markdown) con esta forma:
{
  "preparacion": "string (pasos numerados claros)",
  "tips": "string (consejos breves)"
}

Receta:
- Nombre: ${nombre || 'Sin nombre'}
- Categoría: ${categoria || 'General'}
- Ingredientes: ${ingredientes || 'no especificados'}

Genera la preparación paso a paso.
`.trim();

  const result = await model.generateContent(prompt);
  const text = result.response.text().trim();
  return parseJsonResponse(text);
}

function parseJsonResponse(text) {
  const cleaned = text.replace(/^```json\s*/i, '').replace(/^```\s*/i, '').replace(/\s*```$/, '');
  try {
    return JSON.parse(cleaned);
  } catch {
    return { raw: text };
  }
}

module.exports = { sugerirReceta, generarPreparacion, resolveModelName };
