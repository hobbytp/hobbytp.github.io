# Fix: Metadata Discrepancy in Blog Posts

## Why

Users report that the metadata displayed on blog posts (publish date, word count, reading time) does not match the information provided in the Markdown front matter.

Specific issues:
1.  **Date Mismatch**: The displayed date may not reflect the `date` field in front matter, potentially due to timezone handling or fallback logic.
2.  **Word Count & Reading Time**: The template currently uses Hugo's auto-calculated `.WordCount` and `.ReadingTime` variables, which ignores the manual overrides (`wordCount`, `readingTime`) specified in the front matter.

This discrepancy confuses readers and authors, as the displayed information is inaccurate compared to the source of truth in the content file.

## What Changes

### 1. Update Templates (`layouts/_default/single.html` and `layouts/_default/list.html`)

Modify the metadata display logic to prioritize front matter parameters over Hugo's auto-calculated values:

-   **Word Count**: Check `.Params.wordCount` first. If set, use it; otherwise fallback to `.WordCount`.
-   **Reading Time**: Check `.Params.readingTime` first. If set, use it; otherwise fallback to `.ReadingTime`.
-   **Date**: Ensure the date display respects the front matter `date`. Verify if `.Date` is correctly picking up the front matter date. If needed, explicitly use `.Params.date` or debug timezone configuration.

### 2. Verify Timezone Configuration

Check `hugo.toml` for timezone settings to ensure `2025-12-04T20:00:00+08:00` is displayed correctly.

## Validation

-   Create a test post with mismatched front matter and content statistics.
-   Verify that the rendered page displays the values from front matter.
