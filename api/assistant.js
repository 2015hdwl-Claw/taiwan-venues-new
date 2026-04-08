/**
 * Vercel Serverless Function: AI Assistant for Taiwan Venues
 *
 * RAG Pipeline:
 * 1. Accept user query
 * 2. Search for relevant chunks (embeddings or keyword fallback)
 * 3. Construct context from top-k chunks
 * 4. Call LLM (GLM-4.7-flash via Z.AI API)
 * 5. Return response with sources
 */

const { keywordSearch } = require('./lib/search');

// Embeddings data (loaded at build time)
let embeddingsData = null;

function loadEmbeddings() {
  if (!embeddingsData) {
    const fs = require('fs');
    const path = require('path');
    const embeddingsPath = path.join(process.cwd(), 'ai_knowledge_base', 'embeddings.json');
    if (fs.existsSync(embeddingsPath)) {
      const content = fs.readFileSync(embeddingsPath, 'utf-8');
      embeddingsData = JSON.parse(content);
    }
  }
  return embeddingsData;
}

/**
 * Compute cosine similarity between two vectors
 */
function cosineSimilarity(a, b) {
  if (!a || !b || a.length !== b.length) return 0;
  let dotProduct = 0;
  let normA = 0;
  let normB = 0;
  for (let i = 0; i < a.length; i++) {
    dotProduct += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

/**
 * Search for most similar chunks
 */
function searchSimilarChunks(queryEmbedding, topK = 5, threshold = 0.5) {
  const data = loadEmbeddings();
  if (!data || !data.embeddings) return [];

  const results = data.embeddings
    .map(chunk => ({
      ...chunk,
      score: cosineSimilarity(queryEmbedding, chunk.embedding)
    }))
    .filter(chunk => chunk.score >= threshold)
    .sort((a, b) => b.score - a.score)
    .slice(0, topK);

  return results;
}

/**
 * Generate embedding using OpenAI API
 */
async function generateEmbedding(text, apiKey) {
  const response = await fetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`
    },
    body: JSON.stringify({
      model: 'text-embedding-3-small',
      input: text
    })
  });

  if (!response.ok) {
    throw new Error(`OpenAI API error: ${response.status}`);
  }

  const data = await response.json();
  return data.data[0].embedding;
}

/**
 * Call LLM via z.ai Anthropic-compatible endpoint
 * Coding Plan Pro only supports /api/anthropic/ endpoint
 */
async function callLLM(systemPrompt, userMessage, apiKey) {
  const response = await fetch('https://api.z.ai/api/anthropic/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1024,
      system: systemPrompt,
      messages: [
        { role: 'user', content: userMessage }
      ]
    })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`z.ai API error: ${response.status} - ${error}`);
  }

  const data = await response.json();
  // Anthropic format: content[0].text
  return data.content[0].text;
}

/**
 * Build system prompt
 */
function buildSystemPrompt() {
  return `你是「活動大師」的 AI 場地顧問，專門協助活動企劃人員解決場地相關問題。

## 核心原則

1. **嚴格基於知識庫回答**：只能使用提供的參考資料回答問題，絕對不可編造或推測資訊。
2. **誠實面對未知**：如果知識庫中沒有相關資訊，必須明確說「抱歉，知識庫目前沒有這方面的資訊」。
3. **引用來源**：每個回答都必須標註資料來源（場地名稱 + 資料類型）。
4. **繁體中文**：所有回答使用繁體中文。

## 回答格式

### 當有相關資訊時：
**回答**：[基於參考資料的回答]

**資料來源**：
- [場地名稱] - [資料類型，如：餐飲規定、進撤場規定]

### 當沒有相關資訊時：
**回答**：抱歉，知識庫目前沒有這方面的資訊。建議您直接聯繫場地方確認。

**建議行動**：
- 您可以透過本平台生成詢問信，我們會協助您向場地方查詢。

## 禁止事項

- 不可編造任何未在參考資料中出現的數據、價格、規定
- 不可猜測場地的服務內容
- 不可給出未經證實的建議
- 不可使用「應該」、「可能」、「或許」等不確定語句描述具體規定`;
}

/**
 * Build user message with context
 */
function buildUserMessage(query, chunks) {
  let message = `用戶問題：${query}\n\n`;

  if (chunks.length === 0) {
    message += `參考資料：（無相關資料）`;
  } else {
    message += `參考資料：\n\n`;
    chunks.forEach((chunk, i) => {
      message += `[資料 ${i + 1}] ${chunk.venue_name} - ${chunk.field_path}\n`;
      message += `${chunk.text}\n`;
      message += `（信心度：${(chunk.score * 100).toFixed(0)}%，資料狀態：${chunk.confidence}）\n\n`;
    });
  }

  return message;
}

/**
 * Main handler
 */
export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { query, venueId } = req.body;

    if (!query || typeof query !== 'string') {
      return res.status(400).json({ error: 'Missing or invalid query' });
    }

    // Get API keys from environment
    const openaiApiKey = process.env.OPENAI_API_KEY;
    const glmApiKey = process.env.GLM_API_KEY || process.env.CLASSIFIER_API_KEY;

    if (!glmApiKey) {
      return res.status(500).json({ error: 'GLM API key not configured' });
    }

    let similarChunks = [];
    let searchMethod = 'none';

    // Step 1: Try embeddings search first (if available)
    const data = loadEmbeddings();
    if (data && data.embeddings && openaiApiKey) {
      try {
        const queryEmbedding = await generateEmbedding(query, openaiApiKey);
        similarChunks = searchSimilarChunks(queryEmbedding, 5, 0.3);
        searchMethod = 'embeddings';
      } catch (e) {
        console.error('Embeddings search failed:', e.message);
      }
    }

    // Step 2: Fallback to keyword search if embeddings not available or no results
    if (similarChunks.length === 0) {
      similarChunks = keywordSearch(query, { venueId, topK: 5 });
      searchMethod = 'keyword';

      // Normalize keyword results to match embeddings format
      similarChunks = similarChunks.map(r => ({
        venue_id: r.venueId,
        venue_name: r.venueName,
        field_path: `${r.category}.${r.type}`,
        text: r.text,
        fullText: r.fullText,
        confidence: 'unverified',
        score: r.score / 10 // Normalize score to 0-1 range
      }));
    }

    // Filter by venueId if specified (for embeddings results)
    if (venueId && searchMethod === 'embeddings') {
      similarChunks = similarChunks.filter(c => c.venue_id === venueId);
    }

    // Step 3: Build prompt and call LLM
    const systemPrompt = buildSystemPrompt();
    const userMessage = buildUserMessage(query, similarChunks);

    let answer;
    try {
      answer = await callLLM(systemPrompt, userMessage, glmApiKey);
    } catch (llmError) {
      // Fallback: return search results without LLM processing
      console.error('LLM failed, returning raw search results:', llmError.message);
      answer = similarChunks.length > 0
        ? `找到 ${similarChunks.length} 筆相關資料（LLM 暫時無法處理，顯示原始搜尋結果）：\n\n` +
          similarChunks.map((c, i) => `[${i+1}] ${c.venue_name || '未知場地'} - ${c.field_path || c.category}\n${c.text || c.fullText}`).join('\n\n')
        : '抱歉，知識庫目前沒有這方面的資訊。';
    }

    // Step 4: Return response
    res.json({
      success: true,
      query,
      answer,
      searchMethod,
      sources: similarChunks.map(c => ({
        venueId: c.venue_id,
        venueName: c.venue_name,
        field: c.field_path,
        confidence: c.confidence,
        relevanceScore: Math.round((c.score || 0) * 100)
      })),
      hasKnowledge: similarChunks.length > 0
    });

  } catch (error) {
    console.error('Assistant API error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
}
