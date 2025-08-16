---
description: Validate deployment configurations using deployment-specialist agent
model: sonnet
---

Use the deployment-specialist agent to validate Kubernetes manifests, GitHub Actions, and deployment configurations.

The deployment-specialist will:
- Validate K8s manifests syntax and security settings
- Check GitHub Actions workflow configurations
- Verify security contexts and resource limits
- Analyze deployment best practices compliance
- Test kustomize/helm chart generation

Perfect for:
- Pre-deployment validation
- Security configuration review
- Resource limit verification
- CI/CD pipeline validation
- Infrastructure as code testing

Example usage:
```
/deploy-check
```

This ensures your deployment configurations are secure, valid, and follow best practices before going to production.