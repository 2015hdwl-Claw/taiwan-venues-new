/**
 * GET /api/venues — 場地精簡列表（< 20KB）
 * 供 LLM 和外部工具直接消費
 */
const fs = require('fs');
const path = require('path');

module.exports = async (req, res) => {
  try {
    // CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Cache-Control', 'public, max-age=3600');

    if (req.method === 'OPTIONS') {
      return res.status(204).end();
    }

    const venues = JSON.parse(
      fs.readFileSync(path.join(__dirname, '..', 'venues.json'), 'utf-8')
    );

    // 只回傳精簡欄位，控制在 20KB 以內
    const compact = venues
      .filter(v => v.status !== 'inactive' && v.status !== 'archived')
      .map(v => ({
        id: v.id,
        name: v.name,
        city: v.city,
        venueType: v.venueType || '',
        address: v.address || '',
        maxCapacity: (v.rooms || []).reduce((max, r) => {
          const caps = r.capacity || {};
          return Math.max(max,
            caps.theater || 0, caps.banquet || 0,
            caps.classroom || 0, caps.ushape || 0
          );
        }, 0),
        roomCount: (v.rooms || []).length,
        halfDayPrice: v.pricing?.halfDay || v.priceHalfDay || null,
        fullDayPrice: v.pricing?.fullDay || v.priceFullDay || null,
        topEquipment: (v.equipment || []).slice(0, 5),
        url: `https://taiwan-venues-new-indol.vercel.app/venues/${v.id}`
      }));

    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.status(200).json({
      total: compact.length,
      updated: '2026-04-17',
      venues: compact
    });
  } catch (err) {
    console.error('venues API error:', err);
    res.status(500).json({ error: 'Failed to load venues data' });
  }
};
