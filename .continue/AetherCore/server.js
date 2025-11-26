require('dotenv').config({ path: './dev.env' });
const express = require('express');
const { Redis } = require('@upstash/redis');
const { Ratelimit } = require('@upstash/ratelimit');

const app = express();
app.use(express.json());

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN,
});

const ratelimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(10, '10 s'),
  analytics: true,
});

// Bouncer middleware
app.use(async (req, res, next) => {
  console.log('[Request]', new Date().toISOString(), req.ip);
  const identifier = req.ip || '127.0.0.1';
  const result = await ratelimit.limit(identifier);
  res.set('X-RateLimit-Limit', result.limit.toString());
  res.set('X-RateLimit-Remaining', result.remaining.toString());
  if (!result.success) {
    return res.status(429).json({ 
      error: 'Rate limit exceeded', 
      retry_after: result.reset 
    });
  }
  next();
});

// Success route
app.get('/', (req, res) => {
  const remaining = parseInt(res.get('X-RateLimit-Remaining') || '0');
  res.json({ 
    status: 'Active', 
    db: 'AetherCore', 
    remaining 
  });
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Server running on port ${port}`));
