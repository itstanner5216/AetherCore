// ===========================================================
// Gemini-Hybrid v2.1
// External Intelligence Coprocessor for ProjectGPT
// Node Runtime — USIF Compatible
// ===========================================================

/**
 - Main invocation function for Gemini-Hybrid external intelligence
 - @param {Object} payload - Configuration object for Gemini API call
 - @param {string} payload.api_key - Gemini API key (required)
 - @param {string} payload.prompt - Text prompt to send to Gemini (required)
 - @param {string} [payload.model="gemini-2.0-flash"] - Model to use
 - @param {number} [payload.max_tokens=4096] - Maximum output tokens
 - @param {number} [payload.temperature=0.4] - Temperature for generation
 - @param {Object} [payload.context] - Additional context from orchestrator
 - @returns {Promise<Object>} Structured response with status, evidence, and metadata
 */
export async function geminiHybridInvoke(payload = {}) {
  const {
    api_key = "",
    prompt = "",
    model = "gemini-2.0-flash",
    max_tokens = 4096,
    temperature = 0.4,
    context = {}
  } = payload;

  // ————————
  // 1. Input Validation
  // ————————
  if (!api_key || typeof api_key !== "string") {
    return {
      status: "error",
      origin: "gemini_hybrid",
      error: "Missing or invalid Gemini API key.",
      timestamp: Date.now()
    };
  }

  if (typeof prompt !== "string" || prompt.trim().length === 0) {
    return {
      status: "error",
      origin: "gemini_hybrid",
      error: "Invalid or missing prompt.",
      timestamp: Date.now()
    };
  }

  // ————————
  // 2. Model Selection & Validation
  // ————————
  const allowedModels = ["gemini-2.0-flash", "gemini-2.5-pro"];
  const selectedModel = allowedModels.includes(model) ? model : "gemini-2.0-flash"; // fallback to flash

  // Log model selection reasoning if context provided
  const modelSelectionReason = (context && (context.attempts >= 2 || context.depth === "deep")) ? "pro_escalation" : "flash_default";

  // ————————
  // 3. Construct API Endpoint
  // ————————
  const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${selectedModel}:generateContent?key=${api_key}`;

  const requestBody = {
    contents: [
      {
        parts: [{ text: prompt }]
      }
    ],
    generationConfig: {
      maxOutputTokens: max_tokens,
      temperature: temperature
    }
  };

  // ————————
  // 4. Execute API Request
  // ————————
  const startTime = Date.now();

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(requestBody)
    });

    const responseTime = Date.now() - startTime;

    // ------------------------
    // 5. Parse Response
    // ------------------------
    if (!response.ok) {
      return {
        status: "error",
        origin: "gemini_hybrid",
        error: `HTTP ${response.status}: ${response.statusText}`,
        timestamp: Date.now(),
        metadata: {
          model_requested: selectedModel,
          response_time_ms: responseTime
        }
      };
    }

    const json = await response.json();

    // ------------------------
    // 6. Gemini Error Detection
    // ------------------------
    if (json.error) {
      return {
        status: "error",
        origin: "gemini_hybrid",
        error: json.error.message || "Gemini API returned an error.",
        details: json.error,
        timestamp: Date.now(),
        metadata: {
          model_requested: selectedModel,
          response_time_ms: responseTime
        }
      };
    }

    // ------------------------
    // 7. Extract Output with Fallback Chain
    // ------------------------
    const text =
      json?.candidates?.[0]?.content?.parts?.[0]?.text ||
      json?.candidates?.[0]?.content?.parts?.[0]?.rawText ||
      json?.text ||
      "";

    if (!text || text.trim().length === 0) {
      return {
        status: "error",
        origin: "gemini_hybrid",
        error: "Gemini returned empty response.",
        timestamp: Date.now(),
        metadata: {
          model_used: selectedModel,
          response_time_ms: responseTime
        }
      };
    }

    // ------------------------
    // 8. Success Response with Enhanced Metadata
    // ------------------------
    return {
      status: "ok",
      origin: "gemini_hybrid",
      evidence: text,
      metadata: {
        model_used: selectedModel,
        model_selection_reason: modelSelectionReason,
        tokens_used: json?.usageMetadata?.totalTokenCount || null,
        prompt_tokens: json?.usageMetadata?.promptTokenCount || null,
        response_tokens: json?.usageMetadata?.candidatesTokenCount || null,
        response_time_ms: responseTime,
        timestamp: Date.now(),
        context_provided: Object.keys(context || {}).length > 0
      }
    };
  } catch (err) {
    // ————————
    // 9. Fatal Error Fail-Safe
    // ————————
    return {
      status: "error",
      origin: "gemini_hybrid",
      error: err.message || "Unknown network failure during Gemini API call.",
      error_type: err.name || "UnknownError",
      timestamp: Date.now(),
      metadata: {
        model_requested: selectedModel,
        response_time_ms: Date.now() - startTime
      }
    };
  }
}

/**
 - Helper function to construct optimal prompts for Gemini based on task type
 - @param {string} userQuery - The original user query
 - @param {Object} context - Task context from orchestrator
 - @returns {string} Optimized prompt for Gemini
 */
export function constructGeminiPrompt(userQuery, context = {}) {
  const { task_type = "logic", attempts = 1, flags = {} } = context;

  let systemInstruction = "";

  switch (task_type) {
    case "code":
      systemInstruction = "You are an expert software engineer debugging complex issues. Provide detailed analysis with code examples.";
      break;
    case "research":
      systemInstruction = "You are a thorough researcher. Provide evidence-backed analysis with clear reasoning chains.";
      break;
    case "products":
      systemInstruction = "You are a product research specialist. Find and structure comprehensive product information.";
      break;
    default:
      systemInstruction = "You are a precise reasoning engine. Provide clear, structured analysis.";
  }

  const escalationNote = attempts > 1
    ? `\n\nNOTE: This is escalation attempt #${attempts}. Previous attempts were insufficient.`
    : "";

  return `${systemInstruction}${escalationNote}\n\nTask:\n${userQuery}`;
}

// Export version for compatibility checking
export const VERSION = "2.1";
export const SUPPORTED_MODELS = ["gemini-2.0-flash", "gemini-2.5-pro"];
