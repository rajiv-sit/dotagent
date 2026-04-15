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

function Get-Template {
    param([string]$Name)

    return Get-Content -LiteralPath (Join-Path (Get-RepoRoot) "prompts\$Name") -Raw
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
    $cmd = Get-Command agent.cmd -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    $shim = Get-Command agent -ErrorAction SilentlyContinue
    if ($shim -and $shim.Source -like "*.cmd") {
        return $shim.Source
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
        throw "agent.cmd was not found on PATH."
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
    $stages = @("HLD", "DD", "CODE", "TEST", "REVIEW")
    $jobRefs = New-Object System.Collections.Generic.List[object]
    $edges = New-Object System.Collections.Generic.List[object]
    $previousJobId = $null

    foreach ($stage in $stages) {
        $jobType = if ($stage -eq "REVIEW") { "review" } else { "task" }
        $jobId = New-JobId -Prefix ($stage.ToLowerInvariant())
        $dependencies = @()
        if ($previousJobId) {
            $dependencies = @($previousJobId)
            $edges.Add([ordered]@{ from = $previousJobId; to = $jobId }) | Out-Null
        }

        $metadata = @{
            workflow_id = $workflowId
            stage = $stage
            dependencies = $dependencies
        }

        $prompt = New-StagePrompt -Stage $stage -Objective $Objective
        $summary = "$stage stage for: $Objective"
        $templateName = if ($stage -eq "REVIEW") { "review.md" } else { "task.md" }
        $jobRecord = New-JobRecord -JobId $jobId -Type $jobType -Summary $summary -PromptText $prompt -TemplateName $templateName -Metadata $metadata
        Save-PreparedJob -Record $jobRecord | Out-Null

        $jobRefs.Add([ordered]@{
            stage = $stage
            job_id = $jobId
            dependencies = $dependencies
        }) | Out-Null

        $previousJobId = $jobId
    }

    $workflow = New-WorkflowRecord -WorkflowId $workflowId -Objective $Objective -Jobs $jobRefs -Edges $edges
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

    while ($true) {
        $workflow = Update-WorkflowStatus -WorkflowId $WorkflowId
        $readyJobs = Get-ReadyWorkflowJobs -Workflow $workflow
        if ($readyJobs.Count -eq 0) {
            break
        }

        foreach ($jobRef in $readyJobs) {
            Invoke-AgentPreparedJob -JobId $jobRef.job_id -Model $Model -Sandbox $Sandbox | Out-Null
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


