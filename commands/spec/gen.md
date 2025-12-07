# Generate App Specification

Transform the provided markdown document(s) into a structured `app_spec.txt` specification.

## Input Files

$ARGUMENTS

Read the file(s) above and analyze to extract:

1. **Core concept** - What is being built and why
2. **Features** - All mentioned functionality, explicit or implied
3. **Technical hints** - Any mentioned technologies, constraints, or preferences
4. **User workflows** - How users will interact with the system
5. **Data entities** - What needs to be stored and managed

## Output

Generate `app_spec.txt` in the current directory using this XML structure:

```xml
<project_specification>
  <project_name>{Descriptive project name}</project_name>

  <overview>
    {2-4 sentence summary: what it does, purpose, target users, problem solved}
  </overview>

  <technology_stack>
    <frontend>
      <framework>{Framework + build tool}</framework>
      <styling>{CSS approach}</styling>
      <state_management>{State solution}</state_management>
    </frontend>
    <backend>
      <runtime>{Runtime}</runtime>
      <database>{Database}</database>
    </backend>
    <communication>
      {API style, real-time, external integrations}
    </communication>
  </technology_stack>

  <prerequisites>
    <environment_setup>
      {Setup requirements, dependencies, configuration}
    </environment_setup>
  </prerequisites>

  <core_features>
    <category_name>
      - Feature as action item
      - Include explicit AND implied features
    </category_name>
  </core_features>

  <database_schema>
    <tables>
      <entity_name>
        - id, fields, relationships, timestamps
      </entity_name>
    </tables>
  </database_schema>

  <api_endpoints_summary>
    <resource_name>
      - METHOD /api/path
    </resource_name>
  </api_endpoints_summary>

  <ui_layout>
    <main_structure>{Layout description}</main_structure>
    <area_name>
      - Components, interactions, states
    </area_name>
  </ui_layout>

  <design_system>
    <color_palette>{Colors with hex}</color_palette>
    <typography>{Fonts, sizes}</typography>
    <components>{Button, input, card styling}</components>
    <animations>{Transitions}</animations>
  </design_system>

  <key_interactions>
    <flow_name>
      1. Step-by-step user flow
    </flow_name>
  </key_interactions>

  <implementation_steps>
    <step number="N">
      <title>{Phase}</title>
      <tasks>
        - Actionable tasks
      </tasks>
    </step>
  </implementation_steps>

  <success_criteria>
    <functionality>{What must work}</functionality>
    <user_experience>{UX standards}</user_experience>
    <technical_quality>{Code standards}</technical_quality>
    <design_polish>{Visual quality}</design_polish>
  </success_criteria>
</project_specification>

Guidelines

- Expand terse mentions into complete feature sets (e.g., "user accounts" → login, logout, registration, password reset, profile)
- Infer standard features any app of this type needs (validation, error handling, loading states)
- Don't invent features contradicting the source
- Design proper schemas - use JSON columns only for truly dynamic data
- Order implementation from foundation to polish

Write the complete specification to app_spec.txt in the project root.

```
