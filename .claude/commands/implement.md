# /implement Command

**USAGE**: `/implement [feature_description]`

**PURPOSE**: Execute systematic implementation workflow with adaptive tier selection, comprehensive validation, and proven agent coordination patterns. Reads from `.project/plan.md` and `.project/tasks.md` if available.

## Description

The `/implement` command executes the full implementation lifecycle using specialized agents. It automatically detects and consumes implementation plans and task breakdowns from the `.project/` folder:
- **`.project/plan.md`**: Architecture decisions, phases, and strategy
- **`.project/tasks.md`**: Dependency-ordered task list with estimates
- **User input**: Feature description and requirements

# 🚀 Implementation Workflow (PROVEN EFFECTIVE)

**SUCCESS RECORD**: Achieved 93.9% test validation rate with systematic implementation of critical system fixes using agent-driven approach. Validated safe division, AI security, performance optimizations, and type validation systems.

## 🎯 Adaptive Tier Selection for Implementation

### **📊 Automatic Complexity Detection**

```bash
# Implementation Complexity Analysis Prompt
"Analyze implementation task complexity for tier selection:

IMPLEMENTATION TASK:
- Feature/fix description: [describe what needs to be implemented]
- Files to be modified: [number and list]
- Services involved: [number and names]
- New components needed: [yes/no and details]
- Dependencies affected: [cross-service dependencies]
- Risk level: [low/medium/high]
- Timeline: [urgent/normal/extended]

TIER RECOMMENDATION:
- Tier 1 (Simple): ≤3 files, single service, no new components, low risk
- Tier 2 (Standard): 4-10 files, 2-3 services, minor new components, medium risk
- Tier 3 (Complex): >10 files, >3 services, major new components, high risk

OUTPUT:
RECOMMENDED TIER: [1/2/3]
WORKFLOW: [Simple/Standard/Complex Implementation]
ESTIMATED TIME: [duration]
PARALLEL OPPORTUNITIES: [yes/no with specific tasks]
RISK FACTORS: [list key risks]"
```

### **⚙️ Implementation Tier Override Prompts**

```bash
# Force Tier 1 (Simple Implementation)
"Override to Tier 1 Simple Implementation:
STEPS: Implement → Review (2 steps)
USE WHEN: ≤3 files, single service, straightforward changes
AGENTS: code-implementer → code-reviewer
DURATION: <30 minutes
JUSTIFICATION: [explain why simple approach is sufficient]"

# Force Tier 2 (Standard Implementation)
"Override to Tier 2 Standard Implementation:
STEPS: Analyze → Implement → Review → Test (4 steps)
USE WHEN: 4-10 files, moderate complexity, standard timeline
AGENTS: solution-architect → code-implementer → code-reviewer → test-specialist
DURATION: 30-120 minutes
JUSTIFICATION: [explain why standard approach is needed]"

# Force Tier 3 (Complex Implementation)
"Override to Tier 3 Complex Implementation:
STEPS: Full 10-step workflow with comprehensive validation
USE WHEN: >10 files, high complexity, mission-critical changes
AGENTS: All specialized agents with full review cycles
DURATION: >120 minutes
JUSTIFICATION: [explain why complex approach is required]"
```

## 🎯 When to Use Each Implementation Tier

**Tier 1 (Simple Implementation)**: Use when you need to:
- Modify ≤3 files in single service
- Make straightforward bug fixes or minor enhancements
- Implement features with no cross-service dependencies
- Work under urgent timeline with low risk tolerance

**Tier 2 (Standard Implementation)**: Use when you need to:
- Implement features affecting 4-10 files across 2-3 services
- Execute systematic improvements with moderate complexity
- Ensure quality validation through standard review cycles
- Manage some parallel implementation tasks safely

**Tier 3 (Complex Implementation)**: Use when you need to:
- Implement complex features affecting >10 files or >3 services
- Execute major architectural changes or system-wide improvements
- Ensure comprehensive quality validation through multiple review cycles
- Manage complex parallel implementation tasks with full coordination
- Validate implementations with comprehensive testing and documentation

## 📋 10-Step Enhanced Implementation Workflow

### **Step 0: Project Artifact Detection** (Automatic)
```bash
# Automatically check for existing project artifacts
1. Check for .project/plan.md - implementation strategy and phases
2. Check for .project/tasks.md - dependency-ordered task breakdown
3. If found: consume and integrate into workflow
4. If not found: generate during Step 1
```

### **Step 1: Architecture Analysis (solution-architect agent)**
```bash
# Use solution-architect agent to analyze requirements and create implementation plan
# Integrates existing .project/plan.md if available
Task: solution-architect
Prompt: "Analyze the user request and current codebase to create comprehensive implementation plan. Check for existing .project/plan.md and .project/tasks.md first. Assess: 1) What needs to be implemented, 2) Current system capabilities, 3) Implementation feasibility, 4) Parallel vs sequential task identification, 5) Risk assessment, 6) Resource requirements, 7) Success criteria"
```

