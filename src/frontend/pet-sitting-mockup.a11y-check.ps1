param(
  [string]$FilePath = "src/frontend/pet-sitting-mockup.html"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path -Path $FilePath)) {
  throw "File not found: $FilePath"
}

$content = Get-Content -Raw -Path $FilePath

if ($content -notmatch "\.book-btn:focus-visible\s*\{") {
  throw "Missing .book-btn:focus-visible style block."
}

function Remove-CssComments([string]$css) {
  return [regex]::Replace($css, "/\*.*?\*/", "", [System.Text.RegularExpressions.RegexOptions]::Singleline)
}

function Get-CssPropertyMap([string]$declarations) {
  $properties = @{}
  $matches = [regex]::Matches($declarations, "(?is)(?<name>[a-zA-Z-]+)\s*:\s*(?<value>[^;]+);?")
  foreach ($match in $matches) {
    $properties[$match.Groups["name"].Value.Trim().ToLowerInvariant()] = $match.Groups["value"].Value.Trim()
  }

  return $properties
}

function Get-CssVariables([string]$css) {
  $variables = @{}
  $rootBlocks = [regex]::Matches($css, "(?is):root\s*\{(?<body>.*?)\}")
  foreach ($rootBlock in $rootBlocks) {
    $declarations = Get-CssPropertyMap $rootBlock.Groups["body"].Value
    foreach ($entry in $declarations.GetEnumerator()) {
      if ($entry.Key.StartsWith("--")) {
        $variables[$entry.Key] = $entry.Value
      }
    }
  }

  return $variables
}

function Get-SelectorProperties([string]$css, [string]$selector) {
  $properties = @{}
  $selectorPattern = [regex]::Escape($selector)
  $blocks = [regex]::Matches($css, "(?is)$selectorPattern\s*\{(?<body>.*?)\}")
  foreach ($block in $blocks) {
    $blockProperties = Get-CssPropertyMap $block.Groups["body"].Value
    foreach ($entry in $blockProperties.GetEnumerator()) {
      $properties[$entry.Key] = $entry.Value
    }
  }

  return $properties
}

function Resolve-CssValue([string]$value, [hashtable]$variables, [int]$maxDepth = 10) {
  $resolved = $value
  $pattern = "var\(\s*(?<name>--[a-zA-Z0-9_-]+)\s*(?:,\s*(?<fallback>[^)]+))?\)"

  for ($i = 0; $i -lt $maxDepth; $i++) {
    $next = [regex]::Replace($resolved, $pattern, {
      param($match)
      $name = $match.Groups["name"].Value
      $fallback = $match.Groups["fallback"].Value.Trim()

      if ($variables.ContainsKey($name)) {
        return $variables[$name]
      }

      if ($fallback.Length -gt 0) {
        return $fallback
      }

      return $match.Value
    })

    if ($next -eq $resolved) {
      break
    }

    $resolved = $next
  }

  return $resolved.Trim()
}

function Get-InlineStyleProperties([string]$htmlContent, [string]$className) {
  $pattern = "(?is)<(?<tag>[a-z0-9:-]+)\b(?<attrs>[^>]*\bclass\s*=\s*['""]?[^'"">]*\b$className\b[^'"">]*['""]?[^>]*)>"
  $elementMatch = [regex]::Match($htmlContent, $pattern)
  if (-not $elementMatch.Success) {
    return @{}
  }

  $attrs = $elementMatch.Groups["attrs"].Value
  $styleMatch = [regex]::Match($attrs, "(?is)\bstyle\s*=\s*['""](?<style>[^'""]*)['""]")
  if (-not $styleMatch.Success) {
    return @{}
  }

  return Get-CssPropertyMap $styleMatch.Groups["style"].Value
}

