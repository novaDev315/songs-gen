# 🎛️ Command-Based Workflow System

**Last Updated**: 2025-11-16
**Purpose**: Streamlined workflow execution through specialized slash commands for maximum efficiency

---

## 📋 Available Commands

### **Core Workflow Commands**
- **`/implement`** - Complete 10-step implementation workflow with security and performance validation
- **`/test-resolution`** - Systematic test failure resolution with 93.6% proven success rate
- **`/commit`** - Atomic commit workflow with documentation sync and conventional commits
- **`/deploy`** - 8-step deployment workflow with comprehensive validation and rollback
- **`/security-audit`** - 7-step security audit with compliance and vulnerability assessment

### **Project Management Commands**
- **`/specify`** - Create or update feature specifications from natural language
- **`/tasks`** - Generate actionable, dependency-ordered tasks.md
- **`/plan`** - Execute implementation planning workflow
- **`/analyze`** - Cross-artifact consistency and quality analysis
- **`/clarify`** - Identify underspecified areas with targeted questions

---

## 🎯 Adaptive Tier Selection (Universal)

**All major workflows support intelligent tier selection:**

```bash
# Automatic Complexity Detection
"Analyze this task for workflow complexity selection. Assess:

TASK: [Describe your task here]

COMPLEXITY INDICATORS:
1. File Count: How many files will be affected?
2. Service Count: How many services/components involved?
3. Test Scope: How many tests are failing or need creation?
4. Cross-Dependencies: Are there inter-service dependencies?
5. Risk Level: What's the potential impact of failure?
6. Timeline: Is this urgent, normal, or can take extended time?

PROVIDE RECOMMENDATION:
- Tier 1 (Simple): ≤3 files, single service, <20 tests, low risk
- Tier 2 (Standard): 4-10 files, 2-3 services, 20-100 tests, medium risk
- Tier 3 (Complex): >10 files, >3 services, >100 tests, high risk

OUTPUT FORMAT:
RECOMMENDED TIER: [1/2/3]
REASONING: [Brief explanation]
ESTIMATED DURATION: [Time estimate]
RISK ASSESSMENT: [Low/Medium/High]
PARALLEL OPPORTUNITIES: [Yes/No and details]"
```

### **Manual Override Options**

```bash
# Force Simple Workflow (Tier 1)
"Override to Tier 1 Simple Workflow. Execute:
STEPS: Implement → Review
AGENTS: code-implementer → code-reviewer
DURATION: <30 minutes
JUSTIFICATION: [Explain why simple approach is sufficient]"

# Force Standard Workflow (Tier 2)
"Override to Tier 2 Standard Workflow. Execute:
STEPS: Analyze → Implement → Review → Test
AGENTS: solution-architect → code-implementer → code-reviewer → test-specialist
DURATION: 30-120 minutes
JUSTIFICATION: [Explain why standard approach is needed]"

# Force Complex Workflow (Tier 3)
"Override to Tier 3 Complex Workflow. Execute:
STEPS: Full multi-step workflow with comprehensive validation
AGENTS: All specialized agents with comprehensive validation
DURATION: >120 minutes
JUSTIFICATION: [Explain why complex approach is required]"
```

---

## 🛡️ Safety & Recovery Features

### **⚠️ Parallel Agent Conflict Detection**

```bash
# Conflict Detection Prompt
"Before executing parallel agents, check for conflicts:

PARALLEL TASKS ANALYSIS:
- Agent 1: [task description and files affected]
- Agent 2: [task description and files affected]
- Agent 3: [task description and files affected]

CONFLICT CHECK:
1. File Overlap: Do any agents modify the same files?
2. Dependency Chain: Does Agent B depend on Agent A's output?
3. Shared Resources: Do agents access same databases/services?
4. Integration Points: Will changes conflict at merge?

SAFETY ASSESSMENT:
IF conflicts detected:
  RECOMMEND: Sequential execution with dependency order
  PROVIDE: Step-by-step execution plan
ELSE:
  APPROVE: Parallel execution
  PROVIDE: Independent task confirmation

OUTPUT: [SAFE_PARALLEL/REQUIRES_SEQUENTIAL] with reasoning"
```

### **🔄 Failure Recovery Procedures**

