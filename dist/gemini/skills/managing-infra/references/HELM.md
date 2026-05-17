# Helm Patterns

When to reach for Helm: complex apps with many environments, third-party charts, or heavy templating. For simple env variation prefer Kustomize (see KUBERNETES.md).

## Chart Structure

```
mychart/
├── Chart.yaml
├── values.yaml
├── values-prod.yaml
├── .helmignore
├── templates/
│   ├── _helpers.tpl
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── ingress.yaml
│   └── NOTES.txt
└── charts/
```

## Chart.yaml

```yaml
apiVersion: v2
name: mychart
description: Application chart
type: application
version: 0.1.0          # chart version (SemVer)
appVersion: "1.2.3"     # app version, quoted

dependencies:
  - name: postgresql
    version: "15.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
```

## values.yaml

```yaml
replicaCount: 2

image:
  repository: gcr.io/myproject/api
  tag: ""              # default to .Chart.AppVersion in template
  pullPolicy: IfNotPresent

resources:
  limits:
    cpu: 1000m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]

postgresql:
  enabled: false
```

## _helpers.tpl

```
{{- define "mychart.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "mychart.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}
```

## templates/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "mychart.fullname" . }}
  labels:
    {{- include "mychart.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ .Chart.Name }}
      app.kubernetes.io/instance: {{ .Release.Name }}
  template:
    metadata:
      labels:
        {{- include "mychart.labels" . | nindent 8 }}
    spec:
      securityContext:
        {{- toYaml .Values.securityContext | nindent 8 }}
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

## Best Practices

- Quote `appVersion`; bump chart `version` on every change (SemVer).
- Default image tag to `.Chart.AppVersion`, not `latest`.
- Centralize names/labels in `_helpers.tpl`; never hardcode `.Release.Name`.
- Use `{{- toYaml .Values.x | nindent N }}` for blocks instead of templating each field.
- Gate optional subcharts with `condition:` in `Chart.yaml` and an `enabled` flag in values.
- Per-environment overrides via `values-<env>.yaml` and `-f`, not separate charts.
- Never put secrets in `values.yaml`; reference an external secret manager or `existingSecret`.

## Commands

```bash
helm lint .                                  # Lint chart
helm template . -f values-prod.yaml          # Render locally (no cluster)
helm upgrade --install NAME . -f values-prod.yaml --dry-run --debug   # Diff before apply
helm upgrade --install NAME . -f values-prod.yaml    # Apply (only after dry-run review)
helm history NAME                            # Release history
helm rollback NAME REVISION                  # Roll back

helm dependency update                       # Pull subcharts
```

## Safety

Never run `helm upgrade --install` without `--dry-run --debug` first and showing the diff to the user. For chart upgrades that change immutable fields (selectors, volume claims), surface the destructive change explicitly before proceeding.
