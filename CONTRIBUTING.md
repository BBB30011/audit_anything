# Contributing to Audit Anything (DocAuditor)

Thank you for your interest in contributing to **Audit Anything (`docauditor`)**! This project aims to deliver the gold standard in forensic enterprise document auditing by combining multi-pillar governance frameworks with the reverse-engineering methodology of [morluto/rea](https://github.com/morluto/rea).

---

## 1. Development Principles

All contributions must adhere to our four foundational guarantees:

1. **Deterministic & Offline-First**: Core analyzers must operate without mandatory cloud LLM APIs or internet connectivity.
2. **Zero Hallucination Anchoring**: Every finding generated must have a valid verbatim `quote_anchor` from the source document.
3. **Forensic Integrity**: Document text must always be treated as untrusted content (`_meta.provenance.untrusted_content = True`) to protect against prompt-injection.
4. **100% Test Coverage for Core Rules**: Every new analyzer rule or obligation must be accompanied by comprehensive `pytest` test cases.

---

## 2. Environment Setup

### Prerequisites
- Python 3.10+ (tested up to Python 3.13)
- `git`

### Installation
Clone the repository and install dependencies in editable mode:

```bash
git clone https://github.com/BBB30011/audit_anything.git
cd audit_anything

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

### Running Tests
Run the automated test suite before making any commits:

```bash
pytest tests/ -v
```

---

## 3. Adding a New Audit Analyzer / Rule

To add a new audit rule (e.g., ESG compliance, AML/CFT checks, or specific tax laws):

1. **Locate or Create the Analyzer**:
   - For general enterprise rules, update `skill_audit/analyzers/enterprise_analyzer.py`.
   - For specialized domain rules, create a new analyzer in `skill_audit/analyzers/my_analyzer.py` inheriting from `BaseAnalyzer`.

2. **Implement 5C Finding Generation**:
   Ensure all findings conform to the 5C model:
   - **Condition**: Exact situation observed with verbatim text quote (`quote_anchor`).
   - **Criteria**: Benchmark, policy, or statutory regulation violated.
   - **Cause**: Root cause explanation (why did the gap occur?).
   - **Consequence**: Financial, operational, or legal risk exposure.
   - **Corrective Action**: Actionable, pragmatic recommendation for management.

3. **Register the Analyzer**:
   Export the analyzer in `skill_audit/analyzers/__init__.py` and wire it into `skill_audit/engine.py`.

4. **Write Unit Tests**:
   Add test cases in `tests/test_analyzers.py` or `tests/test_enterprise_pillars.py` checking both compliant and non-compliant inputs.

---

## 4. Adding a Reconstruction Obligation

If a new statutory requirement must be tracked as a mandatory audit checkpoint:

1. Open `skill_audit/analyzers/obligation_engine.py`.
2. Add the obligation definition into `MANDATORY_OBLIGATIONS`:
   ```python
   AuditObligation(
       obligation_id="OBL-NEW-001",
       category="Environmental, Social & Governance (ESG)",
       description="Carbon emission disclosure statement for FY reporting.",
       statutory_reference="POJK No. 51/POJK.03/2017",
       mandatory=True,
   )
   ```
3. Add the deterministic evaluation logic in `evaluate_obligations()`.
4. Add corresponding test assertions in `tests/test_rea_collaboration.py`.

---

## 5. Coding Standards

- Follow PEP 8 style guidelines.
- Use explicit type annotations on all function signatures.
- Document classes and complex functions with clear docstrings explaining audit intent.
- Ensure all file paths and user inputs are handled safely with `pathlib.Path`.

---

## 6. Pull Request Workflow

1. Fork the repository and create your branch from `main`:
   ```bash
   git checkout -b feature/my-new-audit-rule
   ```
2. Commit your changes with clear, descriptive commit messages:
   ```bash
   git commit -m "feat(analyzers): add statutory e-Faktur QR code verification rule"
   ```
3. Ensure all tests pass:
   ```bash
   pytest tests/
   ```
4. Push your branch and open a Pull Request against `main`.
5. Provide a summary of the audit standard, test fixtures used, and edge cases considered in the PR description.

---

## 7. License

By contributing to **Audit Anything**, you agree that your contributions will be licensed under the MIT License.
