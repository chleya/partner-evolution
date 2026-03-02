# Partner-Evolution API 文档

## 概述

Partner-Evolution 是一个具备自我进化能力的AI伙伴系统。

## 基础API

### 状态

```
GET /api/status
```

返回系统状态、信念数、opposition数等。

### 信念

```
GET /api/beliefs
POST /api/beliefs
```

### 目标

```
GET /api/goals
POST /api/goals/generate
```

## v3.0 API

### 身份管理

```
GET /api/v3/ontology/identity
POST /api/v3/ontology/identity/evolve
```

### 基因组

```
GET /api/v3/ontology/genome
POST /api/v3/ontology/genome/mutate
```

### 递归优化

```
GET /api/v3/refiner/analysis
POST /api/v3/refiner/apply
POST /api/v3/refiner/rollback
```

## 观测API

### 检索质量

```
GET /api/observability/retrieval-quality
```

### 健康状态

```
GET /api/observability/health
```

## 配置

### 获取配置

```
GET /api/config
```

### 更新配置

```
POST /api/config
Body: {"key": "value"}
```

---

详细文档见: docs/
