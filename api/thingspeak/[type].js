// Vercel serverless: /api/thingspeak/[type]
const CHANNELS = {
soil: { id: 2791076 },
weather: { id: 2791069 },
matric_uv: { id: 2906294 },
matric: { id: 2906294 },
};

export default async function handler(req, res) {
try {
const { type } = req.query;
const ch = CHANNELS[type];
if (!ch) return res.status(404).json({ error: Unknown type: ${type} });
const results = Number(req.query.results || 60);
let url = https://api.thingspeak.com/channels/${ch.id}/feeds.json?results=${results};
const r = await fetch(url, { headers: { Accept: 'application/json' } });
const data = await r.json();
res.setHeader('Cache-Control', 's-maxage=10, stale-while-revalidate=59');
res.setHeader('Access-Control-Allow-Origin', '*');
res.status(r.status).json(data);
} catch (e) {
res.status(500).json({ error: 'Proxy error', details: String(e) });
}
}
