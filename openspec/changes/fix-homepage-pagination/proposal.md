# Fix Homepage Content Display and Pagination

## Why
Currently, the homepage only displays content from the "daily_ai" section because `site.Params.mainSections` filters content. Additionally, pagination is broken because of hardcoded `first 10` range which ignores the paginator object.

## What Changes
- Update `layouts/_default/list.html` to remove restrictive section filtering when `mainSections` is not defined.
- Replace `range first 10` with proper `.Paginate` usage to support pagination.
- Ensure all regular pages are candidates for the homepage list unless filtered.

## Impact
- Homepage will display articles from all sections (DeepSeek, Papers, Posts, etc.).
- Pagination navigation (Next/Prev) will work correctly.