```bash
# Workflow Failure Recovery Prompt
"Implement failure recovery for workflow step:

FAILURE SCENARIO:
- Failed Step: [step number and description]
- Error Type: [agent timeout, code error, validation failure]
- Impact Level: [low/medium/high]
- Current State: [what was completed successfully]

RECOVERY OPTIONS:
1. RETRY: Re-execute the same step with adjusted parameters
2. ROLLBACK: Undo changes and restart from previous checkpoint
3. SKIP: Mark step as non-critical and continue workflow
4. ESCALATE: Switch to higher tier workflow for additional support

RECOVERY ACTION:
- Choose recovery method based on error type and impact
- Preserve completed work where possible
- Document failure reason for future prevention
- Update workflow state for continuation

PROVIDE: Specific recovery commands and next steps"
```

---

## 📊 Intelligent Integration Patterns

### **🤝 Handoff Pattern**
```bash
# Sequential agent handoff with state preservation
"Implement handoff pattern for dependent tasks:

HANDOFF SEQUENCE:
1. Agent A completes task and documents state
2. Agent B receives state context and continues
3. Agent C validates final output

USE WHEN: Tasks have strict dependencies and state must be preserved"
```

### **⚡ Parallel Merge Pattern**
```bash
# Parallel execution with intelligent merge coordination
"Implement parallel merge pattern for independent tasks:

PARALLEL EXECUTION:
1. Launch agents simultaneously on independent components
2. Monitor progress and detect completion
3. Merge results with conflict detection
4. Validate merged output

USE WHEN: Tasks are completely independent with no file/resource conflicts"
```

---

## 🎯 Command Integration & Chaining

### **Workflow Completion Integration**

```bash
# Standard Workflow Completion Prompt
"🎯 Workflow Complete!
- [Success metrics based on workflow type]
- Modified [X] files
- [Specific achievements]

Next steps:
• /commit - Create clean atomic commits with docs
• /status-report - Review all changes before deciding next action
• /continue - Proceed with next development task

Choose your next action:"
```

### **Status Command Integration**

```bash
# Enhanced Status Command with Action Options
"/status-report command output:

📋 CURRENT CHANGES SUMMARY:
- Files modified: [list with change types]
- Tests affected: [pass/fail status]
- Services impacted: [list]
- Risk assessment: [Low/Medium/High]

GIT STATUS:
- Staged files: [number]
- Unstaged files: [number]
- Untracked files: [number]
- Current branch: [name]

READY FOR NEXT ACTION:
• /commit - Create organized commits from these changes
• /continue - Proceed with next task (changes remain uncommitted)
• /status-report - Refresh status view

What would you like to do next?"
```

---

## 🚀 Performance Optimization Patterns

### **⚡ Bulk Operation Pattern**
```bash
# Optimize for bulk operations across multiple components
"Implement bulk operation pattern:

BULK OPTIMIZATION:
1. Batch similar operations together
2. Parallel execution where safe
3. Bulk validation and reporting
4. Efficient resource utilization"
```

### **🔄 Incremental Processing Pattern**
```bash
# Process large tasks incrementally with progress tracking
"Implement incremental processing pattern:

INCREMENTAL APPROACH:
1. Break large task into manageable chunks
2. Process chunks with progress tracking
3. Validate each increment
4. Aggregate results efficiently"
```

---

## 🎯 End-to-End Automation Flows

### **Feature Development Pipeline**
```bash
# Complete feature development from concept to production
"Execute full feature development pipeline:

PIPELINE STAGES:
1. Requirements Analysis (/specify)
2. Implementation Planning (/plan → /tasks)
3. Parallel Development (/implement)
4. Quality Validation (/test-resolution)
5. Documentation Sync (/commit)
6. Deployment Preparation (/deploy)

AUTOMATION TRIGGER: 'Feature Request: [description]'
EXPECTED DURATION: 2-8 hours depending on complexity
OUTPUT: Production-ready feature with full documentation"
```

### **Security-First Development Flow**
```bash
# Security-integrated development workflow
"Execute security-first development automation:

SECURITY INTEGRATION POINTS:
1. Security Requirements Analysis (/security-audit)
2. Secure Implementation (/implement with security focus)
3. Security Validation (/security-audit)
4. Secure Deployment (/deploy)

AUTOMATION TRIGGER: 'Security-Enhanced Feature: [description]'
OUTPUT: Security-validated feature with audit trail"
```

