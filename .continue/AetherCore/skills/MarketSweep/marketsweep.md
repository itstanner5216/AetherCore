---
name: "AetherCore.MarketSweep"
description: Intelligent real-time deal-aggregation and comparison extension that identifies, analyzes, and ranks online product offers by price, quality, and reliability.
version: 1.0
type: callable
entry_point: marketsweep-entry.js
---

<?xml version="1.0" encoding="UTF-8"?>
<DealFinder_Protocol version="1.0">

  <activation_directive>
    <trigger>Automatically initiate the full instruction sequence upon any user query mentioning a product, item, service, or purchase intent.</trigger>
    <persistence>Apply this logic persistently to every subsequent message in the session until explicitly stopped by the user.</persistence>
    <query_analysis>
      <step>Parse the user's message to extract key variables: product type, specific brands/models, technical specifications, condition requirements, geographic restrictions, budget constraints, and any other relevant details.</step>
      <step>If critical data is missing (e.g., specifications, location), ask minimal, targeted clarifying questions in a single response, then proceed automatically with the research upon receiving answers.</step>
      <step>If sufficient data exists from the query or prior context, skip questions and proceed immediately to research.</step>
    </query_analysis>
  </activation_directive>

  <target_products>
    <brand_list>
      <description>User-specified brands or models; if none provided, include top reputable options in the category.</description>
    </brand_list>
  </target_products>

  <requirements>
    <requirement type="critical" name="condition">
      <accepted>
        <item>New retail packaging</item>
        <item>Open box (verified authentic)</item>
      </accepted>
      <rejected>
        <item>Used/refurbished</item>
        <item>Counterfeit/unbranded</item>
        <item>International versions (non-US unless specified)</item>
      </rejected>
    </requirement>
  </requirements>

  <research_scope>
    <marketplace_coverage type="exhaustive">
      <tier_1_priority>
        <platform>Amazon.com (US)</platform>
        <platform>Newegg.com</platform>
        <platform>eBay.com (US sellers only)</platform>
      </tier_1_priority>
      <tier_2_extended>
        <platform>BestBuy.com</platform>
        <platform>Walmart.com</platform>
        <platform>Target.com</platform>
        <platform>B&amp;H Photo Video</platform>
        <platform>Manufacturer direct stores (US)</platform>
      </tier_2_extended>
      <tier_3_specialty>
        <platform>Any US-based category-specific retailers</platform>
        <platform>Specialty stores with online presence relevant to product type</platform>
      </tier_3_specialty>
    </marketplace_coverage>

    <geographic_restrictions>
      <requirement>US-based sellers ONLY unless user specifies otherwise.</requirement>
      <requirement>Shipping destination: User-provided ZIP code (default to example ZIP if none given).</requirement>
      <exclusions>
        <excluded>AliExpress</excluded>
        <excluded>Banggood</excluded>
        <excluded>International sites</excluded>
        <excluded>Any overseas sellers</excluded>
      </exclusions>
    </geographic_restrictions>
  </research_scope>

  <pricing_methodology>
    <formula>Total Cost = Item Price + Shipping Cost + Taxes (if applicable)</formula>
    <currency>USD</currency>
    <shipping_destination>User-provided ZIP code</shipping_destination>

    <promotional_pricing>
      <policy>Apply ONLY verified, currently active promo codes.</policy>
      <verification_required>
        <check>Code must be active as of research date.</check>
        <check>Code must apply successfully to product.</check>
        <check>No account creation/surveys required for code.</check>
      </verification_required>
      <documentation>List promo code used in listing details.</documentation>
      <sources>
        <source>RetailMeNot</source>
        <source>Honey browser extension</source>
        <source>Slickdeals</source>
        <source>Vendor-official coupon pages</source>
        <source>Reddit category-specific subreddits (current threads)</source>
      </sources>
    </promotional_pricing>

    <special_pricing_notes>
      <handling>Include Prime/free shipping offers.</handling>
      <handling>Account for any minimum purchase thresholds.</handling>
      <handling>Note subscription discounts if they apply to single purchase.</handling>
    </special_pricing_notes>
  </pricing_methodology>

  <data_collection_protocol>
    <for_each_listing>
      <field name="exact_url" required="true">
        <description>Full product listing URL.</description>
        <validation>Must verify link is active before inclusion.</validation>
      </field>
      <field name="brand" required="true">
        <description>Exact brand name from listing.</description>
      </field>
      <field name="product_name" required="true">
        <description>Full product name/model.</description>
      </field>
      <field name="key_specifications" required="true">
        <description>User-relevant specs (e.g., dimensions, performance metrics).</description>
      </field>
      <field name="item_price" required="true">
        <format>$XX.XX USD</format>
        <note>Before shipping, after any promo codes.</note>
      </field>
      <field name="shipping_cost" required="true">
        <format>$XX.XX USD or "FREE"</format>
        <destination>User ZIP code.</destination>
      </field>
      <field name="total_cost" required="true">
        <formula>Item Price + Shipping Cost</formula>
        <format>$XX.XX USD</format>
      </field>
      <field name="promo_code_used" required="false">
        <description>Document any promo code applied.</description>
        <format>CODE: XXXXX (X% off or $X off)</format>
      </field>
      <field name="marketplace" required="true">
        <description>Platform where listing found.</description>
      </field>
      <field name="seller_info" required="true">
        <description>Seller name and basic reputation indicators.</description>
        <include>Seller rating (if available).</include>
        <include>Prime/verified seller status.</include>
      </field>
      <field name="estimated_delivery" required="false">
        <description>Shipping timeframe if relevant to comparison.</description>
      </field>
    </for_each_listing>
  </data_collection_protocol>

  <quality_gates>
    <gate id="1" name="specification_validation">
      <check>All user-defined specifications met exactly.</check>
      <action_if_fail>DISQUALIFY listing immediately.</action_if_fail>
    </gate>
    <gate id="2" name="vendor_validation">
      <check>Seller based in United States (or user-specified region).</check>
      <check>Ships to user destination.</check>
      <action_if_fail>DISQUALIFY listing immediately.</action_if_fail>
    </gate>
    <gate id="3" name="link_verification">
      <check>Product URL is active and accessible.</check>
      <check>Product page loads without errors.</check>
      <check>Product shows as "in stock" or "available".</check>
      <action_if_fail>DISQUALIFY listing, move to next option.</action_if_fail>
      <critical_note>MANDATORY: Verify every purchase link works before delivering to user.</critical_note>
    </gate>
    <gate id="4" name="authenticity">
      <check>Product is genuine (not counterfeit).</check>
      <check>Listing shows proper product images.</check>
      <check>Seller has reasonable reputation.</check>
      <action_if_suspicious>Flag for user review or disqualify.</action_if_suspicious>
    </gate>
  </quality_gates>

  <prioritization_hierarchy>
    <priority level="1">SPECIFICATION COMPLIANCE</priority>
    <priority level="2">TOTAL COST (item + shipping)</priority>
    <priority level="3">BRAND REPUTATION</priority>
    <priority level="4">SHIPPING SPEED</priority>
    <tiebreaker_rules>
      <rule>If costs within $2.00: prefer better brand reputation.</rule>
      <rule>If costs within $0.50: prefer faster shipping.</rule>
      <rule>If all equal: prefer major platforms for return policy.</rule>
    </tiebreaker_rules>
  </prioritization_hierarchy>

  <deliverable_structure>
    <output_format>
      <freedom>AI may choose optimal presentation format.</freedom>
      <suggestions>
        <option>Detailed comparison table with annotations.</option>
        <option>Ranked list with supporting details.</option>
        <option>Executive summary + comprehensive breakdown.</option>
        <option>Hybrid format optimized for decision-making.</option>
      </suggestions>
    </output_format>
    <required_content>
      <section name="top_five_rankings">
        <description>Five cheapest listings meeting ALL specifications.</description>
        <sort_order>Cheapest to most expensive (by total cost).</sort_order>
        <minimum_listings>5 (if available).</minimum_listings>
      </section>
      <section name="listing_details">
        <include>All fields from data collection protocol.</include>
        <include>Working purchase links.</include>
        <include>Clear specification confirmation.</include>
        <include>Any promo codes used.</include>
      </section>
      <section name="research_summary">
        <include>Total marketplaces searched.</include>
        <include>Total listings evaluated.</include>
        <include>Number disqualified (by reason).</include>
        <include>Any notable findings or recommendations.</include>
      </section>
      <section name="verification_statement">
        <requirement>Confirm all links tested and active.</requirement>
        <requirement>Confirm all specs validated.</requirement>
        <requirement>Note research date/time.</requirement>
      </section>
    </required_content>
  </deliverable_structure>

  <operational_constraints>
    <constraint type="critical">
      <rule>NO assumptions or estimations on specifications.</rule>
      <rule>When in doubt about spec compliance, DISQUALIFY listing.</rule>
    </constraint>
    <constraint type="critical">
      <rule>ZERO tolerance for broken/inactive links in final deliverable.</rule>
      <rule>Every URL must be tested immediately before delivery.</rule>
    </constraint>
    <constraint type="critical">
      <rule>Promo codes must be VERIFIED as working TODAY.</rule>
      <rule>Do not include expired or unverifiable promo codes.</rule>
    </constraint>
    <constraint type="methodology">
      <rule>Prioritize specs over price — better to have fewer compliant listings than questionable ones.</rule>
      <rule>Document all specification sources.</rule>
    </constraint>
  </operational_constraints>

  <error_handling>
    <scenario name="fewer_than_five_listings">
      <action>Return all compliant listings found.</action>
      <action>Explain why fewer results available.</action>
      <action>Suggest next-best alternatives if appropriate.</action>
    </scenario>
    <scenario name="link_becomes_inactive">
      <action>Remove from results.</action>
      <action>Search for replacement listing.</action>
      <action>Note in research summary.</action>
    </scenario>
    <scenario name="spec_ambiguity">
      <action>Attempt to verify from manufacturer source.</action>
      <action>If unverifiable, DISQUALIFY listing.</action>
      <action>Document ambiguity in research notes.</action>
    </scenario>
    <scenario name="promo_code_fails">
      <action>Calculate price without promo code.</action>
      <action>Continue with standard pricing.</action>
      <action>Note attempted code in research notes.</action>
    </scenario>
  </error_handling>

  <success_criteria>
    <criterion>Identify 5 cheapest compliant listings (if available).</criterion>
    <criterion>100% specification compliance across all results.</criterion>
    <criterion>100% working links verified.</criterion>
    <criterion>All pricing accurate and current.</criterion>
    <criterion>Clear ranking by total cost.</criterion>
    <criterion>Sufficient detail for immediate purchase decision.</criterion>
  </success_criteria>

  <context_notes>
    <note>Adapt research to user-specified product category and requirements.</note>
    <note>Prioritize accuracy and compliance over quantity of results.</note>
    <note>Results support immediate purchasing decisions.</note>
  </context_notes>

</DealFinder_Protocol>
