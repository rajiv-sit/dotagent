param(
    [Parameter(Position = 0, Mandatory = $true)]
    [ValidateSet("setup", "task", "review", "run", "status", "result", "cancel")]
    [string]$Command,

    [Parameter(Position = 1)]
    [string]$Text,

    [string]$Target,
    [string]$Id,
    [switch]$Execute,
    [string]$Model,
    [ValidateSet("read-only", "workspace-write", "danger-full-access")]
    [string]$Sandbox = "workspace-write"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$adapterPath = Join-Path $PSScriptRoot "adapters\agent-cli.ps1"
if (Test-Path -LiteralPath $adapterPath) {
    . $adapterPath
}

$script:ValidStatuses = @("PENDING", "RUNNING", "SUCCESS", "FAILED", "REVIEWED", "CANCELLED")

function Get-ProjectRoot {
    return (Get-Location).Path
}

function Get-StateRoot {
    return Join-Path (Get-ProjectRoot) ".dotagent-state"
}

function Get-JobsRoot {
    return Join-Path (Get-StateRoot) "jobs"
}

function Get-GraphsRoot {
    return Join-Path (Get-StateRoot) "graphs"
}

function Ensure-Dir {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

function Test-Property {
    param(
        [object]$Object,
        [string]$Name
    )

    if ($null -eq $Object) {
        return $false
    }

    if ($Object -is [System.Collections.IDictionary]) {
        return $Object.Contains($Name)
    }

    return $Object.PSObject.Properties.Name -contains $Name
}

function Get-PropertyValue {
    param(
        [object]$Object,
        [string]$Name,
        [object]$Default = $null
    )

    if ($Object -is [System.Collections.IDictionary]) {
        if ($Object.Contains($Name)) {
            return $Object[$Name]
        }
        return $Default
    }

    if (Test-Property -Object $Object -Name $Name) {
        return $Object.$Name
    }

    return $Default
}

function Convert-ToHashtable {
    param([object]$Value)

    if ($null -eq $Value) {
        return @{}
    }

    if ($Value -is [System.Collections.IDictionary]) {
        return $Value
    }

    $table = @{}
    foreach ($property in $Value.PSObject.Properties) {
        $table[$property.Name] = $property.Value
    }
    return $table
}

function Write-JsonFile {
    param(
        [string]$Path,
        [object]$Value
    )

    $parent = Split-Path -Parent $Path
    if ($parent) {
        Ensure-Dir $parent
    }

    $Value | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Read-JsonFile {
    param([string]$Path)

    return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function Get-RepoRoot {
    return Split-Path -Parent $PSScriptRoot
}

function Get-WorkflowTemplateRoot {
    $repoRoot = Get-RepoRoot
    foreach ($candidate in @(
        (Join-Path $repoRoot "workflows"),
        (Join-Path $repoRoot "prompts"),
        (Join-Path $repoRoot "templates\workflows")
    )) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    throw "workflow templates directory not found"
}

function Get-Template {
    param([string]$Name)

    return Get-Content -LiteralPath (Join-Path (Get-WorkflowTemplateRoot) $Name) -Raw
}

function Get-SchemaPath {
    param([string]$Name)

    return Join-Path (Get-RepoRoot) "schemas\$Name"
}

function Render-Template {
    param(
        [string]$Template,
        [hashtable]$Tokens
    )

    $out = $Template
    foreach ($key in $Tokens.Keys) {
        $out = $out.Replace("{{${key}}}", [string]$Tokens[$key])
    }
    return $out
}

function New-JobId {
    param([string]$Prefix)

    return "$Prefix-" + [DateTime]::UtcNow.ToString("yyyyMMddHHmmssfff")
}

function Convert-ToProcessArguments {
    param([string[]]$Arguments)

    $quoted = foreach ($arg in $Arguments) {
        if ($null -eq $arg) {
            '""'
        } else {
            '"' + ($arg -replace '"', '\"') + '"'
        }
    }

    return [string]::Join(' ', $quoted)
}

function Convert-LegacyStatus {
    param([string]$Status)

    $normalizedStatus = if ($null -eq $Status) { "" } else { $Status.ToLowerInvariant() }

    switch ($normalizedStatus) {
        "prepared" { return "PENDING" }
        "running" { return "RUNNING" }
        "completed" { return "SUCCESS" }
        "failed" { return "FAILED" }
        "cancelled" { return "CANCELLED" }
        default {
            if ($script:ValidStatuses -contains $Status) {
                return $Status
            }
            return "PENDING"
        }
    }
}

function Get-DefaultInput {
    return @{
        summary = ""
        prompt_template = $null
        prompt_file = $null
        base_prompt = $null
    }
}

function Get-DefaultOutput {
    return @{
        output_file = $null
        events_file = $null
        stderr_file = $null
        artifacts_index = $null
        exit_code = $null
        started_at = $null
        completed_at = $null
        prompt_preview = $null
    }
}

function Normalize-JobRecord {
    param([object]$Record)

    $input = Get-DefaultInput
    $output = Get-DefaultOutput
    $metadata = @{}

    $legacyInput = Convert-ToHashtable (Get-PropertyValue -Object $Record -Name "input")
    $legacyOutput = Convert-ToHashtable (Get-PropertyValue -Object $Record -Name "output")
    $legacyMetadata = Convert-ToHashtable (Get-PropertyValue -Object $Record -Name "metadata")

    foreach ($key in $legacyInput.Keys) {
        $input[$key] = $legacyInput[$key]
    }
    foreach ($key in $legacyOutput.Keys) {
        $output[$key] = $legacyOutput[$key]
    }
    foreach ($key in $legacyMetadata.Keys) {
        $metadata[$key] = $legacyMetadata[$key]
    }

    if (Test-Property -Object $Record -Name "summary" -and -not $input["summary"]) {
        $input["summary"] = $Record.summary
    }
    if (Test-Property -Object $Record -Name "kind" -and -not $metadata.ContainsKey("kind")) {
        $metadata["kind"] = $Record.kind
    }
    if (Test-Property -Object $Record -Name "prompt_preview" -and -not $output["prompt_preview"]) {
        $output["prompt_preview"] = $Record.prompt_preview
    }
    if (Test-Property -Object $Record -Name "output_file" -and -not $output["output_file"]) {
        $output["output_file"] = $Record.output_file
    }
    if (Test-Property -Object $Record -Name "events_file" -and -not $output["events_file"]) {
        $output["events_file"] = $Record.events_file
    }
    if (Test-Property -Object $Record -Name "stderr_file" -and -not $output["stderr_file"]) {
        $output["stderr_file"] = $Record.stderr_file
    }
    if (Test-Property -Object $Record -Name "exit_code" -and $null -eq $output["exit_code"]) {
        $output["exit_code"] = $Record.exit_code
    }
    if (Test-Property -Object $Record -Name "created_at" -and -not $metadata.ContainsKey("created_at")) {
        $metadata["created_at_legacy"] = $Record.created_at
    }

    $type = Get-PropertyValue -Object $Record -Name "type"
    if (-not $type) {
        $type = Get-PropertyValue -Object $Record -Name "kind" -Default "task"
    }

    $id = Get-PropertyValue -Object $Record -Name "id"
    $createdAt = Get-PropertyValue -Object $Record -Name "created_at" -Default ([DateTime]::UtcNow.ToString("o"))
    $status = Convert-LegacyStatus -Status (Get-PropertyValue -Object $Record -Name "status" -Default "PENDING")

    return [ordered]@{
        id = $id
        type = $type
        status = $status
        created_at = $createdAt
        input = $input
        output = $output
        metadata = $metadata
    }
}

function New-JobRecord {
    param(
        [string]$JobId,
        [string]$Type,
        [string]$Summary,
        [string]$PromptText,
        [string]$TemplateName,
        [hashtable]$Metadata
    )

    $normalizedMetadata = if ($Metadata) { $Metadata } else { @{} }

    return [ordered]@{
        id = $JobId
        type = $Type
        status = "PENDING"
        created_at = [DateTime]::UtcNow.ToString("o")
        input = @{
            summary = $Summary
            prompt_template = $TemplateName
            prompt_file = $null
            base_prompt = $PromptText
        }
        output = Get-DefaultOutput
        metadata = $normalizedMetadata
    }
}

function Get-JobJsonPath {
    param([string]$JobId)

    return Join-Path (Get-JobsRoot) "$JobId.json"
}

function Get-JobPromptPath {
    param([string]$JobId)

    return Join-Path (Get-JobsRoot) "$JobId.prompt.md"
}

function Get-WorkflowPath {
    param([string]$WorkflowId)

    return Join-Path (Get-GraphsRoot) "$WorkflowId.json"
}

function Save-JobRecord {
    param([object]$Record)

    $jobsRoot = Get-JobsRoot
    Ensure-Dir $jobsRoot
    $normalized = Normalize-JobRecord -Record $Record
    Write-JsonFile -Path (Get-JobJsonPath -JobId $normalized.id) -Value $normalized
    return $normalized
}

function Read-JobRecord {
    param([string]$JobId)

    $jsonPath = Get-JobJsonPath -JobId $JobId
    if (-not (Test-Path -LiteralPath $jsonPath)) {
        throw "Job not found: $JobId"
    }

    return Normalize-JobRecord -Record (Read-JsonFile -Path $jsonPath)
}

function Write-JobPrompt {
    param([object]$Record)

    $normalized = Normalize-JobRecord -Record $Record
    $promptPath = Get-JobPromptPath -JobId $normalized.id
    $normalized.input.prompt_file = $promptPath

    $promptText = $normalized.input.base_prompt
    if ($null -eq $promptText) {
        $promptText = ""
    }

    $promptText | Set-Content -LiteralPath $promptPath -Encoding UTF8
    Save-JobRecord -Record $normalized | Out-Null
    return $promptPath
}

function Set-JobStatusOnRecord {
    param(
        [object]$Record,
        [string]$NewStatus
    )

    $normalized = Normalize-JobRecord -Record $Record
    $current = $normalized.status

    if (-not ($script:ValidStatuses -contains $NewStatus)) {
        throw "Invalid status: $NewStatus"
    }

    $allowed = @{
        PENDING = @("RUNNING", "CANCELLED")
        RUNNING = @("SUCCESS", "FAILED", "CANCELLED")
        SUCCESS = @("REVIEWED")
        FAILED = @("REVIEWED")
        REVIEWED = @()
        CANCELLED = @()
    }

    if ($current -ne $NewStatus -and -not ($allowed[$current] -contains $NewStatus)) {
        throw "Invalid status transition: $current -> $NewStatus"
    }

    $normalized.status = $NewStatus
    return $normalized
}

function Save-PreparedJob {
    param([object]$Record)

    $normalized = Save-JobRecord -Record $Record
    $promptPath = Write-JobPrompt -Record $normalized
    return @{
        json = Get-JobJsonPath -JobId $normalized.id
        prompt = $promptPath
    }
}

function Get-AgentCommand {
    if (Get-Command Resolve-AssistantCommand -ErrorAction SilentlyContinue) {
        $resolved = Resolve-AssistantCommand
        if ($resolved) {
            return $resolved
        }
    }

    return $null
}

function New-ArtifactRecord {
    param(
        [string]$Path,
        [string]$Kind
    )

    $exists = Test-Path -LiteralPath $Path
    $record = [ordered]@{
        kind = $Kind
        path = $Path
        exists = $exists
        size = $null
        sha256 = $null
        updated_at = $null
    }

    if ($exists) {
        $item = Get-Item -LiteralPath $Path
        $record["size"] = $item.Length
        $record["updated_at"] = $item.LastWriteTimeUtc.ToString("o")
        $record["sha256"] = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash
    }

    return $record
}

function Write-ArtifactIndex {
    param(
        [object]$Record,
        [string[]]$AdditionalPaths
    )

    $normalized = Normalize-JobRecord -Record $Record
    $artifactsPath = Join-Path (Get-JobsRoot) "$($normalized.id).artifacts.json"
    $paths = @(
        @{ kind = "prompt"; path = $normalized.input.prompt_file }
        @{ kind = "output"; path = $normalized.output.output_file }
        @{ kind = "events"; path = $normalized.output.events_file }
        @{ kind = "stderr"; path = $normalized.output.stderr_file }
    )

    foreach ($additional in ($AdditionalPaths | Where-Object { $_ })) {
        $paths += @{ kind = "extra"; path = $additional }
    }

    $artifactEntries = @(
        foreach ($entry in $paths) {
        if ($entry.path) {
            New-ArtifactRecord -Path $entry.path -Kind $entry.kind
        }
        }
    )

    $bundle = [ordered]@{
        job_id = $normalized.id
        type = $normalized.type
        status = $normalized.status
        created_at = [DateTime]::UtcNow.ToString("o")
        summary = $normalized.input.summary
        metadata = @{
            workflow_id = Get-PropertyValue -Object $normalized.metadata -Name "workflow_id"
            stage = Get-PropertyValue -Object $normalized.metadata -Name "stage"
            dependencies = @(Get-PropertyValue -Object $normalized.metadata -Name "dependencies" -Default @())
        }
        artifacts = $artifactEntries
    }

    Write-JsonFile -Path $artifactsPath -Value $bundle
    $normalized.output.artifacts_index = $artifactsPath
    Save-JobRecord -Record $normalized | Out-Null
    return $artifactsPath
}

function Get-DependencyContext {
    param([object]$Record)

    $normalized = Normalize-JobRecord -Record $Record
    $dependencies = @(Get-PropertyValue -Object $normalized.metadata -Name "dependencies" -Default @())
    if ($dependencies.Count -eq 0) {
        return ""
    }

    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("")
    $lines.Add("<dependency_context>")

    foreach ($dependencyId in $dependencies) {
        try {
            $dependency = Read-JobRecord -JobId $dependencyId
            $lines.Add("- id: $($dependency.id)")
            $lines.Add("  status: $($dependency.status)")
            $lines.Add("  summary: $($dependency.input.summary)")
            if ($dependency.output.output_file) {
                $lines.Add("  output_file: $($dependency.output.output_file)")
            }
            if ($dependency.output.artifacts_index) {
                $lines.Add("  artifacts_index: $($dependency.output.artifacts_index)")
            }
        } catch {
            $lines.Add("- id: $dependencyId")
            $lines.Add("  status: MISSING")
        }
    }

    $lines.Add("</dependency_context>")
    return ($lines -join [Environment]::NewLine)
}

function Refresh-JobPromptForExecution {
    param([object]$Record)

    $normalized = Normalize-JobRecord -Record $Record
    $basePrompt = $normalized.input.base_prompt
    if ($null -eq $basePrompt) {
        if ($normalized.input.prompt_file -and (Test-Path -LiteralPath $normalized.input.prompt_file)) {
            $basePrompt = Get-Content -LiteralPath $normalized.input.prompt_file -Raw
        } else {
            $basePrompt = ""
        }
    }

    $promptText = $basePrompt + (Get-DependencyContext -Record $normalized)
    
    # Append correction context if this is a retry
    if ($normalized.correction_context) {
        $promptText += "`n`n## Corrective Context (Previous Attempt Feedback)`n"
        $promptText += $normalized.correction_context
    }

    $promptPath = Get-JobPromptPath -JobId $normalized.id
    $promptText | Set-Content -LiteralPath $promptPath -Encoding UTF8
    $normalized.input.prompt_file = $promptPath
    Save-JobRecord -Record $normalized | Out-Null
    return $promptPath
}

function Invoke-AgentPreparedJob {
    param(
        [string]$JobId,
        [string]$Model,
        [string]$Sandbox
    )

    $agent = Get-AgentCommand
    if (-not $agent) {
        throw "No local assistant CLI was found on PATH."
    }

    $record = Read-JobRecord -JobId $JobId
    $record = Set-JobStatusOnRecord -Record $record -NewStatus "RUNNING"
    $record.output.started_at = [DateTime]::UtcNow.ToString("o")
    Save-JobRecord -Record $record | Out-Null

    $promptPath = Refresh-JobPromptForExecution -Record $record
    $outputPath = Join-Path (Get-JobsRoot) "$JobId.output.md"
    $jsonlPath = Join-Path (Get-JobsRoot) "$JobId.events.jsonl"
    $stderrPath = Join-Path (Get-JobsRoot) "$JobId.stderr.log"
    $schemaFile = if ($record.type -eq "review") { "review-output.schema.json" } else { "task-output.schema.json" }
    $schemaPath = Get-SchemaPath -Name $schemaFile

    $argList = New-Object System.Collections.Generic.List[string]
    $argList.Add("exec") | Out-Null
    $argList.Add("-C") | Out-Null
    $argList.Add((Get-ProjectRoot)) | Out-Null
    $argList.Add("-s") | Out-Null
    $argList.Add($Sandbox) | Out-Null
    $argList.Add("--json") | Out-Null
    $argList.Add("--output-schema") | Out-Null
    $argList.Add($schemaPath) | Out-Null
    $argList.Add("-o") | Out-Null
    $argList.Add($outputPath) | Out-Null
    if ($Model) {
        $argList.Add("-m") | Out-Null
        $argList.Add($Model) | Out-Null
    }
    $argList.Add("-") | Out-Null

    $promptText = Get-Content -LiteralPath $promptPath -Raw
    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = $agent
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.Arguments = Convert-ToProcessArguments -Arguments $argList

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $psi
    $process.Start() | Out-Null
    $process.StandardInput.Write($promptText)
    $process.StandardInput.Close()

    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()

    $stdout | Set-Content -LiteralPath $jsonlPath -Encoding UTF8
    $stderr | Set-Content -LiteralPath $stderrPath -Encoding UTF8

    $record = Read-JobRecord -JobId $JobId
    $terminalStatus = if ($process.ExitCode -eq 0) { "SUCCESS" } else { "FAILED" }
    $record = Set-JobStatusOnRecord -Record $record -NewStatus $terminalStatus
    $record.output.completed_at = [DateTime]::UtcNow.ToString("o")
    $record.output.exit_code = $process.ExitCode
    $record.output.output_file = $outputPath
    $record.output.events_file = $jsonlPath
    $record.output.stderr_file = $stderrPath
    $record.output.prompt_preview = $promptText.Substring(0, [Math]::Min(140, $promptText.Length))
    Save-JobRecord -Record $record | Out-Null

    if ($record.type -eq "review" -and $record.status -eq "SUCCESS") {
        $record = Set-JobStatusOnRecord -Record $record -NewStatus "REVIEWED"
        Save-JobRecord -Record $record | Out-Null
    }

    $artifactIndex = Write-ArtifactIndex -Record $record -AdditionalPaths @()
    $record = Read-JobRecord -JobId $JobId
    $record.metadata.last_artifact_indexed_at = [DateTime]::UtcNow.ToString("o")
    $record.metadata.evidence_bundle = $artifactIndex
    Save-JobRecord -Record $record | Out-Null

    return (Read-JobRecord -JobId $JobId)
}

function New-WorkflowRecord {
    param(
        [string]$WorkflowId,
        [string]$Objective,
        [object[]]$Jobs,
        [object[]]$Edges
    )

    return [ordered]@{
        id = $WorkflowId
        type = "workflow"
        created_at = [DateTime]::UtcNow.ToString("o")
        objective = $Objective
        status = "PENDING"
        jobs = $Jobs
        edges = $Edges
        metadata = @{
            stage_order = @("HLD", "DD", "CODE", "TEST", "REVIEW")
        }
    }
}

function Save-WorkflowRecord {
    param([object]$Workflow)

    Ensure-Dir (Get-GraphsRoot)
    Write-JsonFile -Path (Get-WorkflowPath -WorkflowId $Workflow.id) -Value $Workflow
    return $Workflow
}

function Read-WorkflowRecord {
    param([string]$WorkflowId)

    $path = Get-WorkflowPath -WorkflowId $WorkflowId
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Workflow not found: $WorkflowId"
    }

    return Read-JsonFile -Path $path
}

function Get-WorkflowStatus {
    param([object]$Workflow)

    $statuses = foreach ($jobRef in $Workflow.jobs) {
        try {
            (Read-JobRecord -JobId $jobRef.job_id).status
        } catch {
            "FAILED"
        }
    }

    if ($statuses.Count -eq 0) {
        return "PENDING"
    }
    if ($statuses -contains "FAILED" -or $statuses -contains "CANCELLED") {
        return "FAILED"
    }
    if ($statuses -contains "RUNNING") {
        return "RUNNING"
    }
    if ($statuses | Where-Object { $_ -eq "PENDING" }) {
        return "PENDING"
    }
    if ($statuses[-1] -eq "REVIEWED") {
        return "REVIEWED"
    }
    if (($statuses | Select-Object -Unique) -contains "SUCCESS") {
        return "SUCCESS"
    }
    return "PENDING"
}

function Update-WorkflowStatus {
    param([string]$WorkflowId)

    $workflow = Read-WorkflowRecord -WorkflowId $WorkflowId
    $workflow.status = Get-WorkflowStatus -Workflow $workflow
    Save-WorkflowRecord -Workflow $workflow | Out-Null
    return $workflow
}

function New-StagePrompt {
    param(
        [string]$Stage,
        [string]$Objective
    )

    switch ($Stage) {
        "HLD" {
            $template = Get-Template -Name "task.md"
            return Render-Template -Template $template -Tokens @{
                TASK = "Produce or refine the HLD for this objective: $Objective"
            }
        }
        "DD" {
            $template = Get-Template -Name "task.md"
            return Render-Template -Template $template -Tokens @{
                TASK = "Produce or refine the DD for this objective: $Objective"
            }
        }
        "CODE" {
            $template = Get-Template -Name "task.md"
            return Render-Template -Template $template -Tokens @{
                TASK = "Implement the objective with minimal diffs: $Objective"
            }
        }
        "TEST" {
            $template = Get-Template -Name "task.md"
            return Render-Template -Template $template -Tokens @{
                TASK = "Add or update validation for this objective and verify behavior: $Objective"
            }
        }
        "REVIEW" {
            $template = Get-Template -Name "review.md"
            return Render-Template -Template $template -Tokens @{
                TARGET = $Objective
            }
        }
        default {
            throw "Unknown workflow stage: $Stage"
        }
    }
}

function New-Workflow {
    param([string]$Objective)

    $workflowId = New-JobId -Prefix "run"
    
    # STEP 0: Retrieve lessons before planning (Issue #5 - Memory Integration)
    $lessonsContext = ""
    try {
        $memoryOutput = & python -m dotagent_runtime.memory_integration_cli `
            --goal "$Objective" `
            --mode retrieve `
            --json-output 2>$null
        
        if ($LASTEXITCODE -eq 0 -and $memoryOutput) {
            $memoryData = $memoryOutput | ConvertFrom-Json
            if ($memoryData.lessons_prompt) {
                $lessonsContext = $memoryData.lessons_prompt
                Write-Output "📚 Retrieved lessons from previous similar tasks"
            }
        }
    } catch {
        Write-Verbose "Memory retrieval skipped: $_"
    }
    
    # STEP 1: Call real DAG planner to generate dynamic DAG (Issue #1 - Real Planning)
    $plannerOutput = $null
    try {
        $projectRoot = Get-ProjectRoot
        $pythonPath = Join-Path (Split-Path $PSScriptRoot -Parent) "runtime"
        
        # Call Python dag_planner_cli to get real DAG with parallelization
        $planOutput = & python -m dotagent_runtime.dag_planner_cli `
            --goal "$Objective" `
            --project-root $projectRoot `
            --json-output 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            $plannerOutput = $planOutput | ConvertFrom-Json
            Write-Output "📊 Generated DAG: $($plannerOutput.task_count) tasks with parallelization: $($plannerOutput.has_parallelization)"
        }
    } catch {
        Write-Warning "Real DAG planner failed, falling back to default pipeline: $_"
    }

    $jobRefs = New-Object System.Collections.Generic.List[object]
    $edges = New-Object System.Collections.Generic.List[object]
    
    $steps = @()
    if ($plannerOutput -and $plannerOutput.tasks) {
        # Use real DAG from dag_planner (automatically parallelized)
        $tasks = $plannerOutput.tasks
        foreach ($task in $tasks) {
            $steps += @{
                id = $task.id
                action = $task.name
                kind = "IMPL"
                tool = "agent"
                deps = $task.depends_on
                priority = 100
                max_attempts = 1
                can_parallelize = $task.can_parallelize
                work_types = $task.work_types
            }
        }
    } elseif ($plannerOutput -and $plannerOutput.dag) {
        # Fallback to old planner format if present
        $steps = $plannerOutput.dag
    } else {
        # Last resort: fixed 5-stage pipeline (legacy)
        Write-Warning "Using default 5-stage pipeline (DAG planner unavailable)"
        $stages = @("HLD", "DD", "CODE", "TEST", "REVIEW")
        $steps = foreach ($stage in $stages) {
            [ordered]@{
                id = $stage.ToLowerInvariant()
                action = "$stage stage"
                kind = $stage
                deps = @()
                priority = 100
                max_attempts = 1
            }
        }
        
        # Add sequential dependencies for fallback
        for ($i = 1; $i -lt $steps.Count; $i++) {
            $steps[$i].deps = @($steps[$i - 1].id)
        }
    }

    # Build job refs and edges from DAG steps
    $stepIdToJobId = @{}
    foreach ($step in $steps) {
        $stepId = $step.id
        $jobId = New-JobId -Prefix ($stepId -replace "[^a-z0-9]", "")
        $stepIdToJobId[$stepId] = $jobId
        
        $jobType = if ($step.kind -eq "REVIEW") { "review" } else { "task" }
        $dependencies = @()
        
        if ($step.deps) {
            foreach ($depStepId in $step.deps) {
                if ($stepIdToJobId.ContainsKey($depStepId)) {
                    $dependencies += $stepIdToJobId[$depStepId]
                    $edges.Add([ordered]@{ from = $stepIdToJobId[$depStepId]; to = $jobId }) | Out-Null
                }
            }
        }

        $metadata = @{
            workflow_id = $workflowId
            step_kind = $step.kind
            tool = $step.tool
            dependencies = $dependencies
            max_attempts = $step.max_attempts
            work_types = if ($step.work_types) { $step.work_types } else { @() }
            can_parallelize = $step.can_parallelize
        }

        # Inject lessons into prompt (Issue #5 - Memory Integration)
        $taskDescription = "$($step.action) - $Objective"
        if ($lessonsContext) {
            $taskDescription = "$taskDescription`n`n$lessonsContext"
        }
        
        $summary = "$($step.action) for: $Objective"
        $prompt = Render-Template -Template (Get-Template -Name "task.md") -Tokens @{ TASK = $taskDescription }
        $jobRecord = New-JobRecord -JobId $jobId -Type $jobType -Summary $summary -PromptText $prompt -TemplateName "task.md" -Metadata $metadata
        Save-PreparedJob -Record $jobRecord | Out-Null

        $jobRefs.Add([ordered]@{
            stage = $step.kind
            job_id = $jobId
            dependencies = $dependencies
            step_id = $stepId
            max_attempts = $step.max_attempts
        }) | Out-Null
    }

    $workflow = New-WorkflowRecord -WorkflowId $workflowId -Objective $Objective -Jobs $jobRefs -Edges $edges
    if ($plannerOutput) {
        $workflow.planner_metadata = $plannerOutput.metadata
        $workflow.dag = $plannerOutput.dag
    }
    Save-WorkflowRecord -Workflow $workflow | Out-Null
    return $workflow
}

function Get-ReadyWorkflowJobs {
    param([object]$Workflow)

    $ready = New-Object System.Collections.Generic.List[object]

    foreach ($jobRef in $Workflow.jobs) {
        $job = Read-JobRecord -JobId $jobRef.job_id
        if ($job.status -ne "PENDING") {
            continue
        }

        $dependencies = @($jobRef.dependencies)
        $isReady = $true
        foreach ($dependencyId in $dependencies) {
            $dependency = Read-JobRecord -JobId $dependencyId
            if ($dependency.status -in @("FAILED", "CANCELLED")) {
                $job.metadata.blocked_by = $dependencyId
                Save-JobRecord -Record $job | Out-Null
                $isReady = $false
                break
            }
            if ($dependency.status -notin @("SUCCESS", "REVIEWED")) {
                $isReady = $false
                break
            }
        }

        if ($isReady) {
            $ready.Add($jobRef) | Out-Null
        }
    }

    return $ready
}

function Invoke-Workflow {
    param(
        [string]$WorkflowId,
        [string]$Model,
        [string]$Sandbox
    )

    $workflow = Update-WorkflowStatus -WorkflowId $WorkflowId
    $maxRetriesPerStep = 3

    while ($true) {
        $workflow = Update-WorkflowStatus -WorkflowId $WorkflowId
        $readyJobs = Get-ReadyWorkflowJobs -Workflow $workflow
        if ($readyJobs.Count -eq 0) {
            break
        }

        foreach ($jobRef in $readyJobs) {
            $job = Read-JobRecord -JobId $jobRef.job_id
            $maxAttempts = if ($jobRef.max_attempts) { $jobRef.max_attempts } else { $maxRetriesPerStep }
            $attempts = 0
            $stepPassed = $false

            while ($attempts -lt $maxAttempts -and -not $stepPassed) {
                $attempts++
                Write-Output "[$($job.summary)] Attempt $attempts of $maxAttempts..."
                
                # STEP 1: Check if tool can be handled internally
                $tool = $job.metadata.tool ?? "agent"
                $isInternalTool = @("write_file", "read_file", "run_tests", "run_linter", "build", "copy_file", "delete_file", "list_files", "run_command") -contains $tool
                
                if ($isInternalTool) {
                    # Dispatch to internal tool dispatcher
                    try {
                        $projectRoot = Get-ProjectRoot
                        $toolPayload = $job.metadata.payload ?? @{}
                        
                        $toolResult = & python -m dotagent_runtime.tool_dispatcher `
                            --tool $tool `
                            --payload (ConvertTo-Json $toolPayload -Compress) `
                            --project-root $projectRoot `
                            --json-output 2>$null

                        if ($LASTEXITCODE -eq 0 -and $toolResult) {
                            $result = $toolResult | ConvertFrom-Json
                            $job.output.exit_code = if ($result.success) { 0 } else { 1 }
                            $job.output.stdout = $result.stdout
                            $job.output.stderr = $result.stderr
                            $job.output.output_file = $result.output
                            $job.status = if ($result.success) { "SUCCESS" } else { "FAILED" }
                        } else {
                            $job.status = "FAILED"
                            $job.output.exit_code = 1
                        }
                    } catch {
                        Write-Warning "Internal tool dispatch failed, falling back to agent: $_"
                        $isInternalTool = $false
                    }
                }
                
                # STEP 2: If not internal tool or dispatch failed, call agent
                if (-not $isInternalTool) {
                    Invoke-AgentPreparedJob -JobId $jobRef.job_id -Model $Model -Sandbox $Sandbox | Out-Null
                }
                
                $job = Read-JobRecord -JobId $jobRef.job_id

                # STEP 3: Real output validation (not just exit code)
                if ($job.status -eq "SUCCESS" -or $job.status -eq "RUNNING") {
                    try {
                        $tempStepFile = Join-Path ([System.IO.Path]::GetTempPath()) "step_$(New-Guid).json"
                        $tempResultFile = Join-Path ([System.IO.Path]::GetTempPath()) "result_$(New-Guid).json"
                        
                        $stepData = @{
                            step_id = $jobRef.step_id
                            kind = $jobRef.stage
                            metadata = $job.metadata
                        }

                        $resultData = @{
                            job_id = $jobRef.job_id
                            status = $job.status
                            output = $job.output
                            artifacts = $job.artifacts
                        }

                        # Write to temp files
                        ConvertTo-Json $stepData | Set-Content -Path $tempStepFile -Encoding UTF8
                        ConvertTo-Json $resultData | Set-Content -Path $tempResultFile -Encoding UTF8

                        # Call Python output validator for comprehensive checks
                        $validationOutput = $null
                        try {
                            $projectRoot = Get-ProjectRoot
                            $validationJson = & python -m dotagent_runtime.output_validator `
                                --step-json $tempStepFile `
                                --result-json $tempResultFile `
                                --project-root $projectRoot `
                                --json-output 2>$null

                            if ($LASTEXITCODE -eq 0 -and $validationJson) {
                                $validationOutput = $validationJson | ConvertFrom-Json
                            }
                        } catch {
                            Write-Warning "Output validator error, using basic checks: $_"
                        } finally {
                            if (Test-Path -LiteralPath $tempStepFile) { Remove-Item -LiteralPath $tempStepFile -Force -ErrorAction SilentlyContinue }
                            if (Test-Path -LiteralPath $tempResultFile) { Remove-Item -LiteralPath $tempResultFile -Force -ErrorAction SilentlyContinue }
                        }

                        # Process validation result
                        if ($validationOutput -and $validationOutput.status -eq "PASS") {
                            $job.validation = $validationOutput
                            Save-JobRecord -Record $job | Out-Null
                            $stepPassed = $true
                            Write-Output "  ✓ Output validation passed"
                        } elseif ($validationOutput -and $validationOutput.retryable -and $attempts -lt $maxAttempts) {
                            # STEP 4: Use failure analyzer to generate intelligent corrective actions
                            Write-Output "  ✗ Output validation failed: $($validationOutput.status)"
                            
                            # Store failure lesson (Issue #5 - Memory Integration)
                            try {
                                $projectRoot = Get-ProjectRoot
                                $tempStepFile2 = Join-Path ([System.IO.Path]::GetTempPath()) "step_mem_$(New-Guid).json"
                                $tempResultFile2 = Join-Path ([System.IO.Path]::GetTempPath()) "result_mem_$(New-Guid).json"
                                
                                $stepJson = @{
                                    step_id = $jobRef.step_id
                                    kind = $jobRef.stage
                                    action = $job.summary
                                }
                                $resultJson = @{
                                    status = $job.status
                                    errors = $validationOutput.errors
                                    stderr = $job.output.stderr
                                }
                                
                                ConvertTo-Json $stepJson | Set-Content -Path $tempStepFile2 -Encoding UTF8
                                ConvertTo-Json $resultJson | Set-Content -Path $tempResultFile2 -Encoding UTF8
                                
                                # Store the failure as a lesson for future similar tasks
                                & python -m dotagent_runtime.memory_integration_cli `
                                    --goal "$($job.summary)" `
                                    --step-json $tempStepFile2 `
                                    --result-json $tempResultFile2 `
                                    --attempt $(($attempts - 1)) `
                                    --mode store `
                                    --json-output 2>$null | Out-Null
                                Write-Output "  💾 Failure pattern stored for learning"
                                
                                Remove-Item -LiteralPath $tempStepFile2 -Force -ErrorAction SilentlyContinue
                                Remove-Item -LiteralPath $tempResultFile2 -Force -ErrorAction SilentlyContinue
                            } catch {
                                Write-Verbose "Memory storage skipped: $_"
                            }
                            
                            # Generate corrective prompt using failure info
                            $correctionPrompt = @"
## Validation Feedback

**Issues Found:**
"@
                            foreach ($error in $validationOutput.errors) {
                                $correctionPrompt += "`n- [$($error.category)] $($error.detail)"
                                $correctionPrompt += "`n  Fix: $($error.fix_suggestion)"
                            }
                            
                            if ($validationOutput.corrective_actions) {
                                $correctionPrompt += "`n`n**What to fix:**`n"
                                foreach ($action in $validationOutput.corrective_actions) {
                                    $correctionPrompt += "- $action`n"
                                }
                            }
                            
                            $job.correction_context = $correctionPrompt
                            Save-JobRecord -Record $job | Out-Null
                            
                            # Mark as pending for retry with new prompt
                            $job.status = "PENDING"
                            Save-JobRecord -Record $job | Out-Null
                            Write-Output "  Retrying with corrective guidance..."
                        } else {
                            # Non-retryable failure or max retries exhausted
                            $job.validation = $validationOutput
                            Save-JobRecord -Record $job | Out-Null
                            $stepPassed = $true
                            if ($validationOutput -and $validationOutput.status -ne "PASS") {
                                Write-Output "  ✗ Validation failed (non-retryable)"
                                
                                # Store non-retryable failure as critical lesson (Issue #5 - Memory Integration)
                                try {
                                    $tempStepFile3 = Join-Path ([System.IO.Path]::GetTempPath()) "step_mem_$(New-Guid).json"
                                    $tempResultFile3 = Join-Path ([System.IO.Path]::GetTempPath()) "result_mem_$(New-Guid).json"
                                    
                                    $stepJson = @{
                                        step_id = $jobRef.step_id
                                        kind = $jobRef.stage
                                        action = $job.summary
                                    }
                                    $resultJson = @{
                                        status = "CRITICAL_FAILURE"
                                        errors = $validationOutput.errors
                                        non_retryable = $true
                                    }
                                    
                                    ConvertTo-Json $stepJson | Set-Content -Path $tempStepFile3 -Encoding UTF8
                                    ConvertTo-Json $resultJson | Set-Content -Path $tempResultFile3 -Encoding UTF8
                                    
                                    & python -m dotagent_runtime.memory_integration_cli `
                                        --goal "$($job.summary)" `
                                        --step-json $tempStepFile3 `
                                        --result-json $tempResultFile3 `
                                        --attempt $(($attempts - 1)) `
                                        --mode store `
                                        --json-output 2>$null | Out-Null
                                    Write-Output "  💾 Critical failure stored for learning"
                                    
                                    Remove-Item -LiteralPath $tempStepFile3 -Force -ErrorAction SilentlyContinue
                                    Remove-Item -LiteralPath $tempResultFile3 -Force -ErrorAction SilentlyContinue
                                } catch {
                                    Write-Verbose "Memory storage skipped: $_"
                                }
                            }
                        }
                    } catch {
                        Write-Warning "Validation check error: $_"
                        $stepPassed = $true
                    }
                } else {
                    # Job failed execution
                    if ($attempts -lt $maxAttempts) {
                        Write-Output "  ✗ Execution failed, retrying..."
                        
                        # Store execution failure as lesson (Issue #5 - Memory Integration)
                        try {
                            $tempStepFile4 = Join-Path ([System.IO.Path]::GetTempPath()) "step_mem_$(New-Guid).json"
                            $tempResultFile4 = Join-Path ([System.IO.Path]::GetTempPath()) "result_mem_$(New-Guid).json"
                            
                            $stepJson = @{
                                step_id = $jobRef.step_id
                                kind = $jobRef.stage
                                action = $job.summary
                            }
                            $resultJson = @{
                                status = $job.status
                                exit_code = $job.output.exit_code
                                stderr = $job.output.stderr
                            }
                            
                            ConvertTo-Json $stepJson | Set-Content -Path $tempStepFile4 -Encoding UTF8
                            ConvertTo-Json $resultJson | Set-Content -Path $tempResultFile4 -Encoding UTF8
                            
                            & python -m dotagent_runtime.memory_integration_cli `
                                --goal "$($job.summary)" `
                                --step-json $tempStepFile4 `
                                --result-json $tempResultFile4 `
                                --attempt $(($attempts - 1)) `
                                --mode store `
                                --json-output 2>$null | Out-Null
                            Write-Output "  💾 Execution failure stored for learning"
                            
                            Remove-Item -LiteralPath $tempStepFile4 -Force -ErrorAction SilentlyContinue
                            Remove-Item -LiteralPath $tempResultFile4 -Force -ErrorAction SilentlyContinue
                        } catch {
                            Write-Verbose "Memory storage skipped: $_"
                        }
                        
                        $job.status = "PENDING"
                        Save-JobRecord -Record $job | Out-Null
                    } else {
                        Write-Output "  ✗ Execution failed after $maxAttempts attempts"
                        $stepPassed = $true
                        
                        # Store final failure as critical lesson
                        try {
                            $tempStepFile5 = Join-Path ([System.IO.Path]::GetTempPath()) "step_mem_$(New-Guid).json"
                            $tempResultFile5 = Join-Path ([System.IO.Path]::GetTempPath()) "result_mem_$(New-Guid).json"
                            
                            $stepJson = @{
                                step_id = $jobRef.step_id
                                kind = $jobRef.stage
                                action = $job.summary
                            }
                            $resultJson = @{
                                status = "EXECUTION_EXHAUSTED"
                                max_attempts = $maxAttempts
                                stderr = $job.output.stderr
                            }
                            
                            ConvertTo-Json $stepJson | Set-Content -Path $tempStepFile5 -Encoding UTF8
                            ConvertTo-Json $resultJson | Set-Content -Path $tempResultFile5 -Encoding UTF8
                            
                            & python -m dotagent_runtime.memory_integration_cli `
                                --goal "$($job.summary)" `
                                --step-json $tempStepFile5 `
                                --result-json $tempResultFile5 `
                                --attempt $(($attempts - 1)) `
                                --mode store `
                                --json-output 2>$null | Out-Null
                            Write-Output "  💾 Exhausted all attempts, critical failure stored"
                            
                            Remove-Item -LiteralPath $tempStepFile5 -Force -ErrorAction SilentlyContinue
                            Remove-Item -LiteralPath $tempResultFile5 -Force -ErrorAction SilentlyContinue
                        } catch {
                            Write-Verbose "Memory storage skipped: $_"
                        }
                    }
                }
            }

            $workflow = Update-WorkflowStatus -WorkflowId $WorkflowId
            if ($workflow.status -eq "FAILED") {
                return $workflow
            }
        }
    }

    return (Update-WorkflowStatus -WorkflowId $WorkflowId)
}

function Try-ReadWorkflow {
    param([string]$WorkflowId)

    $path = Get-WorkflowPath -WorkflowId $WorkflowId
    if (Test-Path -LiteralPath $path) {
        return Read-JsonFile -Path $path
    }

    return $null
}

function Format-WorkflowStatusLine {
    param([object]$Workflow)

    return "$($Workflow.id) [workflow] $($Workflow.status) - $($Workflow.objective)"
}

switch ($Command) {
    "setup" {
        Ensure-Dir (Get-StateRoot)
        Ensure-Dir (Get-JobsRoot)
        Ensure-Dir (Get-GraphsRoot)
        Write-Output "dotagent runtime ready: $(Get-StateRoot)"
    }
    "task" {
        if (-not $Text) {
            throw "Provide task text."
        }

        $jobId = New-JobId -Prefix "task"
        $templateName = "task.md"
        $prompt = Render-Template -Template (Get-Template -Name $templateName) -Tokens @{ TASK = $Text }
        $record = New-JobRecord -JobId $jobId -Type "task" -Summary $Text -PromptText $prompt -TemplateName $templateName -Metadata @{ dependencies = @() }
        $paths = Save-PreparedJob -Record $record
        Write-ArtifactIndex -Record (Read-JobRecord -JobId $jobId) -AdditionalPaths @() | Out-Null

        Write-Output "Prepared task: $jobId"
        Write-Output "Prompt: $($paths.prompt)"
        Write-Output "Record: $($paths.json)"

        if ($Execute) {
            $result = Invoke-AgentPreparedJob -JobId $jobId -Model $Model -Sandbox $Sandbox
            Write-Output "Executed task: $($result.id) [$($result.status)]"
            Write-Output "Output: $($result.output.output_file)"
        }
    }
    "review" {
        $reviewTarget = if ($Target) { $Target } elseif ($Text) { $Text } else { "current change set" }
        $jobId = New-JobId -Prefix "review"
        $templateName = "review.md"
        $prompt = Render-Template -Template (Get-Template -Name $templateName) -Tokens @{ TARGET = $reviewTarget }
        $record = New-JobRecord -JobId $jobId -Type "review" -Summary $reviewTarget -PromptText $prompt -TemplateName $templateName -Metadata @{ dependencies = @() }
        $paths = Save-PreparedJob -Record $record
        Write-ArtifactIndex -Record (Read-JobRecord -JobId $jobId) -AdditionalPaths @() | Out-Null

        Write-Output "Prepared review: $jobId"
        Write-Output "Prompt: $($paths.prompt)"
        Write-Output "Record: $($paths.json)"

        if ($Execute) {
            $result = Invoke-AgentPreparedJob -JobId $jobId -Model $Model -Sandbox $Sandbox
            Write-Output "Executed review: $($result.id) [$($result.status)]"
            Write-Output "Output: $($result.output.output_file)"
        }
    }
    "run" {
        if (-not $Text) {
            throw "Provide orchestration text."
        }

        $workflow = New-Workflow -Objective $Text
        Write-Output "Prepared workflow: $($workflow.id)"
        Write-Output "Graph: $(Get-WorkflowPath -WorkflowId $workflow.id)"

        foreach ($jobRef in $workflow.jobs) {
            Write-Output "Stage: $($jobRef.stage) -> $($jobRef.job_id)"
        }

        if ($Execute) {
            $result = Invoke-Workflow -WorkflowId $workflow.id -Model $Model -Sandbox $Sandbox
            Write-Output "Executed workflow: $($result.id) [$($result.status)]"
        }
    }
    "status" {
        $graphsRoot = Get-GraphsRoot
        if (Test-Path -LiteralPath $graphsRoot) {
            Get-ChildItem -LiteralPath $graphsRoot -Filter *.json -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTime -Descending |
                ForEach-Object {
                    $workflow = Read-JsonFile -Path $_.FullName
                    $workflow = Update-WorkflowStatus -WorkflowId $workflow.id
                    Write-Output (Format-WorkflowStatusLine -Workflow $workflow)
                }
        }

        $jobsRoot = Get-JobsRoot
        if (-not (Test-Path -LiteralPath $jobsRoot)) {
            if (-not (Test-Path -LiteralPath $graphsRoot)) {
                Write-Output "No dotagent state found."
            }
            break
        }

        Get-ChildItem -LiteralPath $jobsRoot -Filter *.json |
            Where-Object { $_.Name -notlike "*.artifacts.json" } |
            Sort-Object LastWriteTime -Descending |
            ForEach-Object {
                $record = Normalize-JobRecord -Record (Read-JsonFile -Path $_.FullName)
                Write-Output "$($record.id) [$($record.type)] $($record.status) - $($record.input.summary)"
            }
    }
    "result" {
        if (-not $Id) {
            throw "Provide -Id for result."
        }

        $workflow = Try-ReadWorkflow -WorkflowId $Id
        if ($workflow) {
            $workflow = Update-WorkflowStatus -WorkflowId $Id
            Write-Output ($workflow | ConvertTo-Json -Depth 8)
            break
        }

        $record = Read-JobRecord -JobId $Id
        Write-Output ($record | ConvertTo-Json -Depth 8)
        if ($record.output.output_file -and (Test-Path -LiteralPath $record.output.output_file)) {
            Write-Output ""
            Write-Output "--- output ---"
            Get-Content -LiteralPath $record.output.output_file
        }
    }
    "cancel" {
        if (-not $Id) {
            throw "Provide -Id for cancel."
        }

        $workflow = Try-ReadWorkflow -WorkflowId $Id
        if ($workflow) {
            foreach ($jobRef in $workflow.jobs) {
                $job = Read-JobRecord -JobId $jobRef.job_id
                if ($job.status -in @("PENDING", "RUNNING")) {
                    $job = Set-JobStatusOnRecord -Record $job -NewStatus "CANCELLED"
                    Save-JobRecord -Record $job | Out-Null
                    Write-ArtifactIndex -Record $job -AdditionalPaths @() | Out-Null
                }
            }
            $workflow.status = "FAILED"
            Save-WorkflowRecord -Workflow $workflow | Out-Null
            Write-Output "Cancelled workflow: $Id"
            break
        }

        $record = Read-JobRecord -JobId $Id
        if ($record.status -notin @("PENDING", "RUNNING")) {
            throw "Only PENDING or RUNNING jobs can be cancelled."
        }
        $record = Set-JobStatusOnRecord -Record $record -NewStatus "CANCELLED"
        Save-JobRecord -Record $record | Out-Null
        Write-ArtifactIndex -Record $record -AdditionalPaths @() | Out-Null
        Write-Output "Cancelled: $Id"
    }
}