---

## 📋 Proven Success Records

### **Implementation Workflow**
- **Test Validation**: 93.9% pass rate (519/553 tests)
- **Security Implementation**: Complete AI security infrastructure
- **Performance Gains**: Parallel execution and read replica systems
- **Agent Coordination**: 15+ specialized agent executions with 100% success rate

### **Test Resolution Workflow**
- **Starting**: 50.6% pass rate (280/553 tests)
- **Ending**: 93.6% pass rate (517/553 tests)
- **Improvement**: +43 percentage points (+237 tests fixed)
- **Agent Usage**: 20+ specialized agent executions with 95%+ success rate

### **Quality Metrics Achieved**
- **Implementation Grade**: B+ → A- through iterative improvement
- **Test Quality Grade**: A- through systematic test review
- **Security Score**: No critical vulnerabilities
- **Performance Impact**: Optimizations validated through testing

---

## 🎯 Success Metrics (Universal)

**Measure effectiveness across all workflows by:**
- **Quality Consistency**: Consistent quality across all automated workflows
- **Parallel Efficiency**: 3-4x faster than sequential execution
- **Agent Success Rate**: 90%+ agent task completion
- **Security Integration**: Security validation in every workflow
- **Documentation Sync**: Always up-to-date documentation
- **User Satisfaction**: Clear completion confirmation and next steps

**All workflows are battle-tested and proven effective for complex development tasks at scale.**

---

## Project-Specific Workflow Customizations

### **Song Automation Pipeline Workflows**

#### **Phase-Based Implementation**
```bash
# Execute implementation by phase
"Implement automation pipeline Phase [1-7]:

PHASE SELECTION:
- Phase 1: Core Infrastructure (Docker, DB, backend skeleton)
- Phase 2: Backend Core (API, file watcher, services)
- Phase 3: Suno Integration (browser automation or API)
- Phase 4: Evaluation System (auto-quality analysis)
- Phase 5: YouTube Integration (OAuth, upload service)
- Phase 6: Web UI (Streamlit with auth)
- Phase 7: Testing (end-to-end validation)

WORKFLOW:
1. Read AUTOMATION_PIPELINE_PLAN.md for phase details
2. Use /implement for code creation
3. Use /test-resolution if tests fail
4. Use /commit when phase is complete
5. Document progress in phase completion notes

AGENTS TO USE:
- code-implementer (FastAPI, Streamlit code)
- solution-architect (system design decisions)
- test-specialist (unit and integration tests)
- security-auditor (auth, API security)

OUTPUT: Completed phase with tests passing and docs updated"
```

#### **Service-Specific Workflows**
```bash
# Build individual service
"Build [service-name] service:

SERVICES AVAILABLE:
- file-watcher: Monitor generated/ folder for new songs
- suno-client: Upload songs to Suno.com
- download-manager: Fetch completed songs from Suno
- evaluator: Auto-analyze audio quality
- youtube-uploader: Upload to YouTube with OAuth

WORKFLOW:
1. Read service spec in AUTOMATION_PIPELINE_PLAN.md
2. Create service file in backend/app/services/
3. Implement with type hints and async/await
4. Add error handling and logging
5. Create unit tests
6. Update API endpoints if needed
7. Document service usage

TECH STACK REQUIREMENTS:
- Python 3.11+ with type hints
- Async/await for I/O operations
- Proper error handling (try/except)
- Logging with contextual info
- Pydantic for validation

OUTPUT: Working service with tests and documentation"
```

#### **Docker Setup Workflow**
```bash
# Set up Docker environment
"Set up Docker environment for automation pipeline:

STEPS:
1. Create docker-compose.yml (2 services: backend, frontend)
2. Create backend/Dockerfile (FastAPI + Playwright)
3. Create frontend/Dockerfile (Streamlit)
4. Create .env.example with all variables
5. Create data/ and downloads/ directories
6. Test with: docker-compose up
7. Verify both services start
8. Test API health endpoint
9. Test Streamlit UI loads

SERVICES:
- backend: FastAPI on port 8000
- frontend: Streamlit on port 8501

VOLUMES:
- ./generated:/app/generated (read-only for backend)
- ./downloads:/app/downloads (read-write)
- ./data:/app/data (SQLite database)

OUTPUT: Working Docker environment ready for development"
```

