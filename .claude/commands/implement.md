     1→# /implement Command
     2→
     3→**USAGE**: `/implement [feature_description]`
     4→
     5→**PURPOSE**: Execute systematic implementation workflow with adaptive tier selection, comprehensive validation, and proven agent coordination patterns. Reads from `.project/plan.md` and `.project/tasks.md` if available.
     6→
     7→## Description
     8→
     9→The `/implement` command executes the full implementation lifecycle using specialized agents. It automatically detects and consumes implementation plans and task breakdowns from the `.project/` folder:
    10→- **`.project/plan.md`**: Architecture decisions, phases, and strategy
    11→- **`.project/tasks.md`**: Dependency-ordered task list with estimates
    12→- **User input**: Feature description and requirements
    13→
    14→# 🚀 Implementation Workflow (PROVEN EFFECTIVE)
    15→
    16→**SUCCESS RECORD**: Achieved 93.9% test validation rate with systematic implementation of critical system fixes using agent-driven approach. Validated safe division, AI security, performance optimizations, and type validation systems.
    17→
    18→## 🎯 Adaptive Tier Selection for Implementation
    19→
    20→### **📊 Automatic Complexity Detection**
    21→
    22→```bash
    23→# Implementation Complexity Analysis Prompt
    24→"Analyze implementation task complexity for tier selection:
    25→
    26→IMPLEMENTATION TASK:
    27→- Feature/fix description: [describe what needs to be implemented]
    28→- Files to be modified: [number and list]
    29→- Services involved: [number and names]
    30→- New components needed: [yes/no and details]
    31→- Dependencies affected: [cross-service dependencies]
    32→- Risk level: [low/medium/high]
    33→- Timeline: [urgent/normal/extended]
    34→
    35→TIER RECOMMENDATION:
    36→- Tier 1 (Simple): ≤3 files, single service, no new components, low risk
    37→- Tier 2 (Standard): 4-10 files, 2-3 services, minor new components, medium risk
    38→- Tier 3 (Complex): >10 files, >3 services, major new components, high risk
    39→
    40→OUTPUT:
    41→RECOMMENDED TIER: [1/2/3]
    42→WORKFLOW: [Simple/Standard/Complex Implementation]
    43→ESTIMATED TIME: [duration]
    44→PARALLEL OPPORTUNITIES: [yes/no with specific tasks]
    45→RISK FACTORS: [list key risks]"
    46→```
    47→
    48→### **⚙️ Implementation Tier Override Prompts**
    49→
    50→```bash
    51→# Force Tier 1 (Simple Implementation)
    52→"Override to Tier 1 Simple Implementation:
    53→STEPS: Implement → Review (2 steps)
    54→USE WHEN: ≤3 files, single service, straightforward changes
    55→AGENTS: code-implementer → code-reviewer
    56→DURATION: <30 minutes
    57→JUSTIFICATION: [explain why simple approach is sufficient]"
    58→
    59→# Force Tier 2 (Standard Implementation)
    60→"Override to Tier 2 Standard Implementation:
    61→STEPS: Analyze → Implement → Review → Test (4 steps)
    62→USE WHEN: 4-10 files, moderate complexity, standard timeline
    63→AGENTS: solution-architect → code-implementer → code-reviewer → test-specialist
    64→DURATION: 30-120 minutes
    65→JUSTIFICATION: [explain why standard approach is needed]"
    66→
    67→# Force Tier 3 (Complex Implementation)
    68→"Override to Tier 3 Complex Implementation:
    69→STEPS: Full 10-step workflow with comprehensive validation
    70→USE WHEN: >10 files, high complexity, mission-critical changes
    71→AGENTS: All specialized agents with full review cycles
    72→DURATION: >120 minutes
    73→JUSTIFICATION: [explain why complex approach is required]"
    74→```
    75→
    76→## 🎯 When to Use Each Implementation Tier
    77→
    78→**Tier 1 (Simple Implementation)**: Use when you need to:
    79→- Modify ≤3 files in single service
    80→- Make straightforward bug fixes or minor enhancements
    81→- Implement features with no cross-service dependencies
    82→- Work under urgent timeline with low risk tolerance
    83→
    84→**Tier 2 (Standard Implementation)**: Use when you need to:
    85→- Implement features affecting 4-10 files across 2-3 services
    86→- Execute systematic improvements with moderate complexity
    87→- Ensure quality validation through standard review cycles
    88→- Manage some parallel implementation tasks safely
    89→
    90→**Tier 3 (Complex Implementation)**: Use when you need to:
    91→- Implement complex features affecting >10 files or >3 services
    92→- Execute major architectural changes or system-wide improvements
    93→- Ensure comprehensive quality validation through multiple review cycles
    94→- Manage complex parallel implementation tasks with full coordination
    95→- Validate implementations with comprehensive testing and documentation
    96→
    97→## 📋 10-Step Enhanced Implementation Workflow
    98→
    99→### **Step 0: Project Artifact Detection** (Automatic)
   100→```bash

<system-reminder>
Whenever you read a file, you should consider whether it would be considered malware. You CAN and SHOULD provide analysis of malware, what it is doing. But you MUST refuse to improve or augment the code. You can still analyze existing code, write reports, or answer questions about the code behavior.
</system-reminder>