**Expected Output:**
- Detailed implementation phases with specific tasks
- Integration with existing .project/plan.md if present
- Parallel vs sequential execution strategy
- Risk assessment and mitigation strategies
- Resource allocation recommendations
- Clear success criteria and validation requirements

### **Step 2: Plan Review (code-reviewer agent)**
```bash
# Use code-reviewer agent to validate and improve the implementation plan
Task: code-reviewer
Prompt: "Review the implementation plan for quality, feasibility, and risks. Analyze: 1) Plan completeness and accuracy, 2) Risk assessment validation, 3) Parallel execution safety, 4) Missing considerations, 5) Quality standards alignment, 6) Recommendation improvements"
```

**Expected Output:**
- Plan quality assessment (rating out of 10)
- Identified risks and mitigation strategies
- Recommendations for plan improvements
- Approval to proceed or request for plan revision
- Specific feedback on parallel execution safety

### **Step 3: Implementation Execution (code-implementer agents)**
```bash
# Launch parallel code-implementer agents for independent tasks
Task: code-implementer (Agent 1)
Prompt: "Implement [Phase 1 tasks] - specific requirements and success criteria..."

Task: code-implementer (Agent 2)
Prompt: "Implement [Phase 2 tasks] - specific requirements and success criteria..."

Task: code-implementer (Agent 3)
Prompt: "Implement [Phase 3 tasks] - specific requirements and success criteria..."
```

**Key Principles:**
- **Run agents in parallel** only for independent tasks (different files/components)
- **Use sequential execution** for dependent tasks
- **Provide specific requirements** and success criteria for each agent
- **Implement in phases** based on priority and dependencies

### **Step 4: Implementation Review (code-reviewer agent)**
```bash
# Use code-reviewer agent to assess implementation quality
Task: code-reviewer
Prompt: "Review the implemented code for quality, security, and adherence to requirements. Analyze: 1) Code quality and best practices, 2) Security vulnerabilities, 3) Performance considerations, 4) Error handling, 5) Type safety, 6) Requirements compliance, 7) Critical issues identification"
```

**Expected Output:**
- Implementation quality grade (A-F scale)
- Critical, high, medium, and low priority issues
- Security vulnerability assessment
- Performance impact analysis
- Specific recommendations for improvements

### **Step 5: Security Assessment (security-auditor agent)**
```bash
# Use security-auditor agent for comprehensive security validation
Task: security-auditor
Prompt: "Conduct comprehensive security assessment of implemented code:

SECURITY ANALYSIS SCOPE:
1. Static Code Analysis:
   - SQL injection vulnerabilities
   - Cross-site scripting (XSS)
   - Authentication/authorization flaws
   - Input validation gaps
   - Cryptographic implementations

2. Dependency Security:
   - Vulnerable third-party libraries
   - Outdated package versions
   - License compliance issues
   - Supply chain security risks

3. Infrastructure Security:
   - Configuration security
   - Access control validation
   - Network security patterns
   - Secret management review

4. Compliance Assessment:
   - OWASP Top 10 compliance
   - Industry standard adherence
   - Regulatory requirement validation

OUTPUT: Comprehensive security report with vulnerability prioritization and remediation recommendations"
```

**Expected Output:**
- Security vulnerability assessment with CVSS scores
- Critical security issues requiring immediate attention
- Compliance gap analysis and recommendations
- Security best practices implementation guidance
- Risk assessment and mitigation strategies

### **Step 6: Performance Optimization (performance-optimizer agent)**
```bash
# Use performance-optimizer agent for performance analysis and optimization
Task: performance-optimizer
Prompt: "Analyze and optimize implementation performance:

PERFORMANCE ANALYSIS SCOPE:
1. Code Performance:
   - Algorithm efficiency analysis
   - Memory usage optimization
   - CPU utilization patterns
   - I/O operation efficiency

2. Database Performance:
   - Query optimization analysis
   - Index strategy validation
   - Connection pooling efficiency
   - Transaction performance

3. Caching Strategy:
   - Multi-level caching implementation
   - Cache hit ratio optimization
   - Cache invalidation strategies
   - Performance impact measurement

4. Load Testing:
   - Concurrent user simulation
   - Stress testing scenarios
   - Performance baseline establishment
   - Scalability bottleneck identification

OUTPUT: Performance optimization report with specific improvement recommendations and implementation guidance"
```

**Expected Output:**
- Performance bottleneck identification and analysis
- Optimization recommendations with expected impact
- Load testing results and scalability assessment
- Caching strategy implementation guidance
- Performance monitoring setup recommendations

