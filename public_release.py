#!/usr/bin/env python3
"""Validate a candidate, publish APK/sources, then move the public update feed."""
import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import zipfile
from pathlib import Path

SIGNER = 'c5c30a7b708268862044f96e82e4f5604d78a86fac7591524862efea4ffa41e7'
REPO = 'RastyDima/cupergram-updates'


def run(*command, **kwargs):
    return subprocess.check_output(command, text=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('stage', choices=['verify', 'publish']); args = parser.parse_args()
    root = Path.cwd(); payload = root / 'payload'; meta = json.loads((payload / 'update.json').read_text())
    apk = payload / 'Cupergram-12.10.6.apk'
    if not apk.exists():
        parts = sorted((payload / 'apk-parts').glob('part-*'))
        if not parts: raise SystemExit('Candidate APK missing.')
        with apk.open('wb') as output:
            import shutil
            for part in parts:
                with part.open('rb') as source: shutil.copyfileobj(source, output)
    if not 10000 <= apk.stat().st_size <= 200*1024*1024: raise SystemExit('Unexpected APK size.')
    digest = hashlib.sha256(apk.read_bytes()).hexdigest()
    if apk.stat().st_size != meta['size'] or digest != meta['sha256']:
        raise SystemExit('Candidate bytes do not match metadata.')
    sdk = Path(os.environ['ANDROID_HOME']); aapt = sdk / 'build-tools/36.0.0/aapt'
    signing = run(str(aapt.parent / 'apksigner'), 'verify', '--verbose', '--print-certs', str(apk))
    certificates = re.findall(r'certificate SHA-256 digest: ([0-9a-fA-F]+)', signing)
    print('APK signer certificate digests:', certificates)
    if not certificates or {value.lower() for value in certificates} != {SIGNER}:
        raise SystemExit('Candidate APK has a different signing identity.')
    badging = run(str(aapt), 'dump', 'badging', str(apk))
    package = re.search(r"package: name='([^']+)' versionCode='(\d+)' versionName='([^']*)'", badging)
    if not package or package.group(1) != meta['packageName'] or int(package.group(2)) != meta['versionCode']:
        raise SystemExit('Candidate package/version do not match metadata.')
    tag = f"cupergram-{meta['buildRun']}"
    if meta['apkUrl'] != f'https://github.com/{REPO}/releases/download/{tag}/{apk.name}':
        raise SystemExit('Unexpected APK URL.')
    if args.stage == 'verify':
        with zipfile.ZipFile(payload / 'build-kit.zip') as source:
            for info in source.infolist():
                if info.filename.startswith('/') or '..' in Path(info.filename).parts or info.file_size > 10*1024*1024:
                    raise SystemExit('Unsafe source-kit entry.')
            source.extractall(root / 'kit')
        print('APK hash, signer and package match the checked candidate.')
        return
    checksum = payload / (apk.name+'.sha256'); checksum.write_text(digest+'  '+apk.name+'\n')
    notes = payload / 'notes.md'; notes.write_text(meta['notes']+'\n\nAPK · '+str(meta['versionCode'])+'\n\nAndroid check: https://github.com/RastyDima/cupergram/actions/runs/'+str(meta['androidRun'])+' (attempt '+str(meta['androidAttempt'])+')\n\nAPK, SHA256 and corresponding sources (GPL v2 or later) are attached.\n')
    found = subprocess.run(['gh', 'release', 'view', tag, '--repo', REPO], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
    if not found:
        run('gh', 'release', 'create', tag, str(apk), str(checksum), str(root / 'Cupergram-source.zip'), '--repo', REPO, '--target', 'main', '--title', 'Cupergram '+meta['versionName']+' · '+str(meta['versionCode']), '--notes-file', str(notes), '--draft')
    else:
        run('gh', 'release', 'upload', tag, str(apk), str(checksum), str(root / 'Cupergram-source.zip'), '--repo', REPO, '--clobber')
    run('gh', 'release', 'edit', tag, '--repo', REPO, '--draft=false')
    # Never downgrade the feed if an older queued publication finishes later.
    previous = json.loads(run('gh', 'api', f'repos/{REPO}/contents/update.json?ref=main'))
    old = json.loads(base64.b64decode(previous['content']))
    if old['versionCode'] > meta['versionCode']:
        print('A newer public APK exists; leaving its feed unchanged.'); return
    request = dict(message='Offer checked APK '+str(meta['versionCode']), branch='main', sha=previous['sha'], content=base64.b64encode((json.dumps(meta, ensure_ascii=False, indent=2)+'\n').encode()).decode())
    input_file = payload / 'feed-request.json'; input_file.write_text(json.dumps(request))
    run('gh', 'api', f'repos/{REPO}/contents/update.json', '--method', 'PUT', '--input', str(input_file))
    print('Public update feed now offers', meta['versionCode'])


if __name__ == '__main__':
    main()
