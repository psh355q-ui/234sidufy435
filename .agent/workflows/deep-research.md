---
description: 5개 검색 API를 병렬로 실행하여 종합적인 리서치 수행
---

# Deep Research

사용자가 리서치를 요청하면 5개 API를 병렬로 실행하여 종합적인 결과를 제공합니다.

## 트리거 키워드

- 명령어: `/deep-research`
- 키워드: "리서치해줘", "조사해줘", "찾아봐", "검색해줘", "deep dive"

## 필수 환경 변수

다음 API 키가 환경 변수 또는 `.env` 파일에 설정되어 있어야 합니다:

```
BRAVE_API_KEY=your_key
TAVILY_API_KEY=your_key
PERPLEXITY_API_KEY=your_key
NAVER_CLIENT_ID=your_id
NAVER_CLIENT_SECRET=your_secret
YOUTUBE_API_KEY=your_key
```

## 실행 단계

### STEP 0: 환경 변수 로드

```powershell
# .env 파일이 있으면 로드
if (Test-Path .env) {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
    Write-Host "✅ .env 파일에서 환경 변수 로드 완료"
}

# API 키 확인
if (-not $env:BRAVE_API_KEY) {
    Write-Host "❌ API 키가 설정되지 않았습니다."
    Write-Host "   .env 파일 또는 시스템 환경 변수에 API 키를 설정하세요."
    exit 1
}

Write-Host "✅ API 키 로드 완료"
```

### STEP 1: 검색 쿼리 입력

사용자에게 검색어를 질문:

```
검색할 내용을 입력해주세요:
- 영문 검색어: (Brave, Tavily, Perplexity, YouTube용)
- 한국어 검색어: (Naver용, 선택사항)
```

### STEP 2: 병렬 검색 실행

5개 API를 동시에 실행:

```powershell
$query = "사용자 입력 검색어"
$koreanQuery = "한국어 검색어" # 없으면 $query 사용

# 임시 디렉토리 생성
$tempDir = Join-Path $env:TEMP "deep-research"
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

Write-Host "🔍 5개 API로 검색 시작..."

# Brave (20개 결과)
$braveJob = Start-Job -ScriptBlock {
    param($query, $apiKey, $output)
    $uri = "https://api.search.brave.com/res/v1/web/search?q=$query&count=20"
    $headers = @{ "X-Subscription-Token" = $apiKey }
    Invoke-RestMethod -Uri $uri -Headers $headers | ConvertTo-Json -Depth 10 | Out-File $output
} -ArgumentList $query, $env:BRAVE_API_KEY, "$tempDir\brave.json"

# Tavily (20개 + AI 요약)
$tavilyJob = Start-Job -ScriptBlock {
    param($query, $apiKey, $output)
    $uri = "https://api.tavily.com/search"
    $headers = @{ 
        "Authorization" = "Bearer $apiKey"
        "Content-Type" = "application/json"
    }
    $body = @{
        query = $query
        search_depth = "advanced"
        max_results = 20
        include_answer = "advanced"
    } | ConvertTo-Json
    Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $body | ConvertTo-Json -Depth 10 | Out-File $output
} -ArgumentList $query, $env:TAVILY_API_KEY, "$tempDir\tavily.json"

# Perplexity (추론 + 인용)
$perplexityJob = Start-Job -ScriptBlock {
    param($query, $apiKey, $output)
    $uri = "https://api.perplexity.ai/chat/completions"
    $headers = @{
        "Authorization" = "Bearer $apiKey"
        "Content-Type" = "application/json"
    }
    $body = @{
        model = "sonar-reasoning-pro"
        messages = @(
            @{
                role = "user"
                content = $query
            }
        )
        return_citations = $true
    } | ConvertTo-Json
    Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $body | ConvertTo-Json -Depth 10 | Out-File $output
} -ArgumentList $query, $env:PERPLEXITY_API_KEY, "$tempDir\perplexity.json"

# Naver (한국어 10개)
$naverJob = Start-Job -ScriptBlock {
    param($query, $clientId, $clientSecret, $output)
    $uri = "https://openapi.naver.com/v1/search/webkr.json?query=$query&display=10"
    $headers = @{
        "X-Naver-Client-Id" = $clientId
        "X-Naver-Client-Secret" = $clientSecret
    }
    Invoke-RestMethod -Uri $uri -Headers $headers | ConvertTo-Json -Depth 10 | Out-File $output
} -ArgumentList $koreanQuery, $env:NAVER_CLIENT_ID, $env:NAVER_CLIENT_SECRET, "$tempDir\naver.json"

# YouTube (10개 비디오)
$youtubeJob = Start-Job -ScriptBlock {
    param($query, $apiKey, $output)
    $uri = "https://www.googleapis.com/youtube/v3/search?part=snippet&q=$query&type=video&maxResults=10&key=$apiKey"
    Invoke-RestMethod -Uri $uri | ConvertTo-Json -Depth 10 | Out-File $output
} -ArgumentList $query, $env:YOUTUBE_API_KEY, "$tempDir\youtube.json"

# 모든 작업 완료 대기
Write-Host "⏳ 검색 중..."
Wait-Job $braveJob, $tavilyJob, $perplexityJob, $naverJob, $youtubeJob | Out-Null

Write-Host "✅ 모든 검색 완료"
```