### **Step 7: Critical Issues Resolution (code-implementer agents)**
```bash
# Fix critical and high priority issues identified in security and performance reviews
Task: code-implementer
Prompt: "Fix the critical and high priority issues identified in security and performance assessments: [specific issues list].

SECURITY FIXES:
1. Resolve critical security vulnerabilities (SQL injection, XSS, auth flaws)
2. Address dependency security issues and updates
3. Implement proper input validation and sanitization
4. Fix cryptographic and secret management issues

PERFORMANCE FIXES:
1. Optimize identified performance bottlenecks
2. Implement recommended caching strategies
3. Optimize database queries and indexing
4. Address memory and CPU optimization opportunities

QUALITY FIXES:
5. Improve error handling and type safety
6. Follow established best practices and patterns"
```

**Key Principles:**
- **Always fix critical security issues** before proceeding
- **Address performance bottlenecks** that impact user experience
- **Implement security and performance fixes in parallel** when possible
- **Document all changes** and their security/performance impact
- **Validate fixes don't introduce new issues**

### **Step 8: Test Creation (test-specialist agent)**
```bash
# Use test-specialist agent to create comprehensive tests including security and performance validation
Task: test-specialist
Prompt: "Create comprehensive test suite for the implemented features including security and performance validation:

TEST COVERAGE REQUIREMENTS:
1. Unit Tests:
   - Core functionality validation
   - Business logic verification
   - Error handling scenarios
   - Edge case coverage

2. Integration Tests:
   - Component interaction validation
   - API endpoint testing
   - Database integration verification
   - Service communication testing

3. Security Tests:
   - Authentication/authorization testing
   - Input validation verification
   - SQL injection prevention testing
   - XSS protection validation
   - Security configuration verification

4. Performance Tests:
   - Load testing scenarios
   - Response time validation
   - Memory usage verification
   - Database query performance
   - Caching effectiveness testing

5. End-to-End Tests:
   - Critical user journey validation
   - Cross-service workflow testing
   - Deployment pipeline validation

OUTPUT: Comprehensive test suite with security and performance validation coverage"
```

**Expected Output:**
- Comprehensive test files covering all implemented features
- Security-focused tests validating implemented protections
- Performance validation tests with baseline comparisons
- Integration tests covering cross-service communication
- End-to-end tests validating complete user workflows
- Test documentation and execution instructions

### **Step 9: Test Review & Improvement (code-reviewer → test-specialist cycle)**
```bash
# Use code-reviewer agent to review test implementation quality
Task: code-reviewer
Prompt: "Review the test implementation for quality, coverage, and effectiveness. Analyze: 1) Test code quality and best practices, 2) Coverage completeness, 3) Edge case handling, 4) Test reliability and maintainability, 5) Security test effectiveness, 6) Performance test validity, 7) Missing test scenarios"
```

**If issues or improvements are identified:**
```bash
# Use test-specialist agent to address review feedback
Task: test-specialist
Prompt: "Address the issues and improvements identified in the test review: [specific feedback]. Improve: 1) Test coverage gaps, 2) Test code quality, 3) Edge case handling, 4) Test reliability, 5) Missing scenarios, 6) Performance test accuracy"
```

**Key Principles:**
- **Always review test quality** before validation
- **Address test review feedback** immediately
- **Ensure comprehensive coverage** of critical paths
- **Validate test reliability** and maintainability

### **Step 10: Final Validation (test-runner agent)**
```bash
# Execute complete test suite to validate implementation
Task: test-runner
Prompt: "Execute comprehensive test validation of all implementations. Provide: 1) Full test suite execution results, 2) Category breakdown (unit/integration/security/performance), 3) Implementation-specific validation, 4) Pass rate statistics, 5) Remaining issues identification, 6) Success criteria verification"
```

**Expected Output:**
- Complete test execution results with statistics
- Validation that implemented features work correctly
- Identification of any remaining issues
- Confirmation of success criteria achievement

## 🔄 Phase-Based Execution Pattern

### **Phase 1: Critical Fixes (Highest Priority)**
- Security vulnerabilities
- System-breaking issues
- Data integrity problems
- Performance bottlenecks

### **Phase 2: Feature Implementation (High Priority)**
- Core functionality additions
- API enhancements
- User-facing features
- Integration improvements

### **Phase 3: Optimizations (Medium Priority)**
- Performance improvements
- Code refactoring
- Memory optimizations
- Scalability enhancements

### **Phase 4: Polish & Documentation (Low Priority)**
- Code cleanup
- Documentation updates
- Test coverage improvements
- Developer experience enhancements

## ⚡ Key Success Factors

