---
trigger: always_on
---

Workspace Rule: Architecture & Coding Principles (Complete Version)
Activation Mode: Always On / Model Decision: "Whenever planning architecture, generating code structure, or reviewing code."

1. Core Development Principles (Chinese Output Required)
When building project frameworks or writing code, strictly adhere to these standards:

High Cohesion & Low Coupling (高内聚，低耦合): Ensure each module has a single, well-defined purpose. Minimize cross-module dependencies to enhance maintainability.

Modularity & Separability (模块化，可拆分性): Design the system as interchangeable modules. Structure should allow easy extraction or replacement of components.

SOLID Principles (SOLID 原则详解):

单一职责原则 (Single Responsibility): 一个类或模块应只有一个引起它变化的原因。

开闭原则 (Open/Closed): 软件实体应对扩展开放，对修改关闭。

里氏替换原则 (Liskov Substitution): 子类必须能够替换其基类。

接口隔离原则 (Interface Segregation): 不应强迫客户端依赖它们不使用的方法。

依赖倒置原则 (Dependency Inversion): 要依赖抽象，不要依赖具体实现。

Layered Architecture (分层架构原则): Strictly separate concerns using a clear hierarchical structure.

2. Recommended Project Structure (Example)
Unless the user specifies otherwise, initialize or refactor the project following this template:

src/
├── presentation/   # 表现层：Controller, UI 逻辑, API 路由
├── application/    # 应用层：Service 逻辑, UseCase 编排
├── domain/         # 领域层：实体 (Entity), 聚合根, Repository 接口定义
└── infrastructure/ # 基础设施层：数据库 DAO, 外部 API 实现, 缓存配置

3. Mandatory Execution & Conflict Handling
Zero Tolerance: Any generated architecture, code, or plan that violates the above principles MUST be explicitly pointed out in the Walkthrough, along with a correction plan.

Priority: This rule overrides any conflicting general instructions (except for mandatory language rules).

Explanation: Use Chinese to explain how the code satisfies these principles during the Implementation Plan phase.

4. Language Consistency (Locked to Chinese)
Output Requirement: Despite this rule being in English, all user-facing content including Dialogue, Implementation Plan, Walkthrough, Tasks, README.md, and Code Comments must be in Chinese.

Reflective Reasoning: When analyzing the architecture, use professional Chinese technical terminology.