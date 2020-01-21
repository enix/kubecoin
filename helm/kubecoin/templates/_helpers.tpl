{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "kubecoin.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "kubecoin.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "kubecoin.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "kubecoin.labels" -}}
helm.sh/chart: {{ include "kubecoin.chart" . }}
{{ include "kubecoin.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Selector labels
*/}}
{{- define "kubecoin.selectorLabels" -}}
app.kubernetes.io/name: {{ include "kubecoin.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
Create the name of the service account to use
*/}}
{{- define "kubecoin.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
    {{ default (include "kubecoin.fullname" .) .Values.serviceAccount.name }}
{{- else -}}
    {{ default "default" .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}


{{- define "kubecoin.worker.image" -}}
{{ pluck "repository" .Values.worker.image (dict "repository" (printf "%s/worker" .Values.global.registry)) | first -}}
:{{ pluck "tag" .Values.worker.image .Values.global (dict "tag" .Chart.AppVersion) | first}}
{{- end -}}

{{- define "kubecoin.rng.image" -}}
{{ pluck "repository" .Values.rng.image (dict "repository" (printf "%s/rng" .Values.global.registry)) | first -}}
:{{ pluck "tag" .Values.rng.image .Values.global (dict "tag" .Chart.AppVersion) | first}}
{{- end -}}

{{- define "kubecoin.hasher.image" -}}
{{ pluck "repository" .Values.hasher.image (dict "repository" (printf "%s/hasher" .Values.global.registry)) | first -}}
:{{ pluck "tag" .Values.hasher.image .Values.global (dict "tag" .Chart.AppVersion) | first}}
{{- end -}}

{{- define "kubecoin.webui.image" -}}
{{ pluck "repository" .Values.webui.image (dict "repository" (printf "%s/webui" .Values.global.registry)) | first -}}
:{{ pluck "tag" .Values.webui.image .Values.global (dict "tag" .Chart.AppVersion) | first}}
{{- end -}}

{{- define "kubecoin.redis.service" -}}
{{- $redisValues := (dict "Release" (dict "Name" .Release.Name) "Chart" (dict "Name" "redis") "Values" .Values.redis) -}}
{{- include "redis.fullname" $redisValues }}-master
{{- end -}}
