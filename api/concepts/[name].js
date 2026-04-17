/**
 * GET /api/concepts/[name] — 概念頁面 Markdown
 * 供 LLM 和外部工具直接消費
 *
 * 可用概念：台北場地推薦、外燴規定總覽、大型場地推薦、小型會議室推薦、挑高空間對比
 */
const fs = require('fs');
const path = require('path');

const CONCEPT_NAMES = [
  '台北場地推薦', '外燴規定總覽', '大型場地推薦', '小型會議室推薦', '挑高空間對比'
];

const CONCEPT_ALIASES = {
  'taipei': '台北場地推薦',
  'catering': '外燴規定總覽',
  'large': '大型場地推薦',
  'small': '小型會議室推薦',
  'high-ceiling': '挑高空間對比',
  'highceiling': '挑高空間對比',
  'budget': '小型會議室推薦',
};

module.exports = async (req, res) => {
  try {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Cache-Control', 'public, max-age=86400');

    if (req.method === 'OPTIONS') return res.status(204).end();
    if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' });

    const { name } = req.query;
    if (!name) {
      return res.status(200).json({
        concepts: CONCEPT_NAMES,
        usage: '/api/concepts/{name}',
        examples: [
          '/api/concepts/台北場地推薦',
          '/api/concepts/挑高空間對比',
          '/api/concepts/large'
        ]
      });
    }

    const bundle = JSON.parse(
      fs.readFileSync(path.join(__dirname, '..', 'wiki_bundle.json'), 'utf-8')
    );

    let conceptName = CONCEPT_ALIASES[name.toLowerCase()] || name;

    if (!bundle.concepts[conceptName]) {
      return res.status(404).json({
        error: `Concept "${name}" not found`,
        availableConcepts: CONCEPT_NAMES,
        aliases: Object.entries(CONCEPT_ALIASES).map(([k, v]) => `${k} → ${v}`)
      });
    }

    res.setHeader('Content-Type', 'text/markdown; charset=utf-8');
    res.status(200).send(bundle.concepts[conceptName].content);
  } catch (err) {
    console.error('concepts/[name] API error:', err);
    res.status(500).json({ error: 'Failed to load concept data' });
  }
};
