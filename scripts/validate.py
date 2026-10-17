"""Dependency-free structure and public-data checks; not a complete secret detector."""

import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

PUBLIC_FILES = frozenset({
    '.github/pull_request_template.md', '.github/workflows/validate.yml', '.gitignore',
    'CONTRIBUTING.md', 'LICENSE', 'README.md', 'SECURITY.md', 'SKILL.md',
    'agents/openai.yaml', 'assets/team-context.example.json',
    'references/gear-map.md', 'references/workflows.md',
    'scripts/validate.py', 'tests/test_validate.py',
    '.codex-plugin/plugin.json', '.app.json',
    'skills/intgral-meeting/SKILL.md', 'skills/intgral-meeting/agents/openai.yaml',
    'skills/intgral-meeting/references/wispr.md',
    'skills/intgral-meeting/references/archive.md',
    'skills/intgral-meeting/references/topdown.md',
})
RULES = (
    ('credential token', re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{24,}|AKIA[A-Z0-9]{16})\b')),
    ('private key', re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
    ('bearer credential', re.compile(r'(?i)\bBearer\s+[A-Za-z0-9._-]{24,}')),
    ('personal email', re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')),
    ('personal machine path', re.compile(r'/(?:Users|home)/[A-Za-z0-9_.-]+/')),
    ('internal document link', re.compile(r'https?://docs[.]intgral[.]ai/(?:doc|collection)/[A-Za-z0-9_-]+')),
    ('private design link', re.compile(r'https?://(?:www[.])?figma[.]com/(?:design|file|board|slides|proto)/[A-Za-z0-9_-]+')),
    ('private file link', re.compile(r'https?://(?:drive|docs)[.]google[.]com/(?:file/d|drive/(?:u/\d+/)?folders|document/d|spreadsheets/d|presentation/d)/[A-Za-z0-9_-]+')),
    ('private communication link', re.compile(r'https?://(?:app[.]slack[.]com/client/|[A-Za-z0-9-]+[.]slack[.]com/archives/|linear[.]app/[A-Za-z0-9_-]+/(?:issue|project|document)/)')),
)


def sensitive_findings(text, label):
    """Return labels and locations, never the matched sensitive value."""
    findings = []
    for kind, pattern in RULES:
        for match in pattern.finditer(text):
            line = text.count('\n', 0, match.start()) + 1
            findings.append(f'{label}:{line}: {kind}')
    return findings


def package_files(root):
    return [p for p in root.rglob('*')
            if not any(part in {'.git', '__pycache__'} for part in p.relative_to(root).parts)
            and (p.is_file() or p.is_symlink())]


def check_links(root, paths):
    errors = []
    for path in paths:
        if path.suffix != '.md' or path.is_symlink():
            continue
        for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', path.read_text()):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                errors.append(f'{path.relative_to(root)}: unresolved or external local link')
    return errors


def scan_history(root):
    """Inspect historical blobs as well as the current tip, deduplicated by object ID."""
    result = subprocess.run(['git', '-C', str(root), 'rev-list', '--all'], capture_output=True)
    if result.returncode:
        raise ValueError('History validation requires a Git repository.')
    seen = set()
    errors = []
    for commit in result.stdout.decode().splitlines():
        tree = subprocess.check_output(['git', '-C', str(root), 'ls-tree', '-rz', commit])
        for entry in tree.split(b'\0'):
            if not entry:
                continue
            metadata, raw_path = entry.split(b'\t', 1)
            mode, kind, object_id = metadata.decode().split()
            path = raw_path.decode('utf-8', errors='replace')
            if mode == '120000':
                errors.append(f'history {commit[:12]}:{path}: symlink is outside the publication contract')
                continue
            if kind != 'blob' or object_id in seen:
                continue
            seen.add(object_id)
            data = subprocess.check_output(['git', '-C', str(root), 'cat-file', 'blob', object_id])
            try:
                text = data.decode('utf-8')
            except UnicodeDecodeError:
                errors.append(f'history {commit[:12]}:{path}: non-text artifact requires removal before publication')
                continue
            errors.extend(sensitive_findings(text, f'history {commit[:12]}:{path}'))
    return errors


def check_meeting_plugin(root):
    """Keep the packaged meeting entrypoint and required app resolvable."""
    try:
        manifest = json.loads((root / '.codex-plugin/plugin.json').read_text())
        if (manifest['name'] != 'intgral-meeting'
                or manifest['skills'] != './skills/' or manifest['apps'] != './.app.json'):
            return ['meeting plugin: invalid entrypoints']
        apps = json.loads((root / '.app.json').read_text())['apps']
        wispr = apps['app-6a5ae9736be0819199d06d61ac171080']
        if (wispr['id'] != 'asdk_app_6a5ae9736be0819199d06d61ac171080'
                or wispr['required'] is not True):
            return ['meeting plugin: Wispr Flow must be the required app']
        skill = root / 'skills/intgral-meeting/SKILL.md'
        match = re.match(r'\A---\n(.*?)\n---\n', skill.read_text(), re.DOTALL)
        fields = dict(line.split(':', 1) for line in match[1].splitlines() if ':' in line) if match else {}
        if fields.get('name', '').strip() != 'intgral-meeting' or not fields.get('description', '').strip():
            return ['meeting skill: invalid name or description']
    except (OSError, ValueError, KeyError, TypeError):
        return ['meeting plugin: missing or invalid manifest, app dependency or skill']
    return []


def validate(root):
    errors = []
    paths = package_files(root)
    found = {p.relative_to(root).as_posix() for p in paths}
    errors.extend(f'{p}: missing required public file' for p in sorted(PUBLIC_FILES - found))
    errors.extend(f'{p}: file is outside the publication allowlist' for p in sorted(found - PUBLIC_FILES))
    for path in paths:
        label = path.relative_to(root).as_posix()
        if path.is_symlink():
            errors.append(f'{label}: symlink is outside the publication contract')
            continue
        if path.stat().st_size > 512 * 1024:
            errors.append(f'{label}: file is too large for this text-only public package')
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            errors.append(f'{label}: non-text content is outside the publication contract')
            continue
        errors.extend(sensitive_findings(text, label))
    if (root / 'SKILL.md').exists():
        match = re.match(r'\A---\n(.*?)\n---\n', (root / 'SKILL.md').read_text(), re.DOTALL)
        if not match:
            errors.append('SKILL.md: missing frontmatter')
        else:
            fields = dict(line.split(':', 1) for line in match[1].splitlines() if ':' in line)
            if fields.get('name', '').strip() != 'intgral-guide-skill' or not fields.get('description', '').strip():
                errors.append('SKILL.md: invalid name or description')
    if (root / 'assets/team-context.example.json').exists():
        try:
            example = json.loads((root / 'assets/team-context.example.json').read_text())
            if (example['status'] != 'example_only' or example['workspace_root'] is not None or example['current_goal'] is not None
                    or any(example['role_assignments'].values())
                    or example['approval_rules_source'] is not None or example['verified_at'] is not None
                    or any(value for key, value in example['sources'].items() if key != 'documentation_home')
                    or example['sources']['documentation_home'] != 'https://docs.intgral.ai'):
                errors.append('team-context example must contain no real team assignments or internal sources')
        except (ValueError, KeyError, TypeError):
            errors.append('team-context example has an invalid schema')
    errors.extend(check_links(root, paths))
    errors.extend(check_meeting_plugin(root))
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--history', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    errors = validate(root)
    if args.history:
        errors.extend(scan_history(root))
    if errors:
        print('\n'.join(errors))
        raise SystemExit(1)
    print(f'Validated {len(PUBLIC_FILES)} public files' + (' and Git history.' if args.history else '.'))


if __name__ == '__main__':
    main()
