import os
import glob

def generate():
    redirects_path = os.path.join('site', 'public', '_redirects')
    lines = ['# Cloudflare Pages Edge Directives - Instant Affiliate Hops\n']
    
    for filepath in sorted(glob.glob('site/src/content/reviews/*.md')):
        slug = os.path.splitext(os.path.basename(filepath))[0]
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        aff = ''
        web = ''
        for line in content.splitlines():
            if line.startswith('affiliate_url:'):
                aff = line.split(':', 1)[1].strip().strip('"\'')
            elif line.startswith('website_url:'):
                web = line.split(':', 1)[1].strip().strip('"\'')
                
        target = aff if aff else web
        if target:
            lines.append(f'/go/{slug} {target} 302\n')
            
    with open(redirects_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"Generated {len(lines)-1} redirects in {redirects_path}")

if __name__ == '__main__':
    generate()
