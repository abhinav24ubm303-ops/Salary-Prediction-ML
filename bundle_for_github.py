"""
bundle_for_github.py - Generates a 100% self-contained index.html for GitHub Pages.
Inlines all CSS, all JavaScript, and the complete Model Dataset so that GitHub Pages
NEVER has missing 404 assets or folder path issues.
"""

import os
import json

def bundle():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, 'templates', 'index.html')
    css_path = os.path.join(base_dir, 'static', 'css', 'styles.css')
    json_path = os.path.join(base_dir, 'static', 'data', 'model_data.json')
    js_path = os.path.join(base_dir, 'static', 'js', 'app.js')
    output_path = os.path.join(base_dir, 'index.html')

    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    with open(css_path, 'r', encoding='utf-8') as f:
        css = f.read()

    with open(json_path, 'r', encoding='utf-8') as f:
        data_json = f.read()

    with open(js_path, 'r', encoding='utf-8') as f:
        js = f.read()

    # Inlining CSS
    css_replacement = f"<style>\n{css}\n</style>"
    target_css_link = '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/styles.css\') }}">'
    if target_css_link in html:
        html = html.replace(target_css_link, css_replacement)
    else:
        # Fallback search
        html = html.replace('<link rel="stylesheet" href="static/css/styles.css">', css_replacement)

    # Inlining Data and JS
    target_data_script = '<script src="{{ url_for(\'static\', filename=\'data/model_data.js\') }}"></script>'
    if target_data_script in html:
        html = html.replace(target_data_script, '')
    else:
        html = html.replace('<script src="static/data/model_data.js"></script>', '')

    embedded_js_block = f"""
  <!-- Inlined Model Data for 100% Reliable GitHub Pages Deployment -->
  <script>
    window.EMBEDDED_MODEL_DATA = {data_json};
  </script>
  <!-- Inlined Application Controller -->
  <script>
{js}
  </script>
"""

    target_app_script = '<script src="{{ url_for(\'static\', filename=\'js/app.js\') }}"></script>'
    if target_app_script in html:
        html = html.replace(target_app_script, embedded_js_block)
    elif '<script src="static/js/app.js"></script>' in html:
        html = html.replace('<script src="static/js/app.js"></script>', embedded_js_block)
    else:
        html = html.replace('</body>', f'{embedded_js_block}\n</body>')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    # Also create .nojekyll in root
    nojekyll_path = os.path.join(base_dir, '.nojekyll')
    with open(nojekyll_path, 'w', encoding='utf-8') as f:
        f.write('')

    print(f"Successfully generated self-contained index.html at {output_path}")
    print(f"File size: {os.path.getsize(output_path):,} bytes")
    print(f"Created .nojekyll at {nojekyll_path}")

if __name__ == '__main__':
    bundle()