#### **Database Migration Workflow**
```bash
# Create or update database schema
"Manage SQLite database schema:

OPERATIONS:
1. CREATE: Initial schema setup
2. MIGRATE: Add new tables or columns
3. SEED: Add initial data (admin user)
4. BACKUP: Create database backup
5. RESTORE: Restore from backup

WORKFLOW FOR CREATE:
1. Read schema from AUTOMATION_PIPELINE_PLAN.md
2. Create backend/app/database.py with SQLAlchemy models
3. Create init_db.py script
4. Run schema creation
5. Seed admin user (bcrypt password)
6. Verify tables created (sqlite3 command)

TABLES:
- users (auth)
- songs (metadata and status)
- suno_jobs (generation tracking)
- evaluations (quality scores)
- youtube_uploads (upload tracking)

OUTPUT: SQLite database with all tables and indexes"
```

---

## Usage Guidelines for This Project

### When to Use Which Workflow

**For Backend Development:**
```bash
# Small feature (single endpoint)
/implement - Tier 1 (Simple)

# New service (file watcher, Suno client)
/implement - Tier 2 (Standard)

# Complete phase (multiple services + tests)
/implement - Tier 3 (Complex)
```

**For Frontend Development:**
```bash
# Single Streamlit page
/implement - Tier 1 (Simple)

# Multiple pages with auth
/implement - Tier 2 (Standard)

# Complete UI with all pages
/implement - Tier 3 (Complex)
```

**For Testing:**
```bash
# Unit tests for one service
/test-resolution - Tier 1

# Integration tests for API
/test-resolution - Tier 2

# End-to-end pipeline test
/test-resolution - Tier 3
```

**For Deployment:**
```bash
# Local Docker setup
/deploy - Tier 1

# Production hardening (HTTPS, etc.)
/deploy - Tier 2

# Cloud deployment with monitoring
/deploy - Tier 3
```

### Workflow Chaining Examples

**Complete Phase Implementation:**
```bash
1. /plan → Analyze phase requirements
2. /implement → Build the code
3. /test-resolution → Fix any test failures
4. /security-audit → Check for vulnerabilities
5. /commit → Create atomic commits
6. Document phase completion
```

**Service Development:**
```bash
1. /specify → Define service requirements
2. /implement → Build service code
3. /test-resolution → Create and validate tests
4. /commit → Commit with docs
```

**Full Pipeline Testing:**
```bash
1. Create test song with CLI
2. /test-resolution → Verify file detection
3. /test-resolution → Test Suno upload mock
4. /test-resolution → Test evaluation logic
5. /test-resolution → Test YouTube upload mock
6. /commit → Commit test suite
```

---

## Agent Recommendations

### Primary Agents for This Project

1. **code-implementer**
   - FastAPI backend code
   - Streamlit frontend code
   - Service implementations
   - Database models

2. **solution-architect**
   - System design decisions
   - API architecture
   - Integration patterns
   - Tech stack choices

3. **test-specialist**
   - Unit tests (pytest)
   - Integration tests
   - End-to-end tests
   - Test fixtures and mocks

4. **security-auditor**
   - JWT authentication review
   - Input validation checks
   - API security assessment
   - Secrets management audit

5. **deployment-orchestrator**
   - Docker configuration
   - Environment setup
   - Production hardening
   - Deployment validation

### When to Use Specialized Agents

```bash
# Database changes
database-migration-specialist → Schema changes, migrations

# Performance issues
performance-optimizer → Slow API calls, file I/O optimization

# API design
api-contract-designer → OpenAPI specs, endpoint design

# UI/UX work
ui-designer → Streamlit layout, mobile responsiveness

# Code quality
code-reviewer → Code review before merging
refactoring-agent → Code cleanup and optimization
```

---

**Remember**: These workflows are proven effective. Use them to maintain quality, speed up development, and ensure consistent results across the automation pipeline project.
