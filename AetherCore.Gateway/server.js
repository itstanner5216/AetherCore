require('dotenv').config({ path: './dev.env' });
const express = require('express');
const { Redis } = require('@upstash/redis');
const { Ratelimit } = require('@upstash/ratelimit');

const app = express();
app.use(express.json());

const API_KEY = process.env.GATEWAY_API_KEY || process.env.API_KEY;

const authMiddleware = (req, res, next) => {
  if (!API_KEY) {
    return res.status(503).json({ error: 'API key not configured on gateway' });
  }

  const authHeader = req.headers['authorization'] || '';
  const bearerMatch = authHeader.match(/^Bearer (.+)$/i);
  const candidate =
    (bearerMatch && bearerMatch[1]) ||
    req.headers['x-api-key'] ||
    req.query.api_key;

  if (candidate !== API_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  return next();
};

app.use(authMiddleware);

// Validate Redis connection first
const redisUrl = process.env.UPSTASH_REDIS_REST_URL;
const redisToken = process.env.UPSTASH_REDIS_REST_TOKEN;

if (!redisUrl || !redisToken) {
  throw new Error('Missing UPSTASH_REDIS_REST_URL or UPSTASH_REDIS_REST_TOKEN in env');
}

// Remove any trailing slashes from URL
const sanitizedUrl = redisUrl.replace(/\/$/, '');

const redis = new Redis({
  url: sanitizedUrl,
  token: redisToken,
});

// Test Redis connection before starting server
(async () => {
  try {
    await redis.ping();
    console.log('Redis connection successful');
  } catch (err) {
    throw new Error(`Redis connection failed: ${err.message}`);
  }
})();

const ratelimit = new Ratelimit({
  redis: redis,
  limiter: Ratelimit.slidingWindow(10, '10 s'),
  analytics: true,
  prefix: 'aethercore:ratelimit',
});

// Initialize provider quotas from config
const initQuotas = async () => {
  const { providers } = require('../skills/SearchEngine/searchengine-config.json');
  
  for (const [providerType, providerList] of Object.entries(providers)) {
    for (const [providerName, config] of Object.entries(providerList)) {
      const quotaKey = `quota:${providerType}:${providerName}:remaining`;
      const exists = await redis.exists(quotaKey);
      
      if (!exists) {
        await redis.set(quotaKey, config.quota.limit);
        console.log(`Initialized ${providerName} ${providerType} quota: ${config.quota.limit}`);
      }
    }
  }
};

// Initialize quotas before starting server
initQuotas().catch(console.error);

// Import SearchEngine implementation
const { search, scrape, quota_status, reset_quotas } = require('../skills/SearchEngine/searchengine-entry.js');

// API endpoint for search with quota enforcement
app.post('/api/search', async (req, res) => {
  const { query, provider: preferredProvider, max_results = 10 } = req.body;

  if (!query) {
    return res.status(400).json({ error: 'Missing query parameter' });
  }

  const { providers } = require('../skills/SearchEngine/searchengine-config.json');
  let selectedProvider = null;

  // Provider selection logic with Redis quota check
  for (const [providerName, config] of Object.entries(providers.search)) {
    // Skip if specific provider requested and this isn't it
    if (preferredProvider && preferredProvider !== 'auto' && providerName !== preferredProvider) {
      continue;
    }

    const quotaKey = `quota:search:${providerName}:remaining`;
    const remaining = await redis.get(quotaKey);

    if (remaining > 0) {
      selectedProvider = providerName;
      break;
    }
  }

  // If auto mode and no provider found, try any available provider
  if (!selectedProvider && preferredProvider === 'auto') {
    for (const [providerName, config] of Object.entries(providers.search)) {
      const quotaKey = `quota:search:${providerName}:remaining`;
      const remaining = await redis.get(quotaKey);

      if (remaining > 0) {
        selectedProvider = providerName;
        break;
      }
    }
  }

  if (!selectedProvider) {
    return res.status(429).json({ error: 'All search providers quota exhausted' });
  }

  // Atomic quota decrement with protection
  const quotaKey = `quota:search:${selectedProvider}:remaining`;
  const newRemaining = await redis.decr(quotaKey);

  if (newRemaining < 0) {
    // Reset to 0 if negative and return error
    await redis.set(quotaKey, 0);
    return res.status(429).json({ error: `${selectedProvider} quota exhausted` });
  }

  try {
    // Use the SearchEngine implementation with selected provider
    const result = await search({
      query,
      max_results,
      provider: selectedProvider
    });

    // Add quota info to result
    result.remaining_quota = newRemaining;
    result.provider = selectedProvider;

    res.json(result);
  } catch (error) {
    console.error('Search error:', error);
    res.status(500).json({ error: `Search failed: ${error.message}` });
  }
});

// API endpoint for scraping
app.post('/api/scrape', async (req, res) => {
  const { url, render_js = false, use_premium_proxy = false } = req.body;

  if (!url) {
    return res.status(400).json({ error: 'Missing url parameter' });
  }

  try {
    const result = await scrape({
      url,
      render_js,
      use_premium_proxy
    });

    res.json(result);
  } catch (error) {
    console.error('Scrape error:', error);
    res.status(500).json({ error: `Scrape failed: ${error.message}` });
  }
});

// API endpoint for quota status
app.get('/api/quotas', async (req, res) => {
  try {
    const result = quota_status();
    res.json(result);
  } catch (error) {
    console.error('Quota status error:', error);
    res.status(500).json({ error: `Failed to get quota status: ${error.message}` });
  }
});

// API endpoint for quota reset
app.post('/api/reset-quotas', async (req, res) => {
  const { provider = 'all' } = req.body;

  try {
    const { providers } = require('../skills/SearchEngine/searchengine-config.json');

    if (provider === 'all') {
      // Reset all search provider quotas
      for (const [providerName, config] of Object.entries(providers.search)) {
        const quotaKey = `quota:search:${providerName}:remaining`;
        await redis.set(quotaKey, config.quota.limit);
      }
      // Reset all scrape provider quotas
      for (const [providerName, config] of Object.entries(providers.scrape)) {
        const quotaKey = `quota:scrape:${providerName}:remaining`;
        await redis.set(quotaKey, config.quota.limit);
      }
      res.json({ success: true, message: 'All quotas reset', provider: 'all' });
    } else {
      // Reset specific provider
      if (providers.search[provider]) {
        const quotaKey = `quota:search:${provider}:remaining`;
        await redis.set(quotaKey, providers.search[provider].quota.limit);
      } else if (providers.scrape[provider]) {
        const quotaKey = `quota:scrape:${provider}:remaining`;
        await redis.set(quotaKey, providers.scrape[provider].quota.limit);
      } else {
        return res.status(404).json({ error: `Provider ${provider} not found` });
      }
      res.json({ success: true, message: `Quota reset for: ${provider}`, provider });
    }
  } catch (error) {
    console.error('Quota reset error:', error);
    res.status(500).json({ error: `Failed to reset quotas: ${error.message}` });
  }
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Server running on port ${port}`));
