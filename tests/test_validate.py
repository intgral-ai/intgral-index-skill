import importlib.util
import json
import subprocess
import tempfile
import unittest
import shutil
from pathlib import Path

spec = importlib.util.spec_from_file_location('publication_guard', Path(__file__).resolve().parents[1] / 'scripts/validate.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class PublicationGuardTests(unittest.TestCase):
    def test_meeting_package_resolves_required_wispr_app(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(guard.check_meeting_plugin(root), [])

    def test_meeting_package_rejects_missing_or_optional_dependency(self):
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(source / '.codex-plugin', root / '.codex-plugin')
            shutil.copytree(source / 'skills', root / 'skills')
            self.assertTrue(guard.check_meeting_plugin(root))
            dependency = {'apps': {'app-6a5ae9736be0819199d06d61ac171080': {
                'id': 'asdk_app_6a5ae9736be0819199d06d61ac171080', 'required': False}}}
            (root / '.app.json').write_text(json.dumps(dependency))
            self.assertTrue(guard.check_meeting_plugin(root))

    def test_detects_token_without_echoing_it(self):
        token = 'ghp_' + 'a' * 36
        findings = guard.sensitive_findings('token=' + token, 'sample')
        self.assertTrue(findings)
        self.assertNotIn(token, '\n'.join(findings))

    def test_personal_path_and_email_are_rejected(self):
        path = '/' + 'Users' + '/example/private-file'
        email = 'person' + '@' + 'example.invalid'
        self.assertEqual(len(guard.sensitive_findings(path + '\n' + email, 'sample')), 2)

    def test_private_platform_links_are_rejected(self):
        urls = [
            'https://docs.intgral.ai/' + 'doc/' + 'synthetic-page',
            'https://www.figma.com/' + 'design/' + 'synthetic-file',
            'https://drive.google.com/' + 'file/d/' + 'synthetic-file',
            'https://app.slack.com/' + 'client/' + 'synthetic-workspace',
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertTrue(guard.sensitive_findings(url, 'sample'))

    def test_public_documentation_home_is_allowed(self):
        self.assertEqual(guard.sensitive_findings('https://docs.intgral.ai', 'sample'), [])

    def test_private_configuration_cannot_join_package(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'team-context.json').write_text('{}')
            self.assertTrue(any('outside the publication allowlist' in e for e in guard.validate(root)))

    def test_symlink_cannot_import_external_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'README.md').symlink_to(root.parent / 'external-private-data')
            self.assertTrue(any('symlink' in e for e in guard.validate(root)))

    def test_local_links_cannot_escape_package(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / 'README.md'
            document.write_text('[outside](../outside.md)')
            self.assertTrue(guard.check_links(root, [document]))

    def test_removed_credential_is_still_detected_in_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True)
            git('init', '-b', 'main')
            git('config', 'user.name', 'Example Contributor')
            git('config', 'user.email', 'example' + '@' + 'users.noreply.github.com')
            document = root / 'README.md'
            document.write_text('ghp_' + 'b' * 36)
            git('add', 'README.md')
            git('commit', '-m', 'Synthetic unsafe version')
            document.write_text('Public guidance only.')
            git('add', 'README.md')
            git('commit', '-m', 'Synthetic clean tip')
            self.assertEqual(guard.sensitive_findings(document.read_text(), 'current'), [])
            self.assertTrue(guard.scan_history(root))


if __name__ == '__main__':
    unittest.main()
