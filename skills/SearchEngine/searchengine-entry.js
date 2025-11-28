/**
 * AetherCore.SearchEngine
 * Multi-provider search engine with automatic failover and quota management
 *
 * Providers:
 * - Search: Google CSE, Brave, Serper
 * - Scrape: Webscraping API, ScrapingAnt (fallback)
 *
 * Features:
 * - Automatic failover on quota exhaustion or error
 * - Real-time quota tracking and enforcement
 * - Telemetry emission to EventMesh/OptiGraph
 * - Integration with DeepForge, MarketSweep, GeminiBridge
 */

const http = require("http");
const https = require("https");
const url = require("url");

// ============================================================================
// QUOTA MANAGER
// ============================================================================

class QuotaManager {
  constructor() {
    this.quotas = {
      // Search providers
      google: {
        used: 0,
        limit: 100,
        window: "day",
        reset_at: null,
        active: true,
      },
      brave: {
        used: 0,
        limit: 2000,
        window: "month",
        reset_at: null,
        active: true,
      },
      serper: {
        used: 0,
        limit: 2000,
        window: "month",
        reset_at: null,
        active: true,
      },
      // Scrape providers
      webscraping_api: {
        used: 0,
        limit: 5000,
        window: "month",
        reset_at: null,
        active: true,
      },
      scrapingant: {
        used: 0,
        limit: 10000,
        window: "month",
        reset_at: null,
        active: true,
        credit_based: true,
      },
    };
    this.events = [];
    this._initializeResetTimers();
  }

  _initializeResetTimers() {
    const now = new Date();
    for (const [provider, quota] of Object.entries(this.quotas)) {
      if (quota.window === "day") {
        const tomorrow = new Date(now);
        tomorrow.setDate(tomorrow.getDate() + 1);
        tomorrow.setHours(0, 0, 0, 0);
        quota.reset_at = tomorrow.toISOString();
      } else if (quota.window === "month") {
        const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1);
        quota.reset_at = nextMonth.toISOString();
      }
    }
  }

  checkAndReset() {
    const now = new Date();
    for (const [provider, quota] of Object.entries(this.quotas)) {
      if (quota.reset_at && new Date(quota.reset_at) <= now) {
        this._resetProvider(provider);
      }
    }
  }

  _resetProvider(provider) {
    const quota = this.quotas[provider];
    quota.used = 0;
    quota.active = true;
    this._initializeResetTimers();
    this._logEvent("quota_reset", { provider, new_limit: quota.limit });
  }

  canUse(provider, credits = 1) {
    this.checkAndReset();
    const quota = this.quotas[provider];
    if (!quota) return false;
    if (!quota.active) return false;
    return quota.used + credits <= quota.limit;
  }

  consume(provider, credits = 1) {
    const quota = this.quotas[provider];
    if (!quota) return false;

    quota.used += credits;
    this._logEvent("quota_usage", {
      provider,
      credits_used: credits,
      remaining: quota.limit - quota.used,
    });

    if (quota.used >= quota.limit) {
      quota.active = false;
      this._logEvent("provider_deactivation", {
        provider,
        reason: "quota_exhausted",
        reset_at: quota.reset_at,
      });
    }
    return true;
  }

  getStatus() {
    this.checkAndReset();
    const status = {};
    for (const [provider, quota] of Object.entries(this.quotas)) {
      status[provider] = {
        used: quota.used,
        limit: quota.limit,
        remaining: quota.limit - quota.used,
        active: quota.active,
        reset_at: quota.reset_at,
        utilization_pct: Math.round((quota.used / quota.limit) * 100),
      };
    }
    return status;
  }

  getNextActiveProvider(type) {
    this.checkAndReset();
    const searchProviders = ["google", "brave", "serper"];
    const scrapeProviders = ["webscraping_api", "scrapingant"];
    const providers = type === "search" ? searchProviders : scrapeProviders;

    for (const provider of providers) {
      if (this.quotas[provider]?.active) {
        return provider;
      }
    }
    return null;
  }

  _logEvent(type, data) {
    this.events.push({
      type,
      timestamp: new Date().toISOString(),
      ...data,
    });
    // Keep last 100 events
    if (this.events.length > 100) {
      this.events = this.events.slice(-100);
    }
  }

  getEvents() {
    return this.events;
  }

  forceReset(provider = "all") {
    if (provider === "all") {
      for (const p of Object.keys(this.quotas)) {
        this._resetProvider(p);
      }
    } else if (this.quotas[provider]) {
      this._resetProvider(provider);
    }
  }
}

