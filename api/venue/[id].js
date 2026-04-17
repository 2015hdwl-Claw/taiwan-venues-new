/**
 * GET /api/venue/[id] — 單一場地結構化 Markdown
 * 供 LLM 和外部工具直接消費
 */
const fs = require('fs');
const path = require('path');

module.exports = async (req, res) => {
  try {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Cache-Control', 'public, max-age=86400');

    if (req.method === 'OPTIONS') return res.status(204).end();
    if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' });

    const { id } = req.query;
    if (!id || !/^\d+$/.test(id)) {
      return res.status(400).json({ error: 'Invalid venue ID. Use numeric ID, e.g. /api/venue/1072' });
    }

    const bundle = JSON.parse(
      fs.readFileSync(path.join(__dirname, '..', 'wiki_bundle.json'), 'utf-8')
    );

    const venue = bundle.venues[id];
    if (!venue) {
      return res.status(404).json({
        error: `Venue ${id} not found`,
        availableIds: Object.keys(bundle.venues).sort((a, b) => +a - +b)
      });
    }

    res.setHeader('Content-Type', 'text/markdown; charset=utf-8');
    res.status(200).send(venue.content);
  } catch (err) {
    console.error('venue/[id] API error:', err);
    res.status(500).json({ error: 'Failed to load venue data' });
  }
};