### STEP 3: 결과 확인

```powershell
Write-Host "`n=== API 검색 결과 ===" -ForegroundColor Cyan

# Brave
if (Test-Path "$tempDir\brave.json") {
    $brave = Get-Content "$tempDir\brave.json" | ConvertFrom-Json
    $braveCount = $brave.web.results.Count
    if ($braveCount -gt 0) {
        Write-Host "✅ Brave: $braveCount 개 결과" -ForegroundColor Green
    } else {
        Write-Host "❌ Brave: 실패" -ForegroundColor Red
    }
}

# Tavily
if (Test-Path "$tempDir\tavily.json") {
    $tavily = Get-Content "$tempDir\tavily.json" | ConvertFrom-Json
    $tavilyCount = $tavily.results.Count
    if ($tavilyCount -gt 0) {
        Write-Host "✅ Tavily: $tavilyCount 개 결과" -ForegroundColor Green
    } else {
        Write-Host "❌ Tavily: 실패" -ForegroundColor Red
    }
}

# Perplexity
if (Test-Path "$tempDir\perplexity.json") {
    $perplexity = Get-Content "$tempDir\perplexity.json" | ConvertFrom-Json
    $pplxLen = $perplexity.choices[0].message.content.Length
    if ($pplxLen -gt 0) {
        Write-Host "✅ Perplexity: $pplxLen 자" -ForegroundColor Green
    } else {
        Write-Host "❌ Perplexity: 실패" -ForegroundColor Red
    }
}

# Naver
if (Test-Path "$tempDir\naver.json") {
    $naver = Get-Content "$tempDir\naver.json" | ConvertFrom-Json
    $naverCount = $naver.items.Count
    if ($naverCount -gt 0) {
        Write-Host "✅ Naver: $naverCount 개 결과" -ForegroundColor Green
    } else {
        Write-Host "❌ Naver: 실패" -ForegroundColor Red
    }
}

# YouTube
if (Test-Path "$tempDir\youtube.json") {
    $youtube = Get-Content "$tempDir\youtube.json" | ConvertFrom-Json
    $ytCount = $youtube.items.Count
    if ($ytCount -gt 0) {
        Write-Host "✅ YouTube: $ytCount 개 결과" -ForegroundColor Green
    } else {
        Write-Host "❌ YouTube: 실패" -ForegroundColor Red
    }
}
```

### STEP 4: 결과 통합 (Python 스크립트)

```powershell
# Python 스크립트 실행
$scriptPath = ".agent\scripts\deep-research\merge_results.py"

if (Test-Path $scriptPath) {
    python $scriptPath `
        --brave "$tempDir\brave.json" `
        --tavily "$tempDir\tavily.json" `
        --perplexity "$tempDir\perplexity.json" `
        --naver "$tempDir\naver.json" `
        --youtube "$tempDir\youtube.json" `
        --output "$tempDir\merged_research.json"
    
    Write-Host "`n✅ 결과 통합 완료: $tempDir\merged_research.json"
} else {
    Write-Host "⚠️  merge_results.py를 찾을 수 없습니다. 수동으로 결과를 확인하세요."
}
```

### STEP 5: 사용자에게 보고

통합된 결과를 바탕으로 다음을 보고합니다:

1. **핵심 발견사항** (3-5개 요약)
2. **출처별 정보**
   - 웹 검색 결과 (Brave, Tavily)
   - AI 분석 (Perplexity)
   - 한국어 자료 (Naver)
   - 영상 자료 (YouTube)
3. **참고 링크**

---

## API별 역할

| API | 역할 | 강점 |
|-----|------|------|
| **Brave** | 웹 검색 | 프라이버시, 다양한 결과 |
| **Tavily** | 웹 검색 + AI 요약 | 즉시 사용 가능한 요약 |
| **Perplexity** | 추론 + 인용 | 깊이 있는 분석 |
| **Naver** | 한국어 검색 | 한국 콘텐츠 |
| **YouTube** | 영상 검색 | 튜토리얼, 강의 |

---

## 에러 처리

| 에러 | 해결책 |
|------|--------|
| API 키 미로드 | .env 파일 또는 시스템 환경 변수 설정 확인 |
| Rate limit | 3초 대기 후 재시도 |
| 타임아웃 | 결과 수 줄이고 재시도 |
| Naver 인증 오류 | developers.naver.com에서 키 재발급 |

---

## 결과 저장

리서치 결과는 다음 위치에 저장됩니다:

```
%TEMP%\deep-research\
├── brave.json
├── tavily.json
├── perplexity.json
├── naver.json
├── youtube.json
└── merged_research.json  # 통합 결과
```