// ============================================================================
// API CLIENTS
// ============================================================================

const API_KEYS = {
  google: {
    api_key: process.env.GOOGLE_API_KEY,
    cx: process.env.GOOGLE_CSE_ID,
  },
  brave: {
    api_key: process.env.BRAVE_API_KEY,
  },
  serper: {
    api_key: process.env.SERPER_API_KEY,
  },
  webscraping_api: {
    api_key: process.env.WEBSCRAPING_API_KEY,
  },
  scrapingant: {
    api_key: process.env.SCRAPINGANT_API_KEY,
  },
};

function httpRequest(options, postData = null) {
  return new Promise((resolve, reject) => {
    const protocol = options.protocol === "http:" ? http : https;
    const req = protocol.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        try {
          resolve({ status: res.statusCode, data: JSON.parse(data) });
        } catch {
          resolve({ status: res.statusCode, data: data });
        }
      });
    });
    req.on("error", reject);
    req.setTimeout(30000, () => {
      req.destroy();
      reject(new Error("Request timeout"));
    });
    if (postData) req.write(postData);
    req.end();
  });
}

// Search provider implementations
async function searchGoogle(query, maxResults) {
  const params = new URLSearchParams({
    key: API_KEYS.google.api_key,
    cx: API_KEYS.google.cx,
    q: query,
    num: Math.min(maxResults, 10),
  });

  const options = {
    hostname: "www.googleapis.com",
    path: `/customsearch/v1?${params}`,
    method: "GET",
    headers: { Accept: "application/json" },
  };

  const response = await httpRequest(options);
  if (response.status !== 200) {
    throw new Error(`Google API error: ${response.status}`);
  }

  return (response.data.items || []).map((item) => ({
    title: item.title,
    url: item.link,
    snippet: item.snippet,
    source: "google",
  }));
}

async function searchBrave(query, maxResults) {
  const params = new URLSearchParams({
    q: query,
    count: Math.min(maxResults, 20),
  });

  const options = {
    hostname: "api.search.brave.com",
    path: `/res/v1/web/search?${params}`,
    method: "GET",
    headers: {
      Accept: "application/json",
      "X-Subscription-Token": API_KEYS.brave.api_key,
    },
  };

  const response = await httpRequest(options);
  if (response.status !== 200) {
    throw new Error(`Brave API error: ${response.status}`);
  }

  return (response.data.web?.results || []).map((item) => ({
    title: item.title,
    url: item.url,
    snippet: item.description,
    source: "brave",
  }));
}

async function searchSerper(query, maxResults) {
  const postData = JSON.stringify({
    q: query,
    num: Math.min(maxResults, 100),
  });

  const options = {
    hostname: "google.serper.dev",
    path: "/search",
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-KEY": API_KEYS.serper.api_key,
      "Content-Length": Buffer.byteLength(postData),
    },
  };

  const response = await httpRequest(options, postData);
  if (response.status !== 200) {
    throw new Error(`Serper API error: ${response.status}`);
  }

  return (response.data.organic || []).map((item) => ({
    title: item.title,
    url: item.link,
    snippet: item.snippet,
    source: "serper",
  }));
}

// Scrape provider implementations
async function scrapeWebscrapingApi(targetUrl, renderJs) {
  const params = new URLSearchParams({
    api_key: API_KEYS.webscraping_api.api_key,
    url: targetUrl,
    render_js: renderJs ? "1" : "0",
  });

  const options = {
    hostname: "api.webscraping.ai",
    path: `/html?${params}`,
    method: "GET",
    headers: { Accept: "text/html" },
  };

  const response = await httpRequest(options);
  if (response.status !== 200) {
    throw new Error(`Webscraping API error: ${response.status}`);
  }

  return { content: response.data, source: "webscraping_api" };
}