function Convert-CssColorToHex([string]$cssColor) {
  $value = $cssColor.Trim().ToLowerInvariant()
  if ($value -match "^#(?<hex>[0-9a-f]{3}|[0-9a-f]{6})$") {
    $hex = $matches["hex"]
    if ($hex.Length -eq 3) {
      return ("#{0}{0}{1}{1}{2}{2}" -f $hex[0], $hex[1], $hex[2])
    }

    return "#$hex"
  }

  if ($value -match "^rgba?\(\s*(?<r>\d{1,3})\s*,\s*(?<g>\d{1,3})\s*,\s*(?<b>\d{1,3})(?:\s*,\s*(?<a>0|0?\.\d+|1(?:\.0+)?))?\s*\)$") {
    $r = [math]::Max(0, [math]::Min(255, [int]$matches["r"]))
    $g = [math]::Max(0, [math]::Min(255, [int]$matches["g"]))
    $b = [math]::Max(0, [math]::Min(255, [int]$matches["b"]))
    return ("#{0:x2}{1:x2}{2:x2}" -f $r, $g, $b)
  }

  throw "Unsupported color format '$cssColor'. Use hex or rgb(a)."
}

function Get-BackgroundColorValue([hashtable]$properties) {
  if ($properties.ContainsKey("background-color")) {
    return $properties["background-color"]
  }

  if ($properties.ContainsKey("background")) {
    return $properties["background"]
  }

  return $null
}

function Extract-FirstColorToken([string]$value) {
  $hexMatch = [regex]::Match($value, "(?i)#[0-9a-f]{3,6}")
  if ($hexMatch.Success) {
    return $hexMatch.Value
  }

  $rgbMatch = [regex]::Match($value, "(?i)rgba?\([^)]+\)")
  if ($rgbMatch.Success) {
    return $rgbMatch.Value
  }

  return $value
}

function Get-Luminance([string]$hex) {
  $r = [convert]::ToInt32($hex.Substring(1, 2), 16) / 255
  $g = [convert]::ToInt32($hex.Substring(3, 2), 16) / 255
  $b = [convert]::ToInt32($hex.Substring(5, 2), 16) / 255

  $channels = @($r, $g, $b) | ForEach-Object {
    if ($_ -le 0.03928) { $_ / 12.92 } else { [math]::Pow((($_ + 0.055) / 1.055), 2.4) }
  }

  return (0.2126 * $channels[0]) + (0.7152 * $channels[1]) + (0.0722 * $channels[2])
}

function Get-ContrastRatio([string]$colorA, [string]$colorB) {
  $l1 = Get-Luminance $colorA
  $l2 = Get-Luminance $colorB

  if ($l1 -lt $l2) {
    $tmp = $l1
    $l1 = $l2
    $l2 = $tmp
  }

  return ($l1 + 0.05) / ($l2 + 0.05)
}

$styleBlocks = [regex]::Matches($content, "(?is)<style\b[^>]*>(?<css>.*?)</style>")
if ($styleBlocks.Count -eq 0) {
  throw "No <style> block found in file: $FilePath"
}

$combinedCss = ""
foreach ($block in $styleBlocks) {
  $combinedCss += $block.Groups["css"].Value + "`n"
}
$combinedCss = Remove-CssComments $combinedCss

$cssVariables = Get-CssVariables $combinedCss
$bookBtnProperties = Get-SelectorProperties -css $combinedCss -selector ".book-btn"
$inlineProperties = Get-InlineStyleProperties -htmlContent $content -className "book-btn"
foreach ($entry in $inlineProperties.GetEnumerator()) {
  $bookBtnProperties[$entry.Key] = $entry.Value
}

if (-not $bookBtnProperties.ContainsKey("color")) {
  throw "Could not find .book-btn text color in CSS/inline styles."
}

$bgValue = Get-BackgroundColorValue $bookBtnProperties
if (-not $bgValue) {
  throw "Could not find .book-btn background color in CSS/inline styles."
}

$resolvedText = Resolve-CssValue -value $bookBtnProperties["color"] -variables $cssVariables
$resolvedBackground = Resolve-CssValue -value $bgValue -variables $cssVariables
$textHex = Convert-CssColorToHex (Extract-FirstColorToken $resolvedText)
$backgroundHex = Convert-CssColorToHex (Extract-FirstColorToken $resolvedBackground)

$ratio = Get-ContrastRatio -colorA $backgroundHex -colorB $textHex
if ($ratio -lt 4.5) {
  throw ("Contrast ratio too low for .book-btn text/background ({0} on {1}): {2:N2}:1" -f $textHex, $backgroundHex, $ratio)
}

Write-Output ("PASS: .book-btn contrast {0:N2}:1 ({1} on {2}) and focus-visible style present." -f $ratio, $textHex, $backgroundHex)
