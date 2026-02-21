---
description: generate a blog by using 3 files automatically
---


1. Run the generation script:
   ```bash
   uv run python scripts/generate_paper_blog_from_three_files.py --output-dir {folder} {file_name}
   ```

### Parameter Explanation:
* `{folder}`: The folder name under `content/zh/`.
* `{file_name}`: The common file name (exclude postfix) under the `static/tmp` folder. The 3 required files are: `{file_name}.png`, `{file_name}.csv` and `{file_name}.pdf`.