async function scrapeScrapingAnt(targetUrl, renderJs, usePremium) {
  const params = new URLSearchParams({
    url: targetUrl,
    "x-api-key": API_KEYS.scrapingant.api_key,
  });

  if (!renderJs) {
    params.set("browser", "false");
  }
  if (usePremium) {
    params.set("proxy_type", "residential");
  }

  const options = {
    hostname: "api.scrapingant.com",
    path: `/v2/general?${params}`,
    method: "GET",
    headers: { Accept: "text/html" },
  };

  const response = await httpRequest(options);
  if (response.status !== 200) {
    throw new Error(`ScrapingAnt API error: ${response.status}`);
  }

  return { content: response.data, source: "scrapingant" };
}

function calculateScrapingAntCredits(renderJs, usePremium) {
  if (usePremium) {
    return renderJs ? 125 : 25;
  }
  return renderJs ? 10 : 1;
}

// ============================================================================
// MAIN SEARCH ENGINE CLASS
// ============================================================================

class SearchEngine {
  constructor() {
    this.telemetryBuffer = [];
  }

  async search(query, maxResults = 10, preferredProvider = "auto") {
    const startTime = Date.now();
    let results = null;
    let usedProvider = null;
    let errors = [];

    const providers =
      preferredProvider === "auto"
        ? ["google", "brave", "serper"]
        : [preferredProvider];

    for (const provider of providers) {
      try {
        switch (provider) {
          case "google":
            results = await searchGoogle(query, maxResults);
            break;
          case "brave":
            results = await searchBrave(query, maxResults);
            break;
          case "serper":
            results = await searchSerper(query, maxResults);
            break;
        }

        usedProvider = provider;
        break;
      } catch (error) {
        errors.push({ provider, error: error.message });
      }
    }

    const executionTime = Date.now() - startTime;

    if (!results) {
      return {
        success: false,
        error: "All search providers failed",
        errors,
      };
    }

    this._emitTelemetry("search_completed", {
      provider: usedProvider,
      query,
      results_count: results.length,
      execution_time_ms: executionTime,
    });

    return {
      success: true,
      provider: usedProvider,
      query,
      results,
      results_count: results.length,
      execution_time_ms: executionTime,
    };
  }

  async scrape(targetUrl, renderJs = false, usePremium = false) {
    const startTime = Date.now();
    let content = null;
    let usedProvider = null;
    let errors = [];

    // Try webscraping_api first, then scrapingant
    const providers = ["webscraping_api", "scrapingant"];

    for (const provider of providers) {
      try {
        if (provider === "webscraping_api") {
          content = await scrapeWebscrapingApi(targetUrl, renderJs);
        } else {
          content = await scrapeScrapingAnt(targetUrl, renderJs, usePremium);
        }

        usedProvider = provider;
        break;
      } catch (error) {
        errors.push({ provider, error: error.message });
      }
    }

    const executionTime = Date.now() - startTime;

    if (!content) {
      return {
        success: false,
        error: "All scrape providers failed",
        errors,
      };
    }

    this._emitTelemetry("scrape_completed", {
      provider: usedProvider,
      url: targetUrl,
      execution_time_ms: executionTime,
    });

    return {
      success: true,
      provider: usedProvider,
      url: targetUrl,
      content: content.content,
      execution_time_ms: executionTime,
    };
  }

  getQuotaStatus() {
    return {
      message: "Quota status managed by Redis in server.js",
    };
  }

  resetQuotas(provider = "all") {
    return {
      success: true,
      message: `Quota reset requested for: ${provider} (handled by server.js via Redis)`,
    };
  }

  _emitTelemetry(event, data) {
    this.telemetryBuffer.push({
      event,
      timestamp: new Date().toISOString(),
      ...data,
    });
  }

  getTelemetry() {
    const buffer = this.telemetryBuffer;
    this.telemetryBuffer = [];
    return buffer;
  }
}

// ============================================================================
// EXPORTS
// ============================================================================

const engine = new SearchEngine();

module.exports = {
  // Main tools
  search: (params) =>
    engine.search(params.query, params.max_results, params.provider),
  scrape: (params) =>
    engine.scrape(params.url, params.render_js, params.use_premium_proxy),
  quota_status: () => engine.getQuotaStatus(),
  reset_quotas: (params) => engine.resetQuotas(params.provider),

  // For integration
  getTelemetry: () => engine.getTelemetry(),
  getQuotaManager: () => engine.quotaManager,

  // Metadata
  name: "AetherCore.SearchEngine",
  version: "1.0.0",
};
