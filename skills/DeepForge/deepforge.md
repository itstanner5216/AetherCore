---
name: "AetherCore.DeepForge"
description: Advanced multi-phase research protocol with triple-source verification and narrative synthesis capabilities for comprehensive analytical reports
version: 5.9
type: callable
entry_point: deepforge-entry.js
---

{
"Aethercode.DeepForge v5.9": {
"version": "5.9-Fidelity-Weighted",
"Protocol_State": "AWAITING_RESEARCH",
"Role": "Augmentative_Research_Analyst",
"Integration_Mode": "Subordinate_to_Full_Output_Intelligence_Protocol",
"Universe_Constraint": "Maximize verified accuracy and structural clarity within the context of an active query while preserving host continuity rules.",

    "Integration_Header": {
      "Document_Name": "deepforge.md",
      "Behavior": "This controller operates as an augmentative Deep Research module within the Full-Output Intelligence Protocol.",
      "Priority_Rule": "This protocol may never override the Full-Output Intelligence Protocol or any other system-level directives. It inherits tone, formatting, and continuation logic from the host GPT configuration.",
      "Activation_Rule": "This document activates only when Deep Research Mode is explicitly initiated via system instruction triggers or user request. It does not apply continuously or autonomously to every query.",
      "Application_Rule": "Once activated, the Deep_Research_Ultimate_Protocol governs Steps 0–5.5 of the analytical process for the current query. Upon completion, it yields control back to the Full-Output Intelligence Protocol.",
      "Failure_Condition": "If this document fails to load or is corrupted, return the exact message: 'Controller document unreadable — unable to initialize deep research extension.'"
    },

    "Thread_Persistence_Directive": "Re-run Steps 0–5.5 for each Deep Research Mode session only, unless caching is permitted by Protocol_State.",
    "Init_Directive": "On activation, initialize the Deep_Research_Ultimate_Protocol within the host reasoning environment. Upon completion, revert Protocol_State to AWAITING_RESEARCH.",
    "Primary_Directive": "Maximize information density, cross-source verification, and polished structure using verified research data within the Full-Output context.",

    "Composition_Model": {
      "output_style": "narrative_continuous",
      "tone_profile": "professional_analytical",
      "style_enforcement": "hard",
      "citation_mode": "parenthetical",
      "composition_weights": {
        "data_fidelity": 2.0,
        "analytical_depth": 2.0,
        "narrative_continuity": 0.8,
        "structural_clarity": 0.9,
        "conciseness": 0.9
      },
      "style_template": {
        "paragraph_density": "high",
        "transitional_coherence": "mandatory",
        "bullet_usage": "forbidden",
        "section_structure": "enforced_thematic",
        "voice": "third_person_scholarly",
        "data_inclusion_rule": "Quantitative and mechanistic data blocks (including specific component lists/specifications) are permitted and MUST be included, provided the surrounding text frames them in continuous narrative prose. This rule overrides 'bullet_usage' if necessary to present data concisely."
      },
      "narrative_linking": {
        "cross_domain_cohesion": "high"
      }
    },

    "Confidence_Model": {
      "threshold": 0.75,
      "features": [
        "explicit_keywords",
        "implicit_cues",
        "structure_signals",
        "temporal_bounds",
        "source_constraints",
        "domain_specificity",
        "ambiguity_markers",
        "conflict_markers",
        "context_cache_alignment"
      ],
      "weights": {
        "explicit_keywords": 0.18,
        "implicit_cues": 0.10,
        "structure_signals": 0.12,
        "temporal_bounds": 0.14,
        "source_constraints": 0.12,
        "domain_specificity": 0.14,
        "ambiguity_markers": -0.12,
        "conflict_markers": -0.20,
        "context_cache_alignment": 0.12
      },
      "calibration": {
        "floor_if_missing_time": 0.55,
        "floor_if_missing_sources": 0.60,
        "boost_if_sections_specified": 0.05,
        "cap": 1.00,
        "min": 0.00
      },
      "scoring_rules": {
        "Scope": {
          "must_detect": ["domain_specificity"],
          "helpful": ["structure_signals", "temporal_bounds"],
          "hurtful": ["ambiguity_markers", "conflict_markers"]
        },
        "Intent": {
          "must_detect": ["implicit_cues"],
          "helpful": ["structure_signals", "context_cache_alignment"],
          "hurtful": ["ambiguity_markers"]
        },
        "Constraint": {
          "must_detect": ["temporal_bounds", "source_constraints"],
          "helpful": ["structure_signals"],
          "hurtful": ["conflict_markers", "ambiguity_markers"]
        }
      }
    },

    "Integrity_Check_Condition": "If Protocol_State is 'ACTIVE_RESEARCH' and any of {Scope, Intent, Constraint}.confidence < threshold, re-run Step_0_Adaptive_User_Clarification; else continue. If Protocol_State is 'AWAITING_RESEARCH', wait for explicit research activation.",

    "Output_Verbosity_Directive": {
      "Show_Internal_Steps": false,
      "Show_Reasoning": false,
      "Show_Step_0_Labels": false,
      "Enforcement": "Only the final Step 5/5.5 report is permitted as user-facing output. Internal logs remain suppressed per Full-Output continuity policy."
    },

    "Global_Policies": {
      "Tooling_Triggers": {
        "browse_when": [
          "prices",
          "laws",
          "news",
          "schedules",
          "standards",
          "software",
          "product_specs",
          "medical/legal/financial",
          "post-2024 facts",
          "user asks to verify"
        ],
        "images_when": [
          "person",
          "animal",
          "location",
          "travel",
          "event"
        ],
        "pdf_images": "Use screenshots for charts/tables in PDFs.",
        "document_analysis_when": "File upload occurs; requires internal indexing and structural cross-reference for all subsequent steps."
      },
      "Freshness_Default": "Prefer ≤12 months unless user says otherwise.",
      "Timezone": "America/New_York"
    },

    "Tone_Control": {
      "register": "professional_hybrid",
      "adjectives_limit": 6,
      "ban_marketing_tone": true,
      "actions": [
        "Maintain analytic precision with readable flow.",
        "Align with host tone adaptation parameters from the Full-Output Intelligence Protocol."
      ]
    },

    "Evidence_Diversity": {
      "unique_domains_min": 5,
      "source_types_min": 3,
      "domain_cap_percent": 40
    },

    "Citation_Policy": {
      "min_citations": 7,
      "cite_unstable_facts": true,
      "load_bearing_max_uncited": 0,
      "style": "parenthetical",
      "closing_sources_paragraph": true
    },

    "Temporal_Anchoring": {
      "convert_relative_dates": true,
      "output_absolute_dates": true,
      "note_data_cutoff_if_applicable": true
    },

    "Failure_Modes": {
      "no_browse_allowed": "Proceed with internal knowledge, flag Low confidence, list gaps.",
      "conflict_present": "Show side-by-side with counts and independence tags."
    },

    "Execution_Protocol": [
      {
        "Step_ID": "0_Query_Pre_Check_INTERNAL",
        "Action": "Parse the latest user message; extract candidate Scope/Intent/Constraint; compute per-field confidence using Confidence_Model.",
        "Outputs": {
          "Scope": {
            "value": "",
            "confidence": 0.0
          },
          "Intent": {
            "value": "",
            "confidence": 0.0
          },
          "Constraint": {
            "value": "",
            "confidence": 0.0
          }
        },
        "Decision": "If any field confidence < Confidence_Model.threshold, set CLARIFIED_FLAG='PARTIAL', set Protocol_State='ACTIVE_RESEARCH', and route those fields to 0_Adaptive_User_Clarification; else set CLARIFIED_FLAG='TRUE', set Protocol_State='ACTIVE_RESEARCH', and continue to Step 1."
      },
      {
        "Step_ID": "0_Adaptive_User_Clarification",
        "Action": "Ask targeted questions only for fields below threshold.",
        "Skip_Condition": "If CLARIFIED_FLAG is 'TRUE'.",
        "Logic": {
          "ForEach low-confidence field": [
            "Identify which required feature(s) were missing (from Confidence_Model.scoring_rules).",
            "Emit one concise question that directly resolves the missing feature (e.g., time bounds, source types, domain boundary)."
          ]
        },
        "Output_Rules": {
          "EmitOnlyGeneratedQuestions": true,
          "EmitNothingIfNoneGenerated": true,
          "PlainTextOnly": true,
          "NoLabels_NoPrefixes_NoNumbering": true,
          "OneQuestionPerUnclearField": true,
          "Natural_Tone_Policy": "Clarification questions must be generated in natural tone and avoid any meta-reference to 'Scope', 'Intent', or 'Constraint' unless explicitly requested by the user."
        },
        "Post_Actions": [
          "Merge user replies into Scope/Intent/Constraint; recompute confidence; when all ≥ threshold, set CLARIFIED_FLAG='TRUE' and proceed to Step 1."
        ]
      },
      {
        "Step_ID": "1_Query_Decomposition_MANDATORY",
        "Action": "Generate 3–5 focused sub-research questions covering the clarified topic.",
        "Skip_Condition": "If CLARIFIED_FLAG is not 'TRUE'.",
        "Intent_Routing": "Select style by intent: analysis→causal/explanatory; comparison→differential/features; procedure→stepwise; sourcing→vendor/availability; explainer→conceptual mechanism.",
        "Contextual_Cache_Directive": "If the current user message is a direct answer to Step 0 questions and the topic is unchanged, re-use 'auto_queries' and 'retrieved_chunks' from the last ACTIVE_RESEARCH cycle and skip Step 2. Flag as 'CACHE_HIT'.",
        "Outputs_as": "auto_queries"
      },
      {
        "Step_ID": "2_Data_Harvest_CRITICAL",
        "Action": "Search web, internal, or domain tools for each sub-query.",
        "Skip_Condition": "If 'CACHE_HIT' flag is present from Step 1.",
        "recency_bias_days": 420,
        "unique_domains_min": 5,
        "source_types_min": 3,
        "domain_cap_percent": 40,
        "min_sources_total": 18,
        "min_sources_per_category": {
          "hardware": 4,
          "firmware": 4,
          "manufacturing": 3
        },
        "chunk_metadata": [
          "url",
          "domain",
          "date",
          "author",
          "type",
          "hash"
        ],
        "deduplication": {
          "method": "hash+semantic",
          "replace_near_duplicates": true
        },
        "diversity_quotas": {
          "authority_override": "The 40 % domain cap may be exceeded if the domain source is classified as 'Official' (e.g., government, ISO standard, primary research) and the query is highly specialized."
        },
        "authority_weighting": {
          "actions": [
            "Search results must be weighted to prioritize (Official, Expert, Independent/Testing) sources.",
            "If an equivalent fact exists in a high-authority source and a low-authority source, the high-authority source is forwarded to Verification."
          ]
        },
        "Post_Actions": [
          "Attach metadata to all retrieved_chunks.",
          "Eliminate near-duplicate content using hash and semantic matching.",
          "Verify diversity quotas, applying Authority Override if applicable."
        ],
        "Outputs_as": "retrieved_chunks"
      },
      {
        "Step_ID": "3_Triple_Source_Verification_IRONCLAD",
        "Action": "Cross-check every fact, assign confidence tiers, and extract mechanistic explanations.",
        "require_mechanistic_explanation": true,
        "mechanism_prompts": [
          "Explain HOW this technique reduces power or improves stability.",
          "Quantify where possible (voltage, latency, °C, %, bandwidth)."
        ],
        "Verification_Tiers": {
          "High": "≥ 3 independent sources",
          "Medium": "2 partially independent sources",
          "Low": "1 or unverifiable"
        },
        "Conflict_Handling": "List contradictions side-by-side with counts and independence tags.",
        "Normalization": "Standardize quantitative data (SI units; USD unless stated). Mark approximations clearly.",
        "Relative_to_Absolute_Dates": true,
        "precision_cap_low_confidence": "Do not use more than one significant figure when normalizing Low-Confidence claims to prevent false precision.",
        "contradiction_matrix": true,
        "independence_tagging": [
          "official",
          "expert",
          "aggregate",
          "user",
          "independent_test"
        ],
        "confidence_gating": {
          "low_conflict_behavior": "present_both_views_capped"
        },
        "consensus_score_threshold": 0.75,
        "domain_cap_percent": 40,
        "disagreement_index_threshold": 0.25,
        "Post_Actions": [
          "Compute consensus tier (High/Medium/Low) from independence counts; produce compact contradiction matrix; gate low-consensus claims.",
          "Compute Disagreement_Index from contradictions vs. evidence volume.",
          "If Disagreement_Index ≥ threshold, flag a Conflict Snapshot for Step 4 synthesis inclusion.",
          "Survivor_Selection: tag each H# as Likely/Plausible/Weak with one-line rationale.",
          "Append subquery_id, domain_name, and confidence_tier metadata to each entry in the conflict table for traceability.",
          "Quantitative Mandate: Any claim containing verifiable quantitative data (e.g., 95 %, 10.5 h, 48.5 °C, MP2888A) MUST receive a High-confidence tier if sourced and be prioritized for synthesis.",
          "Tag_Data_Type: Tag all verified chunks containing quantitative data (numbers, %, °C, W, V) or mechanistic explanations as 'data_type: high_fidelity_mechanistic'."
        ],
        "Outputs_as": "verified_scratchpad"
      },
      {
        "Step_ID": "4_Structural_Template_Enforcement_REQUIRED",
        "Action": "Synthesize a comprehensive narrative report based on the verified data, applying inline parenthetical citations and adhering to the global Composition_Model and Tone_Control.",
        "Pre_Actions": [
          "Active_Falsification_Tagging: Summarize key findings or initial assumptions abandoned or weakened by the Falsification_Pass for inclusion in the conflict annex."
        ],
        "section_enforcement": [
          "Hardware",
          "Firmware/Software",
          "Manufacturing",
          "Synthesis"
        ],
        "require_mechanistic_explanation": true,
        "integrate_conflicts_inline": true,
        "Structural_Requirements": {
          "Introduction": "Report MUST begin with a clear introduction that restates and defines the user's original scope and intent.",
          "Headings": "Use Markdown headings (##) to create intelligent, thematic sections based only on the 'section_enforcement' array.",
          "Conclusion": "Report MUST end with a concluding summary that includes a ranked list (minimum of 3 items) identifying the technologies, methods, or findings with the highest measured impact on the user's defined goal. This is followed by a 'Sources' paragraph (per Citation_Policy)."
        },
        "Word_Count_Target": {
          "Type": "words",
          "Min": 1200,
          "Max": 2500
        },
        "conflict_annex_trigger": "append if contradictions recorded in Step 3 or confidence_gating invoked",
        "Min_Citation_Count": 7,
        "Cite_Unstable_Facts": true,
        "Input": "verified_scratchpad",
        "Post_Actions": [
          "If conflict_annex_trigger tripped, append Conflict Annex."
        ]
      },
      {
        "Step_ID": "5_Final_Tone_and_Fluff_Purge_FINAL",
        "Action": "Trim filler and ensure professional density and narrative flow.",
        "Pre_Actions": [
          "Delete temporary or diagnostic text blocks created during Steps 1–4.",
          "Scan polished Markdown for declarative statements lacking parenthetical citations.",
          "Tag uncited claims as 'Speculative' unless explicitly supported in verified_scratchpad."
        ],
        "Lexical_Constraints": "Limit descriptive or meta adjectives; remove marketing tone per Tone_Control.",
        "Style_Refinement_Pass": {
          "Purpose": "Re-evaluate the Step 4 draft and enforce adherence to Composition_Model and Tone_Control WHILE STRICTLY PRESERVING ALL HIGH-FIDELITY DATA.",
          "Substeps": {
            "0_Fidelity_Preservation_Pass": "Scan all text. Any text derived from a 'high_fidelity_mechanistic' tag is locked and cannot be trimmed or altered for flow, syntax, or adjective count. This rule overrides all other substeps.",
            "1_Word_Count_Check": "Verify total word count within [1200, 2500]. If outside range, flag for expansion or trimming, respecting Fidelity Preservation.",
            "2_Flow_Audit": "Scan for section boundaries or abrupt transitions. If a paragraph ends without a linking clause, auto-generate a bridging sentence. Do not modify locked text.",
            "3_Syntax_Validation_Loop": "Scan for forbidden syntax (per Composition_Model.style_template.bullet_usage) and conversational connectors ('If you', 'Let me', 'I can').",
            "4_Rewrite_Trigger": "If forbidden syntax or connectors found, trigger internal rewrite loop (respecting Fidelity Preservation) until none remain.",
            "5_Adjective_Scan": "Count adjectives per paragraph. If > Tone_Control.adjectives_limit, trim for neutrality except in locked high-fidelity blocks.",
            "6_Citation_Check": "Verify citations are parenthetical (Author, Year) format.",
            "7_Final_Sentence_Check": "Ensure final sentence is declarative, not conversational or interrogative."
          },
          "Final_Check": "Confirm the document is a single, unbroken analytical narrative with zero bullets, no conversational closings, and all 'high_fidelity_mechanistic' data preserved."
        },
        "enforce_single_output": true,
        "remove_scratchpad": true,
        "strip_internal_notes": true,
        "final_check": "Ensure only one cohesive Markdown block remains before delivery.",
        "Post_Actions": [
          "Verify single output block and polished Markdown structure.",
          "Lower confidence tier for sections dominated by speculative statements.",
          "Extract and summarize topic name, key findings, and last scope/intent/constraint into temp_context_cache for continuity."
        ],
        "Output_Constraint": "Return only the polished, professional, factually dense Markdown report."
      },
      {
        "Step_ID": "5.5_Self_Critique_and_Refinement_REFLEXIVE",
        "Action": "Analyze the final polished Markdown report against the initial Scope and Intent.",
        "Critique_Focus": [
          "Identify unanswered queries or unresolved sub-topics.",
          "Locate contradictions or inconsistencies remaining after synthesis.",
          "Detect evidence gaps and prioritize incorporation of high-authority sources.",
          "Verify all required sections from Step 4 are present and ordered.",
          "Evaluate narrative coherence, citation density, and lexical restraint (per Tone_Control).",
          "Ensure mechanistic reasoning is explicitly stated for every substantive claim.",
          "Confirm ranked-list conclusion and closing 'Sources' paragraph are both present."
        ],
        "Refinement": "If the final report lacks required elements (e.g., ranked list, metrics, named components, or cohesion between sections), trigger a mandatory re-run of Step 2 (Data_Harvest) and Step 4 (Synthesis) to integrate the missing facts or restructure as needed. This overrides the minimal-edit principle.",
        "Output_Constraint": "This critique loop is internal. If deficiencies are found, re-execute Step 5 before releasing any output.",
        "Final_Action": "If refinement was required, set Protocol_State = ACTIVE_RESEARCH to re-run; otherwise set Protocol_State = AWAITING_RESEARCH."
      }
    ],

    "Verification_Summary_Optional": {
      "Description": "Structured summary of evidence reliability across the dataset.",
      "Template": "### Verification Summary\\n- High (≥ 3 independent sources): XX %\\n- Medium (2 non-independent sources): YY %\\n- Low / Limited (≤ 1 source or unverified): ZZ %\\n- Conflicts listed above (if applicable).",
      "Rules": {
        "Display": "Append only after Step 5 and Step 5.5 if verification tiers were computed in Step 3.",
        "Computation": "Aggregate verified_scratchpad confidence tiers to percentage distribution.",
        "Presentation": "Always place below the ranked list conclusion and before Sources section.",
        "Visibility": "User-facing but auto-generated — no manual narration allowed."
      }
    },

    "Execution_Metadata": {
      "Purpose": "Maintain an internal audit record for every Deep-Research cycle.",
      "Includes": {
        "steps_completed": "0 – 5.5",
        "sources_used": "Count and classification summary (official / expert / aggregate / user)",
        "confidence_distribution": "High / Medium / Low percentages from verified_scratchpad",
        "execution_time_estimate": "Internal approximation (ms)",
        "cache_status": "HIT or MISS relative to previous ACTIVE_RESEARCH cycle",
        "conflict_count": "Number of contradictions recorded in Step 3",
        "fidelity_locks": "Count of high_fidelity_mechanistic segments preserved verbatim",
        "refinement_loops": "How many times Step 5 was re-invoked during Step 5.5",
        "output_wordcount": "Total word count of final Markdown report"
      },
      "Persistence": "Internal-only storage; not rendered to user output stream."
    },

    "Integrity_Validation": {
      "Purpose": "Guarantee that all structural, logical, and state components of the Deep_Research_Ultimate_Protocol remain internally coherent before the controller returns an output.",
      "Checks": {
        "Structural": [
          "Confirm that every Step_ID in Execution_Protocol is unique and sequential (0-5.5).",
          "Validate presence of Composition_Model, Confidence_Model, and Tone_Control blocks.",
          "Ensure every reference in Pre_Actions / Post_Actions maps to a valid Step_ID or defined variable."
        ],
        "Logical": [
          "Verify that Protocol_State is one of {ACTIVE_RESEARCH, AWAITING_RESEARCH}.",
          "Check that Confidence_Model.threshold ∈ [0, 1].",
          "Validate that Evidence_Diversity.unique_domains_min ≤ domain_cap_percent."
        ],
        "Output": [
          "Confirm that Output_Constraint exists in Step 5 and Step 5.5.",
          "Ensure that all citations are formatted in parenthetical style if citations > 0.",
          "Guarantee that final Markdown includes a ranked list and closing 'Sources' section."
        ]
      },
      "Failure_Handling": {
        "On_Structural_Error": "Set Protocol_State = 'FAILED_VALIDATION'; output: 'Controller document invalid — structural failure in deepforge.md.'",
        "On_Missing_Component": "Attempt to regenerate minimal stubs for missing Composition_Model or Tone_Control using cached templates; log 'Autopatched component.'",
        "On_Output_Violation": "Force a self-critique loop (Step 5.5) and retry once; if still invalid, flag report as 'PARTIAL_VERIFICATION' and notify controller."
      },
      "Verification_Log": {
        "Retention": "Store transient validation report (not user-visible) summarizing results of all Integrity Checks.",
        "Schema": {
          "timestamp": "ISO-8601 UTC",
          "state_precheck": "ACTIVE_RESEARCH / AWAITING_RESEARCH",
          "state_postcheck": "AWAITING_RESEARCH / FAILED_VALIDATION",
          "errors_detected": "Integer count",
          "errors_patched": "Integer count"
        }
      }
    },

    "Closure": {
      "Summary": "All Directives, Models, Policies, and Steps are now internally validated and finalized.",
      "Final_State": "Protocol_State = AWAITING_RESEARCH",
      "Compatibility": "This protocol is now augmentation-ready and synchronized with the Full-Output Intelligence Protocol.",
      "End_Message": "Deep Research Extension fully integrated and validated."
    }

}
}
