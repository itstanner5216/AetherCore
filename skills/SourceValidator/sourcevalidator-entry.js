/**
 * AetherCore.SourceValidator
 * Source credibility scoring, cross-referencing, bias detection, and citation
 */

const DOMAIN_CREDIBILITY = {
  '.gov': 95, '.edu': 90, '.org': 70,
  'reuters.com': 92, 'apnews.com': 92, 'bbc.com': 88,
  'nytimes.com': 85, 'wsj.com': 85, 'nature.com': 95,
  'arxiv.org': 88, 'pubmed.gov': 95, 'wikipedia.org': 65
};

class SourceValidator {
  scoreSource(urlStr, domain = '', contentType = 'article') {
    if (!domain && urlStr) {
      try {
        const parsed = new URL(urlStr);
        domain = parsed.hostname.replace('www.', '');
      } catch (e) {
        domain = '';
      }
    }

    let score = 50;
    const factors = { base: 50 };

    for (const [knownDomain, knownScore] of Object.entries(DOMAIN_CREDIBILITY)) {
      if (domain.includes(knownDomain) || domain.endsWith(knownDomain)) {
        score = knownScore;
        factors.known_domain = knownScore;
        break;
      }
    }

    if (contentType === 'peer-reviewed') {
      score = Math.min(100, score + 15);
      factors.peer_reviewed = 15;
    } else if (contentType === 'opinion') {
      score = Math.max(0, score - 20);
      factors.opinion_penalty = -20;
    }

    let tier;
    if (score >= 80) tier = 'tier_1';
    else if (score >= 60) tier = 'tier_2';
    else if (score >= 40) tier = 'tier_3';
    else tier = 'tier_4';

    return { url: urlStr, domain, score, factors, tier };
  }

  crossReference(claim, sources = []) {
    let agreements = 0;
    const conflicts = [];

    for (const source of sources) {
      if (source.supports !== false) {
        agreements++;
      } else {
        conflicts.push(source);
      }
    }

    const agreementRate = sources.length > 0 ? agreements / sources.length : 0;
    const verified = agreementRate >= 0.6;

    return {
      claim,
      sources_checked: sources.length,
      verified,
      agreement_rate: Math.round(agreementRate * 100) / 100,
      conflicting_sources: conflicts
    };
  }

  detectBias(content, sourceUrl = '') {
    const indicators = [];
    let biasScore = 0;

    const loadedWords = ['always', 'never', 'obviously', 'clearly', 'everyone knows'];
    const lowerContent = content.toLowerCase();

    for (const word of loadedWords) {
      if (lowerContent.includes(word)) {
        indicators.push(`Loaded language: '${word}'`);
        biasScore += 10;
      }
    }

    if (content.includes('!')) {
      indicators.push('Exclamatory language');
      biasScore += 5;
    }

    let biasType = 'neutral';
    if (biasScore > 30) biasType = 'high';
    else if (biasScore > 15) biasType = 'moderate';
    else if (biasScore > 0) biasType = 'low';

    return {
      source_url: sourceUrl,
      bias_score: Math.min(100, biasScore),
      bias_type: biasType,
      indicators
    };
  }

  cite(source, format = 'apa') {
    const title = source.title || 'Untitled';
    const author = source.author || 'Unknown';
    const url = source.url || '';
    const date = source.date || 'n.d.';

    let citation;
    switch (format) {
      case 'apa':
        citation = `${author}. (${date}). ${title}. Retrieved from ${url}`;
        break;
      case 'mla':
        citation = `${author}. "${title}." Web. ${date}. <${url}>.`;
        break;
      case 'chicago':
        citation = `${author}. "${title}." Accessed ${date}. ${url}.`;
        break;
      default:
        citation = `${title} - ${url}`;
    }

    return { citation, format_used: format };
  }
}

const validator = new SourceValidator();

module.exports = {
  score_source: (params) => validator.scoreSource(params.url, params.domain, params.content_type),
  cross_reference: (params) => validator.crossReference(params.claim, params.sources),
  detect_bias: (params) => validator.detectBias(params.content, params.source_url),
  cite: (params) => validator.cite(params.source, params.format),
  name: 'AetherCore.SourceValidator',
  version: '1.0'
};
