# AetherCore.MarketSweep Skill Package

**Version:** 1.0  
**Type:** Autonomous Research & Comparison Module  
**Compatibility:** Project GPT Universal Skill Integration Framework ≥1.0

---

## 🎯 Overview

**AetherCore.MarketSweep** is an intelligent, real-time deal-aggregation and comparison extension designed to autonomously identify, analyze, and rank online product offers by price, quality, and reliability. This skill operates as a subordinate module within Project GPT's modular intelligence ecosystem, automatically activating when users mention product purchase intent.

### Key Features

- **Exhaustive Marketplace Coverage**: Searches across 15+ US-based platforms including Amazon, Newegg, eBay, Best Buy, Walmart, Target, B&H Photo, and specialized retailers
- **Specification Compliance**: Enforces strict quality gates to ensure 100% specification match
- **Price Verification**: Calculates total cost including shipping, taxes, and validated promo codes
- **Link Validation**: Verifies every product URL is active and in-stock before delivery
- **Intelligent Ranking**: Prioritizes by specification compliance first, then total cost
- **Geographic Filtering**: US-based sellers only (configurable), excludes international/overseas platforms

---

## 📦 Installation

### Automatic Registration (Recommended)

1. Download `AetherCore.MarketSweep.zip`
2. Extract the archive to your Project GPT `/project_files/skills/` directory
3. The skill will auto-register on next system initialization
4. Verify registration in skill inventory: `list active skills`

### Manual Registration

If auto-registration fails:

```bash
cd /project_files/skills/
unzip AetherCore.MarketSweep.zip -d AetherCore.MarketSweep/
register_skill --path AetherCore.MarketSweep/marketsweep-config.json
```

---

## 🚀 Usage

### Activation Methods

The skill activates automatically when you mention products or purchase intent. Alternatively, use explicit commands:

#### Automatic Activation Examples
```
"Find me the cheapest GTX 4070 graphics card"
"I need a gaming laptop under $1500"
"Compare prices for Sony WH-1000XM5 headphones"
```

#### Explicit Activation
```
"Activate AetherCore.MarketSweep and search for..."
"Use AetherCore.MarketSweep: find me..."
"Run AetherCore.MarketSweep on [product]"
```

### Query Syntax

Provide as much detail as possible for optimal results:

**Basic Query:**
```
Find deals on mechanical keyboards
```

**Optimized Query:**
```
Find mechanical keyboards with:
- Cherry MX switches
- RGB backlighting
- TKL or full-size
- Under $150
- Shipping to ZIP 45701
```

### Configuration Parameters

AetherCore.MarketSweep extracts these parameters automatically from your query:

| Parameter | Description | Example |
|-----------|-------------|---------|
| **Product Type** | Category/item name | "gaming laptop", "USB-C cable" |
| **Specifications** | Technical requirements | "RTX 4060", "32GB RAM", "1TB SSD" |
| **Brand/Model** | Preferred manufacturers | "ASUS", "Sony WH-1000XM5" |
| **Condition** | New/open-box only | "new in box", "sealed retail" |
| **Budget** | Maximum price constraint | "under $500", "max $200" |
| **Location** | ZIP code for shipping | "45701", "ship to Ohio" |

---

## 📊 Output Format

AetherCore.MarketSweep delivers structured results optimized for immediate purchasing decisions:

### 1. Top 5 Rankings
Displays the cheapest listings meeting ALL specifications, sorted by total cost.

### 2. Detailed Listing Information
For each option:
- **Direct Purchase Link** (verified active)
- **Brand & Model** (exact match)
- **Key Specifications** (compliance confirmed)
- **Item Price** (after promo codes)
- **Shipping Cost** (to your ZIP code)
- **Total Cost** (all-inclusive)
- **Seller Information** (reputation indicators)
- **Estimated Delivery**

### 3. Research Summary
- Total marketplaces searched
- Number of listings evaluated
- Disqualification reasons
- Notable findings/recommendations

### 4. Verification Statement
- Link validation timestamp
- Specification confirmation
- Research date/time

---

## 🔍 Quality Gates

All listings must pass these criteria:

1. **Specification Validation**: Exact match to user requirements
2. **Vendor Validation**: US-based seller, ships to destination
3. **Link Verification**: Active URL, in-stock, loads properly
4. **Authenticity Check**: Genuine product, proper images, reputable seller

**Failure = Immediate Disqualification**

---

## 🌐 Marketplace Coverage

### Tier 1 (Always Searched)
- Amazon.com (US)
- Newegg.com
- eBay.com (US sellers only)

### Tier 2 (Extended Search)
- BestBuy.com
- Walmart.com
- Target.com
- B&H Photo Video
- Manufacturer direct stores

### Tier 3 (Specialty)
- Category-specific retailers (auto-detected)
- Regional specialty stores with online presence

