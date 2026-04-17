/**
 * GET /api/concepts — List available concept pages
 */
const fs = require('fs');
const path = require('path');

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Cache-Control', 'public, max-age=3600');

  if (req.method === 'OPTIONS') return res.status(204).end();

  const bundle = JSON.parse(
    fs.readFileSync(path.join(__dirname, '..', '..', 'wiki_bundle.json'), 'utf-8')
  );

  const concepts = Object.keys(bundle.concepts || {});
  res.status(200).json({ total: concepts.length, concepts });
};
