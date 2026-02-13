import type { ThreatCategory } from "../types.js";

// =============================================================================
// Pattern Library
//
// Each pattern has a regex, category, base confidence, and description.
// Confidence is adjusted at scan time based on context (e.g., tool results
// get a boost because indirect injection is higher-signal there).
// =============================================================================

export interface ThreatPattern {
  id: string;
  regex: RegExp;
  category: ThreatCategory;
  confidence: number;
  description: string;
}

export const THREAT_PATTERNS: ThreatPattern[] = [
  // --- Direct Prompt Injection ---
  {
    id: "PI-001",
    regex: /ignore\s+(all\s+)?(previous|prior|above|earlier|preceding)\s+(instructions?|prompts?|rules?|directives?)/i,
    category: "prompt_injection",
    confidence: 0.95,
    description: "Classic 'ignore previous instructions' pattern",
  },
  {
    id: "PI-002",
    regex: /disregard\s+(all\s+)?(previous|prior|above|your)\s+(instructions?|programming|guidelines?|rules?)/i,
    category: "prompt_injection",
    confidence: 0.95,
    description: "Disregard instructions variant",
  },
  {
    id: "PI-003",
    regex: /you\s+are\s+now\s+(a|an|in)\s+/i,
    category: "prompt_injection",
    confidence: 0.6,
    description: "Identity reassignment attempt (low confidence — common in legit prompts)",
  },
  {
    id: "PI-004",
    regex: /new\s+instructions?:?\s/i,
    category: "prompt_injection",
    confidence: 0.7,
    description: "Instruction injection via 'new instructions' framing",
  },
  {
    id: "PI-005",
    regex: /\[system\]|\[INST\]|<\|system\|>|<\|im_start\|>system/i,
    category: "prompt_injection",
    confidence: 0.9,
    description: "Chat template delimiter injection",
  },
  {
    id: "PI-006",
    regex: /```system\s*\n|<system_prompt>|<\/system_prompt>/i,
    category: "prompt_injection",
    confidence: 0.85,
    description: "System prompt block injection via code fences or XML tags",
  },

  // --- Jailbreak ---
  {
    id: "JB-001",
    regex: /DAN\s+(mode|prompt)|do\s+anything\s+now/i,
    category: "jailbreak",
    confidence: 0.9,
    description: "DAN jailbreak pattern",
  },
  {
    id: "JB-002",
    regex: /developer\s+mode\s+(enabled|activated|on)|maintenance\s+mode/i,
    category: "jailbreak",
    confidence: 0.85,
    description: "Developer/maintenance mode activation",
  },
  {
    id: "JB-003",
    regex: /act\s+as\s+(if\s+)?(you\s+have\s+)?no\s+(restrictions?|limitations?|filters?|guardrails?)/i,
    category: "jailbreak",
    confidence: 0.9,
    description: "Restriction removal prompt",
  },
  {
    id: "JB-004",
    regex: /pretend\s+(that\s+)?(you\s+)?(are|have)\s+(no|unrestricted|unlimited)/i,
    category: "jailbreak",
    confidence: 0.85,
    description: "Pretend-no-restrictions pattern",
  },
  {
    id: "JB-005",
    regex: /hypothetical(ly)?\s*(,\s*)?(if|what\s+if|suppose|imagine)\s+.{0,40}(no\s+rules?|no\s+restrictions?|could\s+do\s+anything)/i,
    category: "jailbreak",
    confidence: 0.75,
    description: "Hypothetical framing to bypass restrictions",
  },
  {
    id: "JB-006",
    regex: /respond\s+(to\s+every\s+prompt|without).{0,40}(moral|filter|censor|restrict)/i,
    category: "jailbreak",
    confidence: 0.85,
    description: "Respond-without-filter jailbreak pattern",
  },
  {
    id: "JB-007",
    regex: /you\s+(are|will\s+be|play)\s+(a\s+character\s+named|the\s+role\s+of|now)\s+\w+/i,
    category: "jailbreak",
    confidence: 0.7,
    description: "Character/role-play persona override",
  },
  {
    id: "JB-008",
    regex: /\[(system|INST)\].*?(no\s+rules?|no\s+restrictions?|unlimited|uncensored)/i,
    category: "jailbreak",
    confidence: 0.9,
    description: "Bracket-based persona override with restriction removal",
  },
  {
    id: "JB-009",
    regex: /simulate\s+(developer\s+mode|a\s+conversation\s+where\s+you\s+act)/i,
    category: "jailbreak",
    confidence: 0.85,
    description: "Simulate developer mode jailbreak",
  },

  // --- Instruction Override ---
  {
    id: "IO-001",
    regex: /forget\s+(everything|all|what)\s+(you|about)/i,
    category: "instruction_override",
    confidence: 0.8,
    description: "Memory/context wipe attempt",
  },
  {
    id: "IO-002",
    regex: /override\s+(your|the|all)\s+(safety|security|system|previous)/i,
    category: "instruction_override",
    confidence: 0.9,
    description: "Explicit override attempt",
  },
  {
    id: "IO-003",
    regex: /from\s+now\s+on,?\s+(you\s+)?(will|must|should|are\s+going\s+to)\s/i,
    category: "instruction_override",
    confidence: 0.7,
    description: "Persistent instruction injection",
  },

  // --- Data Exfiltration ---
  {
    id: "DE-001",
    regex: /repeat\s+(your|the)\s+(system\s+)?(prompt|instructions?|rules?|guidelines?)/i,
    category: "data_exfiltration",
    confidence: 0.85,
    description: "System prompt extraction attempt",
  },
  {
    id: "DE-002",
    regex: /show\s+me\s+(your|the)\s+(system|hidden|secret|internal)\s+(prompt|message|instructions?)/i,
    category: "data_exfiltration",
    confidence: 0.85,
    description: "System prompt reveal request",
  },
  {
    id: "DE-003",
    regex: /what\s+(are|were)\s+(your|the)\s+(original|initial|first|system)\s+(instructions?|prompt|rules?)/i,
    category: "data_exfiltration",
    confidence: 0.8,
    description: "Original instructions probing",
  },
  {
    id: "DE-004",
    regex: /output\s+(all|every|the\s+entire)\s+(conversation|context|history|session)/i,
    category: "data_exfiltration",
    confidence: 0.75,
    description: "Full context dump request",
  },
  {
    id: "DE-005",
    regex: /repeat\s+(the\s+)?(words|text|everything|content)\s+(above|before)/i,
    category: "data_exfiltration",
    confidence: 0.85,
    description: "Prompt stealing via 'repeat the words above' variant",
  },
  {
    id: "DE-006",
    regex: /paste\s+(your|the)\s+(system\s+)?(prompt|instructions?|configuration)\s+(here|below)/i,
    category: "data_exfiltration",
    confidence: 0.85,
    description: "Prompt stealing via 'paste your system prompt here'",
  },
  {
    id: "DE-007",
    regex: /(list|share|tell\s+me)\s+(the\s+)?(top\s+\d+\s+)?(guidelines?|rules?|instructions?)\s+you\s+follow/i,
    category: "data_exfiltration",
    confidence: 0.8,
    description: "Prompt stealing via 'list the guidelines you follow'",
  },

  // --- Social Engineering ---
  {
    id: "SE-001",
    regex: /i\s+am\s+(your|the)\s+(developer|creator|admin|owner|operator|master)/i,
    category: "social_engineering",
    confidence: 0.8,
    description: "False authority claim",
  },
  {
    id: "SE-002",
    regex: /this\s+is\s+(a|an)\s+(authorized|official|approved)\s+(test|audit|security\s+check)/i,
    category: "social_engineering",
    confidence: 0.75,
    description: "Fake authorization context",
  },
  {
    id: "SE-003",
    regex: /anthropic|openai|peter\s+steinberger|openclaw\s+team/i,
    category: "social_engineering",
    confidence: 0.5,
    description: "Name-dropping authority figures (needs context)",
  },
  {
    id: "SE-004",
    regex: /i('m|am)\s+(your|the|a)\s+(technical\s+)?(maintainer|debugger)/i,
    category: "social_engineering",
    confidence: 0.8,
    description: "False maintainer/debugger authority claim",
  },
  {
    id: "SE-005",
    regex: /share\s+(your|the)\s+(configuration|config|settings?)\s+(for\s+)?(security\s+)?(verification|audit|review)/i,
    category: "social_engineering",
    confidence: 0.8,
    description: "Config extraction via fake security audit framing",
  },

  // --- Tool Abuse ---
  {
    id: "TA-001",
    regex: /exec\s*\(\s*['"`]|child_process|spawn\s*\(|eval\s*\(/i,
    category: "tool_abuse",
    confidence: 0.85,
    description: "Code execution injection in message content",
  },
  {
    id: "TA-002",
    regex: /curl\s+.*\|\s*(sh|bash|zsh)|wget\s+.*\|\s*(sh|bash)/i,
    category: "tool_abuse",
    confidence: 0.9,
    description: "Pipe-to-shell command injection",
  },
  {
    id: "TA-003",
    regex: /rm\s+-rf\s+[\/~]|mkfs|dd\s+if=.*of=\/dev/i,
    category: "tool_abuse",
    confidence: 0.95,
    description: "Destructive system command",
  },

  // --- Indirect Injection (tool results / documents) ---
  {
    id: "II-001",
    regex: /IMPORTANT:\s*(ignore|disregard|forget|override)/i,
    category: "indirect_injection",
    confidence: 0.9,
    description: "Embedded instruction in document/tool result",
  },
  {
    id: "II-002",
    regex: /<!--\s*(system|instruction|prompt|ignore)/i,
    category: "indirect_injection",
    confidence: 0.9,
    description: "HTML comment hidden instruction",
  },
  {
    id: "II-003",
    regex: /\u200b|\u200c|\u200d|\u2060|\ufeff/,
    category: "indirect_injection",
    confidence: 0.6,
    description: "Zero-width character steganography (may be benign)",
  },
  {
    id: "II-004",
    regex: /\[hidden\]|\[invisible\]|display:\s*none|visibility:\s*hidden/i,
    category: "indirect_injection",
    confidence: 0.7,
    description: "Hidden content markers",
  },
  {
    id: "II-005",
    regex: /the\s+(code|table|function)\s+(below\s+)?needs\s+improvement.{0,80}(enhance|improve|add\s+more\s+detail)/i,
    category: "indirect_injection",
    confidence: 0.7,
    description: "Code/table wrapper hiding malicious intent",
  },
];

// Patterns with elevated confidence when found in tool results
// (indirect injection is higher signal in untrusted content)
export const TOOL_RESULT_BOOST_CATEGORIES: ThreatCategory[] = [
  "indirect_injection",
  "prompt_injection",
  "instruction_override",
  "jailbreak",
];

export const TOOL_RESULT_CONFIDENCE_BOOST = 0.15;
