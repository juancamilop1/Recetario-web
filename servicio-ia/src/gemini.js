const { GoogleGenerativeAI } = require('@google/generative-ai');

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
  const modelName = process.env.GEMINI_MODEL || 'gemini-3.5-flash-lite';
  return genAI.getGenerativeModel({ model: modelName });
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

module.exports = { sugerirReceta, generarPreparacion };