### Excluded Platforms
- AliExpress
- Banggood
- International sites
- Overseas sellers

---

## 💰 Pricing Methodology

**Total Cost Formula:**
```
Total Cost = Item Price + Shipping Cost + Taxes (if applicable)
```

### Promotional Pricing
- **Only verified, active promo codes** are applied
- Sources: RetailMeNot, Honey, Slickdeals, vendor pages, Reddit
- Codes must work TODAY (no expired codes)
- No account creation/surveys required

### Special Considerations
- Prime/free shipping offers included
- Minimum purchase thresholds noted
- Subscription discounts (if applicable to single purchase)

---

## ⚙️ Configuration

### Default Settings
```json
{
  "geographic_restriction": "US only",
  "condition": ["new", "open_box"],
  "min_listings": 5,
  "link_verification": true,
  "promo_code_validation": true
}
```

### Custom Overrides
Specify in your query:
```
"Include international sellers"
"Allow refurbished items"
"Search only Amazon and Newegg"
```

---

## 🛠️ Dependencies

**None.** AetherCore.MarketSweep is self-contained and requires no companion skills.

### Recommended Companions
- `price-tracker`: Monitor price history over time
- `review-analyzer`: Deep-dive into product reviews
- `spec-validator`: Cross-reference manufacturer specifications

---

## 🔧 Troubleshooting

### Issue: Fewer than 5 results returned
**Cause**: Strict specification requirements limiting available options  
**Solution**: AetherCore.MarketSweep prioritizes compliance over quantity. Consider relaxing specs or checking "next-best alternatives" in research summary.

### Issue: Link becomes inactive
**Action**: Automatically removed and replaced with next-best option  
**Note**: Documented in research summary

### Issue: Promo code fails
**Action**: Price calculated without code, noted in research notes  
**Fallback**: Standard pricing used

### Issue: Specification ambiguity
**Action**: Verification attempted via manufacturer source  
**Failure**: Listing disqualified, documented in notes

---

## 📋 Success Criteria

A successful AetherCore.MarketSweep session achieves:

✅ 5 cheapest compliant listings identified (if available)  
✅ 100% specification compliance  
✅ 100% working links verified  
✅ Accurate, current pricing  
✅ Clear ranking by total cost  
✅ Sufficient detail for immediate purchase  

---

## 🧩 Integration Architecture

### Execution Flow
```
User Query → Query Analysis → Specification Extraction → 
Market Research → Quality Gates → Price Verification → 
Link Validation → Ranking Algorithm → Formatted Output
```

### Subordinate Execution
- **Inherits tone** from parent protocol
- **Session-temporary memory**: Unloads on exit
- **Auto-registration**: No manual activation needed
- **Fuzzy matching**: Understands natural language variations

---

## 📝 Example Session

**User:**  
"Find the cheapest RTX 4070 with at least 12GB VRAM, new condition, shipping to 45701"

**AetherCore.MarketSweep Output:**
```
🏆 TOP 5 RTX 4070 DEALS (12GB+ VRAM, New Condition)

1. ASUS Dual GeForce RTX 4070 - $549.99
   • Newegg.com | 12GB GDDR6X | Verified Seller
   • Item: $529.99 | Ship: FREE | Promo: TECHSAVE20 (-$20)
   • Link: [verified active ✓]

2. MSI Ventus 2X RTX 4070 - $559.99
   • Amazon.com | 12GB GDDR6X | Prime Seller
   • Item: $559.99 | Ship: FREE (Prime)
   • Link: [verified active ✓]

[... 3 more listings ...]

📊 RESEARCH SUMMARY
• Marketplaces: 11 searched
• Listings: 47 evaluated, 42 disqualified
  - Disqualified: 18 (refurbished), 12 (international), 8 (spec mismatch), 4 (inactive)
• All links verified: November 9, 2025, 3:42 PM EST
```

---

## 🔒 Operational Constraints

### Critical Rules
- **NO assumptions** on specifications
- **ZERO tolerance** for broken links
- **Verified promo codes** only (working today)
- **Specs > Price**: Fewer compliant results better than questionable ones

---

## 📚 Additional Resources

- **Project GPT Documentation**: `/docs/skill-integration.md`
- **Universal Skill Framework**: `/docs/universal-framework-spec.md`
- **Support**: Contact system administrator or check `/logs/marketsweep.log`

---

## 📄 License & Attribution

**Author:** System Skill Developer  
**Version:** 1.0  
**Last Updated:** November 2025  
**License:** Proprietary (Project GPT Internal Use)

---

## 🚧 Roadmap

### Planned Features (v1.1+)
- Historical price tracking integration
- Multi-currency support
- International seller option flag
- Real-time stock monitoring
- Price drop alerts
- Refurbished product filtering option

---

**End of Documentation**

For technical support or feature requests, refer to Project GPT system documentation.