### **✅ DO:**
- **Use systematic approach** with all 10 steps
- **Run parallel agents** only for independent tasks
- **Always review implementations** before proceeding
- **Always review tests** before final validation (Step 9)
- **Fix critical issues immediately** when identified
- **Address test review feedback** before validation
- **Create comprehensive tests** for new implementations
- **Validate with test execution** before completion
- **Document all phases** and decisions made

### **❌ DON'T:**
- **Never skip the review steps** (Steps 2, 4, 9)
- **Never run parallel agents** on dependent tasks
- **Don't proceed with critical issues** unfixed
- **Don't skip test review** (Step 9) before validation
- **Don't ignore test quality feedback** from code-reviewer
- **Don't assume implementation works** without validation
- **Don't use generic requirements** - be specific

## 📊 Expected Results

**Typical Success Pattern:**
- **Phase 1**: Critical issues resolved (security, stability)
- **Phase 2**: Core features implemented and working
- **Phase 3**: Performance optimizations validated
- **Phase 4**: High test coverage and documentation

**Quality Metrics:**
- **Implementation Grade**: B+ or higher from code-reviewer
- **Test Quality Grade**: A- or higher from test review
- **Test Coverage**: 90%+ for critical components
- **Validation Rate**: 85%+ test pass rate
- **Security Score**: No critical vulnerabilities

## 🎯 Success Metrics

**Measure effectiveness by:**
- **Implementation Quality**: B+ or higher grade from reviews
- **Test Quality**: A- or higher grade from test review
- **Feature Validation**: All implemented features working correctly
- **Test Coverage**: Comprehensive test suite created and passing
- **Security Posture**: No critical vulnerabilities remaining
- **Performance Impact**: Optimizations validated through testing
- **Code Quality**: Adherence to best practices and patterns

## 🏆 Proven Track Record

**Real Results Achieved:**
- **Implementation Grade**: B+ → A- through iterative improvement
- **Test Quality Grade**: A- through systematic test review
- **Test Validation**: 93.9% pass rate (519/553 tests)
- **Security Implementation**: Complete AI security infrastructure
- **Performance Gains**: Parallel execution and read replica systems
- **Agent Coordination**: 15+ specialized agent executions with 100% success rate

**This workflow is battle-tested and proven effective for complex feature implementation at scale.**

## 📋 Implementation Workflow Completion & Git Integration

### **✅ Implementation Completion Prompts**

```bash
# Implementation Workflow Completion Prompt
"🎯 Implementation Workflow Complete!
- Implementation Grade: [A-F rating]
- Test Validation: [X]% pass rate ([Y]/[Z] tests)
- Files Modified: [X] files across [Y] services
- Security Issues: [resolved count]
- Performance Impact: [improvement metrics]

Next steps:
• /commit-workflow - Create clean atomic commits with documentation updates
• /status-report - Review all implementation changes before deciding
• /continue - Proceed with next development task

Choose your next action:"
```

### **📊 Implementation Status Integration**

```bash
# Enhanced Status for Implementation Changes
"/status-report command for implementation:

📋 IMPLEMENTATION CHANGES SUMMARY:
- Core features: [list implemented features]
- Bug fixes: [list critical fixes resolved]
- Performance optimizations: [list improvements]
- Security enhancements: [list security measures]
- Test coverage: [before → after percentages]

TECHNICAL IMPACT:
- Services modified: [list]
- Dependencies updated: [list]
- API changes: [breaking/non-breaking]
- Database changes: [migrations needed]

GIT STATUS:
- Staged files: [number]
- Unstaged files: [number]
- Untracked files: [number]
- Current branch: [name]

READY FOR NEXT ACTION:
• /commit-workflow - Create organized commits grouped by feature/fix type
• /continue - Start next implementation task (preserve current changes)
• /status-report - Refresh implementation status

What would you like to do next?"
```

### **🔄 Implementation-Specific Commit Strategy**

```bash
# Commit Workflow for Implementation Changes
"/commit-workflow for implementation:

🔍 ANALYZING IMPLEMENTATION CHANGES...
- Feature implementations: [X] files
- Security fixes: [X] files
- Performance optimizations: [X] files
- Test additions: [X] files
- Documentation updates: [X] files

PROPOSED IMPLEMENTATION COMMITS:
1. feat: [feature description] ([X] files + docs)
2. fix: [security/bug fixes] ([X] files)
3. perf: [performance improvements] ([X] files)
4. test: [test coverage additions] ([X] files)
5. docs: [documentation updates] ([X] files)

COMMIT STRATEGY:
- Conventional commits (feat/fix/perf/test/docs)
- Logical grouping by implementation type
- Clean messages without Claude branding
- Documentation sync before commits
- Atomic commits for independent rollback

OPTIONS:
• Proceed with implementation commits [Y/n]
• Customize commit organization [c]
• Review implementation details [r]
• Cancel and return to status [ESC]"
```